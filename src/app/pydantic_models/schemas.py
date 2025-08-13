from typing import Annotated, Optional, Literal

from fastapi.params import Depends
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HeroCreate(BaseModel):
    name: str = Field(min_length=1,  max_length=128, description="Имя героя")


class PowerStatsSchema(BaseModel):
    intelligence: int = Field(
        default=0,
        le=100,
        ge=0,
        description='Интеллект'
    )
    strength: int = Field(
        default=0,
        le=100,
        ge=0,
        description="Сила"
    )
    speed: int = Field(
        default=0,
        le=100,
        ge=0,
        description="Cкорость"
    )
    durability: int = Field(
        default=0,
        le=100,
        ge=0,
        description="Прочность"
    )
    power: int = Field(
        default=0,
        le=100,
        ge=0,
        description="Мощь"
    )
    combat: int = Field(
        default=0,
        le=100,
        ge=0,
        description="Боевые навыки"
    )

    model_config = ConfigDict(from_attributes=True)


class HeroSchema(BaseModel):
    name: str = Field(max_length=128, description="Имя")
    powerstats: PowerStatsSchema

    @field_validator('name', mode='before')
    @classmethod
    def switch_register(cls, value) -> str:
        return value.lower()


class HeroResponse(PowerStatsSchema):
    name: str = Field(max_length=128, description="Имя")

    @field_validator('name', mode='before')
    @classmethod
    def switch_register(cls, value) -> str:
        return value.title()

    model_config = ConfigDict(from_attributes=True)


class FiltersSchema(BaseModel):
    name: Optional[str] = Field(default="", max_length=128, description="Имя")

    intelligence: Optional[int] = Field(None, description="Фильтр по интеллекту")
    strength: Optional[int] = Field(None, description="Фильтр по силе")
    speed: Optional[int] = Field(None, description="Фильтр по скорости")
    durability: Optional[int] = Field(None, description="Фильтр по прочности")
    power: Optional[int] = Field(None, description="Фильтр по мощи")
    combat: Optional[int] = Field(None, description="Фильтр по боевым навыкам")


    intelligence_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Интеллект"'
    )
    strength_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Сила"'
    )
    speed_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Скорость"'
    )
    durability_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Прочность"'
    )
    power_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Мощь"'
    )
    combat_operator: Literal['ge', 'le', 'eq'] = Field(
        default='ge',
        description='Оператор для фильтра "Боевые навыки"'
    )

    @field_validator('name', mode='before')
    @classmethod
    def switch_register(cls, value):
        return value.lower()


FiltersDep = Annotated[FiltersSchema, Depends()]




