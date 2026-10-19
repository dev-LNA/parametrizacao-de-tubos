import unittest

from src import data_types as dt
from src.parametros_py import (
    calcular_area,
    calcular_deslocamento,
    calcular_momento_inercia,
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
            nome="Al 6061-O", densidade=2700, modulo_elasticidade=68.9 * 1e9
        )
        deslocamento = calcular_deslocamento(tubo, material)
        assert deslocamento == 4.443326041396131e-05
