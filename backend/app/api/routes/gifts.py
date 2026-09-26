import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    Gift,
    GiftCreate,
    GiftImageUpload,
    GiftPublic,
    GiftsPublic,
    GiftUpdate,
    Message,
    User,
)
from app.utils import save_upload_file_to_static

router = APIRouter(prefix="/gifts", tags=["gifts"])


@router.get("/", response_model=GiftsPublic)
def read_gifts(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve gifts.

    Superusers see every gift; regular users only see their own.
    """
    if current_user.is_superuser:
        count = session.exec(select(func.count()).select_from(Gift)).one()
        gifts = crud.get_gifts(session=session, offset=skip, limit=limit)
    else:
        count = session.exec(
            select(func.count())
            .select_from(Gift)
            .where(Gift.owner_id == current_user.id)
        ).one()
        gifts = crud.get_gifts_by_owner(
            session=session, owner_id=current_user.id, offset=skip, limit=limit
        )

    return GiftsPublic(data=gifts, count=count)


@router.get("/public/{user_id}", response_model=GiftsPublic)
def read_public_gifts(
    session: SessionDep, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Public listing of another user's gifts, reachable from the shared link.

    No authentication on purpose: the product spec requires that visitors without
    an account can open a shared link and see the list.
    """
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    count = session.exec(
        select(func.count()).select_from(Gift).where(Gift.owner_id == user_id)
    ).one()
    gifts = crud.get_gifts_by_owner(
        session=session, owner_id=user_id, offset=skip, limit=limit
    )
    return GiftsPublic(data=gifts, count=count)


@router.post(
    "/image",
    response_model=GiftImageUpload,
    dependencies=[Depends(get_current_user)],
)
def upload_gift_image(*, file: UploadFile = File(...)) -> Any:
    """
    Store an uploaded gift image and return the URL to reference from a gift.

    Authentication is required even though no user data is read.
    """
    photo_url = save_upload_file_to_static(file, folder="gifts")
    return GiftImageUpload(photo_url=photo_url)


@router.get("/{id}", response_model=GiftPublic)
def read_gift(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get a gift by ID.
    """
    gift = session.get(Gift, id)
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if not current_user.is_superuser and (gift.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return gift


@router.post("/", response_model=GiftPublic)
def create_gift(
    *, session: SessionDep, current_user: CurrentUser, gift_in: GiftCreate
) -> Any:
    """
    Create a new gift owned by the current user.
    """
    return crud.create_gift(session=session, gift_in=gift_in, owner_id=current_user.id)


@router.put("/{id}", response_model=GiftPublic)
def update_gift(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    gift_in: GiftUpdate,
) -> Any:
    """
    Update a gift. Reservations are not updatable here.
    """
    gift = session.get(Gift, id)
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if not current_user.is_superuser and (gift.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.update_gift(session=session, db_gift=gift, gift_in=gift_in)


@router.post("/{id}/claim", response_model=GiftPublic)
def claim_gift(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Claim a gift ("Me lo quedo").

    Exclusivity is enforced by the database, not by this check: the UPDATE only
    matches a row whose reserved_by_id is still NULL, so exactly one concurrent
    caller can win and every other one gets 409.
    """
    gift = session.get(Gift, id)
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if gift.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot reserve your own gift")
    if not crud.claim_gift(session=session, gift_id=id, user_id=current_user.id):
        raise HTTPException(status_code=409, detail="Gift is already reserved")
    session.refresh(gift)
    return gift


@router.delete("/{id}")
def delete_gift(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a gift.
    """
    gift = session.get(Gift, id)
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if not current_user.is_superuser and (gift.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    crud.delete_gift(session=session, db_gift=gift)
    return Message(message="Gift deleted successfully")
