from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from app.api.deps import CurrentUser, get_db
from app.crud import create_gift
from app.models import Gift, GiftCreate, User
from app.utils import save_upload_file_to_static

router = APIRouter()


@router.post("/", response_model=Gift)
async def create_new_gift(
    name: Annotated[str, Form()],
    approximate_price: Annotated[float, Form()],
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    description: Annotated[str | None, Form()] = None,
    product_link: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile, File()] | None = None,
):
    photo_url = None
    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only images are allowed.",
            )
        photo_url = save_upload_file_to_static(file, folder="gifts")

    gift_in = GiftCreate(
        name=name,
        approximate_price=approximate_price,
        description=description,
        product_link=product_link,
        photo_url=photo_url,
    )
    gift = create_gift(session=db, gift_in=gift_in, owner_id=current_user.id)
    return gift