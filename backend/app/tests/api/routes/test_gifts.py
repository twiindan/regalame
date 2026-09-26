import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.user_and_gift import create_random_gift


def test_create_gift(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Test Gift", "price": 10.0}
    response = client.post(
        f"{settings.API_V1_STR}/gifts/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["price"] == data["price"]
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
    assert content["price"] == gift.price
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
    data = {"name": "Updated name", "price": 20.0}
    response = client.put(
        f"{settings.API_V1_STR}/gifts/{gift.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["price"] == data["price"]
    assert content["id"] == str(gift.id)
    assert content["owner_id"] == str(gift.owner_id)


def test_update_gift_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated name", "price": 20.0}
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
    data = {"name": "Updated name", "price": 20.0}
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
