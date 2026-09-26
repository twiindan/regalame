# ABOUTME: Unit tests for gift CRUD operations.
# ABOUTME: Verifies the functionality of creating, reading, updating, and deleting gifts.

import uuid

from sqlmodel import Session

from app import crud
from app.models import GiftCreate, GiftUpdate
from app.tests.utils.user_and_gift import create_random_gift, create_random_user


def test_create_gift(db: Session) -> None:
    user = create_random_user(db)
    gift_in = GiftCreate(name="Test Gift", price=10.0)
    gift = crud.create_gift(session=db, gift_in=gift_in, owner_id=user.id)
    assert gift.name == "Test Gift"
    assert gift.price == 10.0
    assert gift.owner_id == user.id
    assert gift.id is not None


def test_get_gift_by_id(db: Session) -> None:
    gift = create_random_gift(db)
    fetched_gift = crud.get_gift_by_id(session=db, gift_id=gift.id)
    assert fetched_gift
    assert fetched_gift.id == gift.id
    assert fetched_gift.name == gift.name


def test_get_gifts_by_owner(db: Session) -> None:
    user = create_random_user(db)
    gift1 = create_random_gift(db, owner_id=user.id)
    gift2 = create_random_gift(db, owner_id=user.id)
    gifts = crud.get_gifts_by_owner(session=db, owner_id=user.id)
    assert len(gifts) == 2
    assert gift1 in gifts
    assert gift2 in gifts


def test_update_gift(db: Session) -> None:
    gift = create_random_gift(db)
    new_name = "Updated Gift Name"
    gift_update = GiftUpdate(name=new_name)
    updated_gift = crud.update_gift(session=db, db_gift=gift, gift_in=gift_update)
    assert updated_gift.name == new_name
    assert updated_gift.id == gift.id


def test_delete_gift(db: Session) -> None:
    gift = create_random_gift(db)
    crud.delete_gift(session=db, db_gift=gift)
    deleted_gift = crud.get_gift_by_id(session=db, gift_id=gift.id)
    assert deleted_gift is None
