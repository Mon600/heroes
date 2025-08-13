from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.models import Hero
from src.app.pydantic_models.schemas import HeroSchema, FiltersSchema


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_hero(self, hero: HeroSchema):
        powerstats_dict = hero.powerstats.model_dump()
        stmt = (insert(Hero)
                .values(
                        name=hero.name,
                        **powerstats_dict
                        )
                .on_conflict_do_update(
                                        index_elements=['name'],
                                        set_=powerstats_dict)
                .returning(Hero)
                )
        hero = await self.session.execute(stmt)
        await self.session.commit()
        return hero.scalars().one()

    async def get_hero(self, filters: FiltersSchema):
        stmt = select(Hero)

        def add_filter(stmt, column, value: Optional[int], operator: str):
            if value is None:
                return stmt
            if operator == "eq":
                return stmt.where(column == value)
            elif operator == "ge":
                return stmt.where(column >= value)
            elif operator == "le":
                return stmt.where(column <= value)
            else:
                raise ValueError(f"Unknown operator: {operator}")

        if filters.name:
            stmt = stmt.where(Hero.name.ilike(filters.name))

        stmt = add_filter(stmt, Hero.intelligence, filters.intelligence, filters.intelligence_operator)
        stmt = add_filter(stmt, Hero.strength, filters.strength, filters.strength_operator)
        stmt = add_filter(stmt, Hero.speed, filters.speed, filters.speed_operator)
        stmt = add_filter(stmt, Hero.durability, filters.durability, filters.durability_operator)
        stmt = add_filter(stmt, Hero.power, filters.power, filters.power_operator)
        stmt = add_filter(stmt, Hero.combat, filters.combat, filters.combat_operator)

        result = await self.session.execute(stmt)
        return result.scalars().all()