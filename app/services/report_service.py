from sqlalchemy import func, desc, cast, Date
from datetime import datetime, timedelta, timezone
from flask import current_app

from app.core.extensions import db
from app.models import Classification, Tag, classification_tags

class ReportService:
    def get_weekly_summary_data(self) -> dict:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        category_counts = self._query_category_counts(one_week_ago)
        top_tags = self._query_top_tags(one_week_ago)
        comments_over_time = self._query_comments_over_time(one_week_ago)
        avg_confidence = self._query_avg_confidence(one_week_ago)
        top_tags_by_cat = self._query_top_tags_by_category(one_week_ago)

        report_data = {
            "categories_chart": {
                "labels": [row.category for row in category_counts],
                "data": [row.total for row in category_counts],
            },
            "top_tags_chart": {
                "labels": [row.name for row in top_tags],
                "data": [row.total for row in top_tags],
            },
            "over_time_chart": {
                "labels": [
                    (
                        datetime.strptime(row.date, '%Y-%m-%d').strftime('%d/%m')
                        if isinstance(row.date, str)
                        else row.date.strftime('%d/%m')
                    )
                    for row in comments_over_time
                ],
                "data": [row.total for row in comments_over_time],
            },
            "avg_confidence_chart": {
                "labels": [row.category for row in avg_confidence],
                "data": [round(row.average_confidence * 100, 2) for row in avg_confidence],
            },
            "tags_by_category_chart": {
                "data": self._format_tags_by_category_data(top_tags_by_cat)
            }
        }
        
        return report_data

    def _query_category_counts(self, since: datetime):
        return db.session.query(
            Classification.category, func.count(Classification.id).label('total')
        ).filter(Classification.created_at >= since).group_by(Classification.category).order_by(desc('total')).all()

    def _query_top_tags(self, since: datetime):
        return db.session.query(
            Tag.name, func.count(Tag.id).label('total')
        ).select_from(Classification).join(
            classification_tags, Classification.id == classification_tags.c.classification_id
        ).join(Tag, Tag.id == classification_tags.c.tag_id).filter(
            Classification.created_at >= since
        ).group_by(Tag.name).order_by(desc('total')).limit(10).all()

    def _query_comments_over_time(self, since: datetime):
        date_function = func.date(Classification.created_at) if current_app.config["TESTING"] else cast(Classification.created_at, Date)
        return db.session.query(
            date_function.label('date'), func.count(Classification.id).label('total')
        ).filter(Classification.created_at >= since).group_by('date').order_by('date').all()

    def _query_avg_confidence(self, since: datetime):
        return db.session.query(
            Classification.category, func.avg(Classification.confidence).label('average_confidence')
        ).filter(Classification.created_at >= since).group_by(Classification.category).order_by(desc('average_confidence')).all()
    
    def _query_top_tags_by_category(self, since: datetime):
        subquery = db.session.query(
            Classification.category,
            Tag.name.label('tag_name'),
            func.count(Tag.id).label('tag_count'),
            func.row_number().over(
                partition_by=Classification.category,
                order_by=func.count(Tag.id).desc()
            ).label('rank')
        ).join(classification_tags, Classification.id == classification_tags.c.classification_id).join(
            Tag, Tag.id == classification_tags.c.tag_id
        ).filter(Classification.created_at >= since).group_by(Classification.category, Tag.name).subquery()
        
        return db.session.query(
            subquery.c.category, subquery.c.tag_name, subquery.c.tag_count
        ).filter(subquery.c.rank <= 3).order_by(subquery.c.category, subquery.c.rank).all()


    def _format_tags_by_category_data(self, data):
        if not data:
            return {"labels": [], "datasets": []}
        labels = sorted(list(set(row.tag_name for row in data)))
        datasets_data = {}
        for row in data:
            if row.category not in datasets_data:
                datasets_data[row.category] = {label: 0 for label in labels}
            datasets_data[row.category][row.tag_name] = row.tag_count
        colors = {'ELOGIO': '#2ecc71', 'CRÍTICA': '#e74c3c', 'SUGESTÃO': '#3498db', 'DÚVIDA': '#f1c40f', 'SPAM': '#95a5a6'}
        datasets = []
        for category, tags in datasets_data.items():
            datasets.append({
                "label": category,
                "data": [tags[label] for label in labels],
                "backgroundColor": colors.get(category, '#7f8c8d')
            })
        return {"labels": labels, "datasets": datasets}

report_service = ReportService()