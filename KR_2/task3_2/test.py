from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_existing_product():
    response = client.get("/product/123")
    assert response.status_code == 200
    assert response.json() == {
        "product_id": 123,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 599.99,
    }


def test_get_another_product():
    response = client.get("/product/101")
    assert response.status_code == 200
    assert response.json()["name"] == "Headphones"


def test_get_nonexistent_product():
    response = client.get("/product/9999")
    assert response.status_code == 200
    assert "error" in response.json()


def test_get_product_invalid_id():
    """Строка вместо int, следовательно 422"""
    response = client.get("/product/abc")
    assert response.status_code == 422


def test_search_by_keyword():
    response = client.get("/products/search?keyword=phone")
    assert response.status_code == 200
    results = response.json()
    names = [p["name"] for p in results]
    assert "Smartphone" in names
    assert "Phone Case" in names


def test_search_with_category():
    response = client.get("/products/search?keyword=phone&category=Electronics")
    assert response.status_code == 200
    results = response.json()
    # Phone Case (Accessories) не должен попасть
    assert all(p["category"] == "Electronics" for p in results)


def test_search_with_limit():
    response = client.get("/products/search?keyword=s&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_search_no_results():
    response = client.get("/products/search?keyword=zzznoresult")
    assert response.status_code == 200
    assert response.json() == []


def test_search_missing_keyword():
    """keyword обязателен, тогда 422"""
    response = client.get("/products/search")
    assert response.status_code == 422


def test_search_case_insensitive():
    """Поиск без учёта регистра"""
    response = client.get("/products/search?keyword=PHONE")
    assert response.status_code == 200
    assert len(response.json()) > 0