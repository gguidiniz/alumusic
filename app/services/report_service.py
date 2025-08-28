from sqlalchemy import func, desc, Date, cast
from datetime import datetime, timedelta, timezone

from app.core.extensions import db
from app.models.comment import Classification, Tag, classification_tags

class ReportService:
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
            }
        }

        return report_data
    
report_service = ReportService()