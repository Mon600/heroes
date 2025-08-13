from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unit_save_hero(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.post("/hero/", json={"name": "Superman"})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Superman"
    assert data["strength"] == 100
    mock_service.save_hero.assert_called_once_with("Superman")


@pytest.mark.asyncio
async def test_unit_negative_save_hero(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.post("/hero/", json={"name": "Unknown"})

    assert response.status_code == 404
    data = response.json()
    assert "Герой не найден" in data["detail"]
    mock_service.save_hero.assert_called_once_with("Unknown")


@pytest.mark.asyncio
async def test_get_heroes_by_speed_ge(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.get("/hero/", params={
        "speed": 90,
        "speed_operator": "ge"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    print(data)
    assert {h["name"] for h in data} == {"Superman", "Flash"}


@pytest.mark.asyncio
async def test_get_heroes_by_intelligence_eq(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.get("/hero/", params={
        "intelligence": 100,
        "intelligence_operator": "eq"
    })
    assert response.status_code == 200
    data = response.json()
    assert {h["name"] for h in data} == {"Batman", "Iron Man"}


@pytest.mark.asyncio
async def test_get_heroes_by_combat_le(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.get("/hero/", params={
        "combat": 85,
        "combat_operator": "le"
    })
    assert response.status_code == 200
    data = response.json()
    assert {h["name"] for h in data} == {"Superman", "Flash", "Iron Man"}


@pytest.mark.asyncio
async def test_get_heroes_by_name_and_power(
        async_client: AsyncClient,
        unit_test_override,
        mock_service: AsyncMock
):
    response = await async_client.get("/hero/", params={
        "name": "Flash",
        "power": 90,
        "power_operator": "ge"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Flash"
