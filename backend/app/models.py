import uuid
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    gifts: list["Gift"] = Relationship(
        back_populates="owner",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[Gift.owner_id]"},
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: Mapped["User"] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Shared properties
class GiftBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    approximate_price: float | None = Field(default=None, ge=0)
    photo_url: str | None = Field(default=None, max_length=255)
    product_link: str | None = Field(default=None, max_length=255)


# Properties to receive on gift creation
class GiftCreate(GiftBase):
    pass


# Properties to receive on gift update
# Reservation is deliberately not updatable here: claiming a gift goes through
# a dedicated endpoint that guarantees exclusivity in the database.
class GiftUpdate(GiftBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Gift(GiftBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    reserved_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True
    )
    owner: Mapped["User"] = Relationship(
        back_populates="gifts",
        sa_relationship_kwargs={"foreign_keys": "[Gift.owner_id]"},
    )
    reserved_by: Mapped[Optional["User"]] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Gift.reserved_by_id]"},
    )

    @property
    def is_reserved(self) -> bool:
        return self.reserved_by_id is not None


# Properties to return via API, id is always required
class GiftPublic(GiftBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    # Deliberately a boolean and not reserved_by_id: the shared public list must
    # not reveal which user claimed a gift.
    is_reserved: bool


class GiftsPublic(SQLModel):
    data: list[GiftPublic]
    count: int


# Response returned after storing an uploaded gift image
class GiftImageUpload(SQLModel):
    photo_url: str


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
