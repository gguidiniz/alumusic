from sqlalchemy import func, desc, Date, cast
from datetime import datetime, timedelta, timezone

from app.core.extensions import db
from app.models.comment import Classification, Tag, classification_tags

class ReportService:
    def format_tags_by_category(self, data):
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
    
    def get_weekly_summary_data(self) -> dict:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        category_counts_query = (
            db.session.query(
                Classification.category,
                func.count(Classification.id).label('total')
            )
            .filter(Classification.created_at >= one_week_ago)
            .group_by(Classification.category)
            .order_by(desc('total'))
        )
        category_counts = category_counts_query.all()

        top_tags_query = (
            db.session.query(
                Tag.name,
                func.count(classification_tags.c.tag_id).label('total')
            )
            .join(classification_tags, Tag.id == classification_tags.c.tag_id)
            .join(Classification, Classification.id == classification_tags.c.classification_id)
            .filter(Classification.created_at >= one_week_ago)
            .group_by(Tag.name)
            .order_by(desc('total'))
            .limit(10)
        )
        top_tags = top_tags_query.all()

        comments_over_time_query = (
            db.session.query(
                cast(Classification.created_at, Date).label('date'),
                func.count(Classification.id).label('total')
            )
            .filter(Classification.created_at >= one_week_ago)
            .group_by('date')
            .order_by('date')
        )
        comments_over_time = comments_over_time_query.all()

        avg_confidence_query = (
            db.session.query(
                Classification.category,
                func.avg(Classification.confidence).label('average_confidence')
            )
            .filter(Classification.created_at >= one_week_ago)
            .group_by(Classification.category)
            .order_by(desc('average_confidence'))
        )
        avg_confidence_by_category = avg_confidence_query.all()

        subquery = (
            db.session.query(
                Classification.category,
                Tag.name.label('tag_name'),
                func.count(Tag.id).label('tag_count'),
                func.row_number().over(
                    partition_by=Classification.category,
                    order_by=func.count(Tag.id).desc()
                ).label('rank')
            )
            .join(classification_tags, Classification.id == classification_tags.c.classification_id)
            .join(Tag, Tag.id == classification_tags.c.tag_id)
            .filter(Classification.created_at >= one_week_ago)
            .group_by(Classification.category, Tag.name)
        ).subquery()

        top_tags_by_category_query = (
            db.session.query(subquery.c.category, subquery.c.tag_name, subquery.c.tag_count)
            .filter(subquery.c.rank <= 3)
            .order_by(subquery.c.category, subquery.c.rank)
        )
        top_tags_by_category = top_tags_by_category_query.all()

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
                "labels": [row.date.strftime('%d/%m') for row in comments_over_time],
                "data": [row.total for row in comments_over_time],
            },
            "avg_confidence_chart": {
                "labels": [row.category for row in avg_confidence_by_category],
                "data": [round(row.average_confidence * 100, 2) for row in avg_confidence_by_category]
            },
            "tags_by_category_chart": {
                "data": self.format_tags_by_category(top_tags_by_category)
            }
        }

        return report_data
    
report_service = ReportService()