import logging
from typing import Dict, Any

from fastapi import FastAPI
from httpx import AsyncClient, HTTPStatusError

from src.config import get_api_access
from src.app.db.repository.repository import Repository
from src.app.pydantic_models.schemas import HeroSchema, FiltersSchema

from src.app.pydantic_models.schemas import HeroResponse


class Service:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.token = get_api_access()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    async def find_hero_by_name(json: dict, name: str):
        heroes = json.get("results")
        if heroes:
            for hero in heroes:
                if hero["name"].lower() == name.lower():
                    hero_schema = HeroSchema.model_validate(hero)
                    return hero_schema
            return ValueError("No results")
        else:
            return None


    async def save_hero(self, name: str) -> HeroResponse | Dict[str, Any]:
        url = f"https://superheroapi.com/api/{self.token}/search/{name}"
        async with AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
            except HTTPStatusError as e:
                self.logger.warning(f"Heroes-API error: {e.response.status_code}")
                raise e
        try:
            response_json = response.json()
            hero = await self.find_hero_by_name(response_json, name)
            res = await self.repository.add_hero(hero)
            return res
        except ValueError as e:
            self.logger.warning(str(e))
            raise e
        except AttributeError as e:
            self.logger.warning(str(e))
            raise e


    async def get_heroes(self, hero: FiltersSchema) -> list[HeroResponse]:
        try:
            res = await self.repository.get_hero(hero)
            return res
        except (ValueError, AttributeError, TypeError) as e:
            self.logger.warning(str(e))
            raise e
