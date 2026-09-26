import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.user_and_gift import create_random_gift


def test_create_gift(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Test Gift", "approximate_price": 10.0}
    response = client.post(
        f"{settings.API_V1_STR}/gifts/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["approximate_price"] == data["approximate_price"]
    assert "id" in content
    assert "owner_id" in content


def test_read_gift(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    response = client.get(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == gift.name
    assert content["approximate_price"] == gift.approximate_price
    assert content["id"] == str(gift.id)
    assert content["owner_id"] == str(gift.owner_id)


def test_read_gift_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/gifts/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Gift not found"


def test_read_gift_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    response = client.get(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_gifts(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_gift(db)
    create_random_gift(db)
    response = client.get(
        f"{settings.API_V1_STR}/gifts/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_gift(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    data = {"name": "Updated name", "approximate_price": 20.0}
    response = client.put(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["approximate_price"] == data["approximate_price"]
    assert content["id"] == str(gift.id)
    assert content["owner_id"] == str(gift.owner_id)


def test_update_gift_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated name", "approximate_price": 20.0}
    response = client.put(
        f"{settings.API_V1_STR}/gifts/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Gift not found"


def test_update_gift_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    data = {"name": "Updated name", "approximate_price": 20.0}
    response = client.put(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_gift(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    response = client.delete(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Gift deleted successfully"


def test_delete_gift_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/gifts/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Gift not found"


def test_delete_gift_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    response = client.delete(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_upload_gift_image(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    response = client.post(
        f"{settings.API_V1_STR}/gifts/image",
        headers=superuser_token_headers,
        files={"file": ("photo.png", png, "image/png")},
    )
    assert response.status_code == 200
    photo_url = response.json()["photo_url"]
    assert photo_url.startswith("/static/gifts/")
    assert photo_url.endswith(".png")


def test_upload_gift_image_rejects_non_image(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/gifts/image",
        headers=superuser_token_headers,
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid file type. Only images are allowed."


def test_claim_gift(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    assert gift.reserved_by_id is None
    response = client.post(
        f"{settings.API_V1_STR}/gifts/{gift.id}/claim",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(gift.id)
    assert content["is_reserved"] is True
    assert "reserved_by_id" not in content


def test_claim_gift_twice_conflicts(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    gift = create_random_gift(db)
    first = client.post(
        f"{settings.API_V1_STR}/gifts/{gift.id}/claim",
        headers=normal_user_token_headers,
    )
    assert first.status_code == 200

    second = client.post(
        f"{settings.API_V1_STR}/gifts/{gift.id}/claim",
        headers=superuser_token_headers,
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "Gift is already reserved"


def test_claim_gift_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/gifts/{uuid.uuid4()}/claim",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Gift not found"


def test_claim_own_gift_is_rejected(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    created = client.post(
        f"{settings.API_V1_STR}/gifts/",
        headers=superuser_token_headers,
        json={"name": "My own gift", "approximate_price": 5.0},
    )
    assert created.status_code == 200

    response = client.post(
        f"{settings.API_V1_STR}/gifts/{created.json()['id']}/claim",
        headers=superuser_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot reserve your own gift"


def test_claim_gift_requires_authentication(client: TestClient, db: Session) -> None:
    gift = create_random_gift(db)
    response = client.post(f"{settings.API_V1_STR}/gifts/{gift.id}/claim")
    assert response.status_code == 401


def test_read_public_gifts_without_authentication(
    client: TestClient, db: Session
) -> None:
    gift = create_random_gift(db)
    response = client.get(f"{settings.API_V1_STR}/gifts/public/{gift.owner_id}")
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert str(gift.id) in [item["id"] for item in content["data"]]

    # The shared view must expose only whether a gift is taken, never by whom.
    for item in content["data"]:
        assert "is_reserved" in item
        assert "reserved_by_id" not in item


def test_read_public_gifts_unknown_user(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/gifts/public/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_public_gifts_reflects_reserved_state(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    gift = create_random_gift(db)
    claimed = client.post(
        f"{settings.API_V1_STR}/gifts/{gift.id}/claim",
        headers=normal_user_token_headers,
    )
    assert claimed.status_code == 200

    response = client.get(f"{settings.API_V1_STR}/gifts/public/{gift.owner_id}")
    assert response.status_code == 200
    item = next(g for g in response.json()["data"] if g["id"] == str(gift.id))
    assert item["is_reserved"] is True
