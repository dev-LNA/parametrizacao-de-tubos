import pytest

from src import data_types as dt


class Test_Data_types:
    def test_tubo(self) -> None:
        tubo = dt.Tubo(diametro=0.1, espessura=1e-3, comprimento=1)
        assert tubo.l_val == 0.1

    def test_tubo_erro(self) -> None:
        with pytest.raises(ValueError):
            dt.Tubo(diametro=1, espessura=0.6, comprimento=1)

    def test_material(self) -> None:
        dt.Material(densidade=0.1, modulo_elasticidade=68.9, nome="Al 5052-H32")
