from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class Material(BaseModel):
    densidade: float = Field(gt=0)
    modulo_elasticidade: float = Field(gt=0)
    nome: Literal[
        "Al 6061-O",
        "Al 6061-T6",
        "Al 5052-H32",
        "Inox 304",
        "Inox 316",
        "Inox 430",
        "Aço 1045",
    ]


class Tubo(BaseModel):
    diametro: float = Field(gt=0)
    espessura: float = Field(gt=0)
    comprimento: float = Field(gt=0, default=0)
    l_val: float = 0.1

    @model_validator(mode="after")
    def valida_espessura(self) -> Self:
        if 2 * self.espessura > self.diametro:
            raise ValueError(
                f"A espessura deve ser menor do que {self.diametro / 2}: {self.espessura}"
            )
        return self
