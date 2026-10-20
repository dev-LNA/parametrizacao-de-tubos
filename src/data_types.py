from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class Materiais_Cadastrados(StrEnum):
    AL_6061_0 = "Al 6061-O"
    AL_6061_T6 = "Al 6061-T6"
    AL_5052_H32 = "Al 5052-H32"
    INOX_304 = "Inox 304"
    INOX_316 = "Inox 316"
    INOX_430 = "Inox 430"
    AÇO_1045 = "Aço 1045"


class Material(BaseModel):
    densidade: float = Field(gt=0)
    modulo_elasticidade: float = Field(gt=0)
    nome: Materiais_Cadastrados


class Tubo(BaseModel):
    diametro: float = Field(gt=0)
    espessura: float = Field(gt=0, default=0)
    comprimento: float = Field(gt=0, default=0)
    l_val: float = 0.1

    @model_validator(mode="after")
    def valida_espessura(self) -> Self:
        if 2 * self.espessura > self.diametro:
            raise ValueError(
                f"A espessura deve ser menor do que {self.diametro / 2} m: {self.espessura}"
            )
        return self

    def espessura_valida(self, espessura: float) -> bool:
        return not (espessura <= 0 or espessura > self.diametro / 2)


class Positive_Float(float):
    """Tipo derivado de float que aceita apenas valores estritamente positivos (> 0)."""

    def __new__(cls, value: float | str) -> Self:
        value = super().__new__(cls, value)
        if value <= 0:
            raise ValueError(
                f"O valor deve ser um número positivo (> 0), recebido: {value}"
            )

        return value

    def __truediv__(self, value: float) -> Positive_Float:
        res = super().__truediv__(value)
        return Positive_Float(res)
