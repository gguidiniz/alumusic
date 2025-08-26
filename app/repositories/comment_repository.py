from app.core.extensions import db
from app.models.comment import Comment, Classification, Tag
from app.schemas.comment_schema import CommentSchema, ClassificationResultSchema

class CommentRepository:
    def save_comment_classification(
        self,
        comment_data: CommentSchema,
        classification_result: ClassificationResultSchema
    ) -> Comment:
        
        comment = db.session.query(Comment).filter_by(external_id=str(comment_data.id)).first()
        if not comment:
            comment = Comment(
                external_id=str(comment_data.id),
                text=comment_data.text
            )
            db.session.add(comment)

        tags_to_associate = []
        for tag_data in classification_result.tags:
            tag = db.session.query(Tag).filter_by(name=tag_data.tag).first()
            if not tag:
                tag = Tag(name=tag_data.tag, explanation=tag_data.explanation)
                db.session.add(tag)
            tags_to_associate.append(tag)

        new_classification = Classification(
            category=classification_result.category,
            confidence=classification_result.confidence,
            tags=tags_to_associate,
            comment=comment
        )

        db.session.add(new_classification)

        return comment
    
comment_repository = CommentRepository()