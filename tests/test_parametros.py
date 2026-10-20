import unittest

from src import data_types as dt
from src.parametros_py import (
    calcular_area,
    calcular_comprimento_sympy,
    calcular_deslocamento,
    calcular_espessura_sympy,
    calcular_momento_inercia,
    identificar_material,
)


class Test_Parametros(unittest.TestCase):
    def test_calc_area(self) -> None:
        area = calcular_area(diametro=0.1, espessura=1e-3)
        assert area == 0.00031101767270538995

    def test_calc_momento_inercia(self) -> None:
        momento = calcular_momento_inercia(0.1, 1e-3)
        assert momento == 3.81074403482279e-07

    def test_calc_deslocamento(self) -> None:
        tubo = dt.Tubo(diametro=0.1, espessura=1e-3, comprimento=1)
        material = dt.Material(
            nome=dt.Materiais_Cadastrados.AL_6061_0,
            densidade=2700,
            modulo_elasticidade=68.9 * 1e9,
        )
        deslocamento = calcular_deslocamento(tubo, material)
        assert deslocamento == 4.443326041396131e-05

    def test_calc_comprimento(self) -> None:
        tubo = dt.Tubo(diametro=0.1, espessura=1e-3, comprimento=1)
        material = dt.Material(
            nome=dt.Materiais_Cadastrados.AL_6061_0,
            densidade=2700,
            modulo_elasticidade=68.9 * 1e9,
        )
        deslocamento = dt.Positive_Float(1e-3)
        comprimento = calcular_comprimento_sympy(deslocamento, tubo, material)
        assert comprimento == 2.214700653613681

    def test_calc_espessura(self) -> None:
        tubo = dt.Tubo(diametro=0.1, comprimento=2, espessura=1e-3)
        material = dt.Material(
            nome=dt.Materiais_Cadastrados.AL_6061_0,
            densidade=2700,
            modulo_elasticidade=68.9 * 1e9,
        )
        deslocamento = dt.Positive_Float(7e-4)
        espessura = calcular_espessura_sympy(deslocamento, tubo, material)
        assert espessura == 0.0032587519737255584

    def test_identifica_material(self) -> None:
        tubo = dt.Tubo(diametro=0.1, comprimento=2, espessura=1e-3)
        deslocamento = dt.Positive_Float(1e-4)
        material, deslocamento = identificar_material(tubo, deslocamento)
        assert material == dt.Materiais_Cadastrados.AL_5052_H32
