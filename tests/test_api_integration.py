import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_save_hero(async_client: AsyncClient, integration_override_dependencies):
    response = await async_client.post("/hero/", json={"name": "Superman"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Superman"
    assert data["intelligence"] == 94


@pytest.mark.asyncio
async def test_negative_save_hero(async_client: AsyncClient, integration_override_dependencies):
    response = await async_client.post("/hero/", json={"name": "Supermann"})
    data = response.json()

    assert response.status_code == 404
    assert data['detail'] == 'Герой не найден, возможно вы ввели неверное имя героя'


@pytest.mark.asyncio
async def test_get_heroes_by_params(async_client: AsyncClient, integration_override_dependencies):
    await async_client.post("/hero/", json={"name": "Batman"})
    await async_client.post("/hero/", json={"name": "Dart Vader"})
    await async_client.post("/hero/", json={"name": "Spider-man"})
    await async_client.post("/hero/", json={"name": "Iron man"})
    await async_client.post("/hero/", json={"name": "Thanos"})

    response = await async_client.get("/hero/", params={
        'strength': 40,
        'strength_operator': 'ge',
        'speed': 60,
        'speed_operator': 'le'
    }
                                      )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert list(map(lambda x: x['name'], data)) == ['Batman', 'Iron Man', 'Thanos']


@pytest.mark.asyncio
async def test_negative_get_heroes_by_params(async_client: AsyncClient, integration_override_dependencies):
    response = await async_client.get("/hero/", params={
        'combat': 100,
        'combat_operator': 'eq'
    }
                                      )
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Героев с такими параметрами нет в базе данных.'


@pytest.mark.asyncio
async def test_get_heroes_by_name(async_client: AsyncClient, integration_override_dependencies):
    response = await async_client.get("/hero/", params={
        'name': 'Superman'
    }
                                      )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert list(map(lambda x: x['name'], data)) == ['Superman']


@pytest.mark.asyncio
async def test_negative_get_heroes_by_name(async_client: AsyncClient, integration_override_dependencies):
    response = await async_client.get("/hero/", params={
        'name': 'Supermann'
    })
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Героев с такими параметрами нет в базе данных.'
