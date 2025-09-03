from app.core.extensions import db
import datetime
from datetime import timezone

class WeeklySummary(db.Model):
    __tablename__ = 'weekly_summaries'

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    def __repr__(self):
        return f'<WeeklySummary for {self.start_date} to {self.end_date}>'