from fastapi.testclient import TestClient


def test_api(app):
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer valid_token"}

        response = client.get("/products")
        assert response.status_code == 401
        print("GET /products без токена: 401 OK")

        response = client.get(
            "/products",
            headers={"Authorization": "Bearer wrong_token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Неверный токен"
        print("GET /products с неправильным заголовком: 401 OK")

        response = client.get("/products", headers=headers)
        assert response.status_code == 200
        print("GET /products: OK")
        assert response.headers["cache-control"] == "max-age=3600"
        assert response.headers["content-type"].startswith("application/json")
        print("HTTP-заголовки: OK")

        response = client.get("/products?limit=5&offset=0", headers=headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "products" in data
        assert data["limit"] == 5
        assert data["offset"] == 0
        print("GET /products с пагинацией: OK")

        response = client.get("/products?limit=0", headers=headers)
        assert response.status_code == 422

        response = client.get("/products?limit=101", headers=headers)
        assert response.status_code == 422

        response = client.get("/products?offset=-1", headers=headers)
        assert response.status_code == 422
        print("Ограничение пагинации: OK")

        response = client.get("/products/999999")
        assert response.status_code == 404
        print("GET отсутствующего товара: OK")

        response = client.put(
            "/products/999999",
            json={
                "name": "Test",
                "price": "1000.00",
                "stock": 100,
            },
        )
        assert response.status_code == 404
        print("PUT отсутствующего товара: OK")

        response = client.delete("/products/999999")
        assert response.status_code == 404
        print("DELETE отсутствующего товара: OK")

        print("Все тесты выполнены")
