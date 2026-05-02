async def test_remove_item(client):
    add_resp = await client.post("/items", json={"product_id": 1, "quantity": 2})
    item_id = add_resp.json()["id"]

    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 200

    cart = await client.get("/")
    assert len(cart.json()["items"]) == 0


async def test_remove_nonexistent_item(client):
    await client.get("/")
    response = await client.delete("/items/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
