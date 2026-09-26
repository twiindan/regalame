import uuid
from typing import Any, cast

from sqlalchemy import CursorResult, update
from sqlmodel import Session, col, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Gift,
    GiftCreate,
    GiftUpdate,
    Item,
    ItemCreate,
    ItemUpdate,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item(*, session: Session, item_id: uuid.UUID) -> Item | None:
    statement = select(Item).where(Item.id == item_id)
    return session.exec(statement).first()


def get_items(*, session: Session, offset: int = 0, limit: int = 100) -> list[Item]:
    statement = select(Item).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def update_item(*, session: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    item_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, item_id: uuid.UUID) -> Item | None:
    item = session.get(Item, item_id)
    if not item:
        return None
    session.delete(item)
    session.commit()
    return item


def create_gift(*, session: Session, gift_in: GiftCreate, owner_id: uuid.UUID) -> Gift:
    db_gift = Gift.model_validate(gift_in, update={"owner_id": owner_id})
    session.add(db_gift)
    session.commit()
    session.refresh(db_gift)
    return db_gift


def get_gift_by_id(*, session: Session, gift_id: uuid.UUID) -> Gift | None:
    statement = select(Gift).where(Gift.id == gift_id)
    return session.exec(statement).first()


def get_gifts(*, session: Session, offset: int = 0, limit: int = 100) -> list[Gift]:
    statement = select(Gift).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def get_gifts_by_owner(
    *, session: Session, owner_id: uuid.UUID, offset: int = 0, limit: int = 100
) -> list[Gift]:
    statement = (
        select(Gift).where(Gift.owner_id == owner_id).offset(offset).limit(limit)
    )
    return list(session.exec(statement).all())


def update_gift(*, session: Session, db_gift: Gift, gift_in: GiftUpdate) -> Gift:
    gift_data = gift_in.model_dump(exclude_unset=True)
    db_gift.sqlmodel_update(gift_data)
    session.add(db_gift)
    session.commit()
    session.refresh(db_gift)
    return db_gift


def claim_gift(*, session: Session, gift_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Atomically reserve a gift for a user.

    Returns True when this caller won the race. The database is the arbiter, not
    the application: two concurrent callers both evaluate reserved_by_id IS NULL,
    but under READ COMMITTED the second UPDATE blocks on the first one's row
    lock, re-evaluates the predicate after that commit, matches no row and
    updates zero rows.
    """
    statement = (
        update(Gift)
        .where(col(Gift.id) == gift_id, col(Gift.reserved_by_id).is_(None))
        .values(reserved_by_id=user_id)
        .execution_options(synchronize_session=False)
    )
    result = cast("CursorResult[Any]", session.execute(statement))
    session.commit()
    return result.rowcount > 0


def delete_gift(*, session: Session, db_gift: Gift) -> None:
    session.delete(db_gift)
    session.commit()
