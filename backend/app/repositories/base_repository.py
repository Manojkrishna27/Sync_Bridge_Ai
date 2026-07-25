from app.core.extensions import db

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, id):
        return self.model.query.filter_by(id=id, deleted_at=None).first()

    def get_all(self):
        return self.model.query.filter_by(deleted_at=None).all()

    def create(self, entity_or_kwargs=None, **kwargs):
        if entity_or_kwargs is not None and hasattr(entity_or_kwargs, '__tablename__'):
            instance = entity_or_kwargs
        else:
            if isinstance(entity_or_kwargs, dict):
                kwargs.update(entity_or_kwargs)
            instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance):
        instance.soft_delete()
        return instance
