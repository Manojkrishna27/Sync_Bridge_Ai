from datetime import datetime
import uuid
from app.core.extensions import db
from sqlalchemy.dialects.mysql import CHAR

def generate_uuid():
    return str(uuid.uuid4())

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(CHAR(36), primary_key=True, default=generate_uuid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
