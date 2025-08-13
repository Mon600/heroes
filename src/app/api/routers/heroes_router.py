from fastapi import APIRouter, HTTPException
from httpx import HTTPStatusError

from src.app.dependencies.dependencies import ServiceDep

from src.app.pydantic_models.schemas import HeroResponse, FiltersDep, HeroCreate

router = APIRouter(prefix='/hero', tags=["Герои 🦹"])


@router.post("/", summary="Cохранить героя в базу данных🦹⬇️", )
async def save_hero(hero: HeroCreate, service: ServiceDep) -> HeroResponse:
    try:
        hero = await service.save_hero(hero.name)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=404,
            detail=f'Герой не найден, возможно вы ввели неверное имя героя')
    except HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail=f'Ошибка внешнего сервиса. Попробуйте позже.'
        )
    return hero


@router.get("/", summary="Получить героев из базы данных по заданным параметрами🦹⬆️")
async def get_hero(filters: FiltersDep, service: ServiceDep) -> list[HeroResponse]:
    try:
        heroes = await service.get_heroes(filters)
        if not heroes or heroes is None:
            raise HTTPException(status_code=404, detail='Героев с такими параметрами нет в базе данных.')
        return heroes
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f'Ошибка валидации данных, проверьте введенные данные еще раз')