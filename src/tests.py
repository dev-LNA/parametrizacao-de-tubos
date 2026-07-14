import sympy

from src.utils import D_val, gravidade, l_val


def calcular_espessura_sympy(
    deslocamento_pinhole: float,
    densidade: float,
    comprimento: float,
    modulo_elasticidade: float,
    verboso=False,
):
    """Calcula a espessura t simbolicamente usando Sympy."""
    if verboso:
        print("\n--- Iniciando cálculo simbólico para Espessura ---")
    t_sym = sympy.Symbol("t", real=True, positive=True)
    modulo_elasticidade_pa = modulo_elasticidade * 1e9
    area_sym = (sympy.pi / 4) * (D_val**2 - (D_val - 2 * t_sym) ** 2)  # type:ignore
    momento_inercia_sym = (sympy.pi / 64) * (D_val**4 - (D_val - 2 * t_sym) ** 4)  # type:ignore
    eq = sympy.Eq(
        deslocamento_pinhole,
        (
            densidade
            * gravidade
            * area_sym
            * comprimento**3
            * (3 * comprimento + 4 * l_val)
        )
        / (24 * modulo_elasticidade_pa * momento_inercia_sym),
    )

    return sympy.nsolve(eq, t_sym, 0.001)


deslocamento_pinhole = 0.042e-3
densidade = 2700
comprimento = 1
modulo_elasticidade = 68.9
espessura = calcular_espessura_sympy(
    deslocamento_pinhole, densidade, comprimento, modulo_elasticidade
)
print(f"{espessura} mm")
