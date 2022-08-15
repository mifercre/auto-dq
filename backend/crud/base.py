from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from db.base_class import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


ORDER_BY_MAP = {
    'ASC': asc,
    'DESC': desc
}


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Optional[Any] = None, **kwargs) -> Optional[ModelType]:
        if id:
            return db.query(self.model).filter(self.model.id == id).first()
        else:
            return db.query(self.model).filter(*self.get_filter_by_args(kwargs)).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, sort: list = None) -> List[ModelType]:
        order_by = None
        if sort and len(sort) == 2:
            order_by = ORDER_BY_MAP[sort[1]](getattr(self.model, sort[0]))

        return db.query(self.model).order_by(order_by).offset(skip).limit(limit).all()

    def get_filtered(self, db: Session, *, skip: int = 0, limit: int = 100, sort: list = None, **kwargs) -> List[ModelType]:
        order_by = None
        if sort and len(sort) == 2:
            order_by = ORDER_BY_MAP[sort[1]](getattr(self.model, sort[0]))

        return db.query(self.model).filter(*self.get_filter_by_args(kwargs)).order_by(order_by).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        # obj_data = jsonable_encoder(db_obj)
        obj_data = db_obj.json()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def truncate(self, db: Session):
        db.execute(f'TRUNCATE TABLE "{self.model.__tablename__}" CASCADE')
        db.commit()

    def count(self, db: Session, **kwargs) -> int:
        return db.query(self.model.id).filter(*self.get_filter_by_args(kwargs)).count()

    def get_filter_by_args(self, dic_args: dict):
        filters = []
        for key, value in dic_args.items():  # type: str, any
            if key.endswith('___gt'):
                key = key[:-5]
                filters.append(getattr(self.model, key) > value)
            elif key.endswith('___gte'):
                key = key[:-6]
                filters.append(getattr(self.model, key) >= value)
            elif key.endswith('___lt'):
                key = key[:-5]
                filters.append(getattr(self.model, key) < value)
            elif key.endswith('___lte'):
                key = key[:-6]
                filters.append(getattr(self.model, key) <= value)
            elif key.endswith('___like'):
                key = key[:-7]
                filters.append(getattr(self.model, key).like('%{}%'.format(value)))
            elif key.endswith('___ilike'):
                key = key[:-8]
                filters.append(getattr(self.model, key).ilike('%{}%'.format(value)))
            elif isinstance(value, list):
                filters.append(getattr(self.model, key).in_(value))
            else:
                filters.append(getattr(self.model, key) == value)
        return filters
