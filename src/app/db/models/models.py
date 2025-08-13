from typing import Annotated

from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from src.config import Base

pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[pk]
    name: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    intelligence: Mapped[int] = mapped_column(
                                            CheckConstraint("intelligence >= 0 AND intelligence <= 100"),
                                            nullable=False
                                                )
    strength: Mapped[int] = mapped_column(
                                        CheckConstraint("strength >= 0 AND strength <= 100"),
                                        nullable=False
                                            )
    speed: Mapped[int] = mapped_column(
                                    CheckConstraint("speed >= 0 AND speed <= 100"),
                                    nullable=False
                                        )
    durability: Mapped[int] = mapped_column(
                                        CheckConstraint("durability >= 0 AND durability <= 100"),
                                        nullable=False
                                            )
    power: Mapped[int] = mapped_column(
                                    CheckConstraint("power >= 0 AND power <= 100"),
                                    nullable=False
                                        )
    combat: Mapped[int] = mapped_column(
                                    CheckConstraint("combat >= 0 AND combat <= 100"),
                                    nullable=False
                                        )


