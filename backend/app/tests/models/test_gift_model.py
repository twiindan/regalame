# ABOUTME: Test file for the Gift model.
# ABOUTME: Ensures the Gift model is correctly defined and has the expected fields and relationships.

from sqlmodel import Session, SQLModel, create_engine

from app.models import Gift, User

# Define a test database URL
sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def test_create_gift():
    create_db_and_tables()
    with Session(engine) as session:
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password="hashedpassword",
            full_name="Test User"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create a gift
        gift_name = "Test Gift"
        approx_price = 25.50
        description = "A wonderful test gift."
        product_link = "http://example.com/gift"
        photo_url = "/static/images/gifts/test_gift.jpg"

        gift = Gift(
            name=gift_name,
                            price=approx_price,            description=description,
            product_link=product_link,
            photo_url=photo_url,
            owner_id=user.id
        )
        session.add(gift)
        session.commit()
        session.refresh(gift)

        assert gift.id is not None
        assert gift.name == gift_name
        assert gift.price == approx_price
        assert gift.description == description
        assert gift.product_link == product_link
        assert gift.photo_url == photo_url
        assert gift.owner_id == user.id
        assert gift.owner.id == user.id

        # Test optional fields
        gift_no_optional = Gift(
            name="Simple Gift",
                            price=10.00,            owner_id=user.id
        )
        session.add(gift_no_optional)
        session.commit()
        session.refresh(gift_no_optional)

        assert gift_no_optional.id is not None
        assert gift_no_optional.name == "Simple Gift"
        assert gift_no_optional.price == 10.00
        assert gift_no_optional.description is None
        assert gift_no_optional.product_link is None
        assert gift_no_optional.photo_url is None
        assert gift_no_optional.owner_id == user.id
        assert gift_no_optional.owner.id == user.id
