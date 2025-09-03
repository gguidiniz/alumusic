from app.core.extensions import db
import datetime
from datetime import timezone

classification_tags = db.Table('classification_tags',
                               db.Column('classification_id', db.Integer, db.ForeignKey('classifications.id'), primary_key=True),
                               db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                               )

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    classifications = db.relationship('Classification', back_populates='comment', lazy=True)

    def __repr__(self):
        return f'<Comment {self.external_id}>'
    
class Classification(db.Model):
    __tablename__ = 'classifications'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    comment = db.relationship('Comment', back_populates='classifications')

    tags = db.relationship('Tag', secondary=classification_tags, back_populates='classifications', lazy=True)

    def __repr__(self):
        return f'<Classification {self.id} for Comment {self.comment_id}>'
    
class Tag(db.Model):
     __tablename__ = 'tags'

     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(100), unique=True, nullable=False)
     explanation = db.Column(db.Text, nullable=True)

     classifications = db.relationship('Classification', secondary=classification_tags, back_populates='tags', lazy=True)

     def __repr__(self):
         return f'<Tag {self.name}>'