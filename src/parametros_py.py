import math
from time import time

import pandas as pd
import sympy
from scipy.constants import g as gravidade

from src import data_types as dt
from src.utils import ARQUIVO_CSV, obter_caminho_recurso


def calcular_area(diametro: float, espessura: float) -> float:
    """Calcula a área A do tubo com base na espessura t."""

    return (math.pi / 4.0) * (diametro**2 - (diametro - 2 * espessura) ** 2)


def calcular_momento_inercia(diametro: float, espessura: float) -> float:
    """Calcula o momento de inércia I do tubo com base na espessura t."""
    return (math.pi / 64.0) * (diametro**4 - (diametro - 2 * espessura) ** 4)


def calcular_deslocamento(
    tubo: dt.Tubo,
    material: dt.Material,
) -> dt.Positive_Float:
    """Calcula o deslocamento do tubo com base nos parâmetros fornecidos."""
    area = calcular_area(tubo.diametro, tubo.espessura)
    momento_inercia = calcular_momento_inercia(tubo.diametro, tubo.espessura)

    numerador = (
        material.densidade
        * gravidade
        * area
        * tubo.comprimento**3
        * (3 * tubo.comprimento + 4 * tubo.l_val)
    )
    denominador = 24 * material.modulo_elasticidade * momento_inercia
    deslocamento_pinhole = dt.Positive_Float(numerador / denominador)

    return deslocamento_pinhole


def identificar_material(
    tubo: dt.Tubo,
    deslocamento_medido: dt.Positive_Float,
) -> tuple[str, float]:
    """Compara o deslocamento medido com o deslocamento teórico de cada material."""

    melhor_material = None
    menor_diferenca = float("inf")

    caminho_arquivo_csv = obter_caminho_recurso() / ARQUIVO_CSV
    materiais = pd.read_csv(caminho_arquivo_csv)

    for _, linha in materiais.iterrows():
        material = dt.Material(
            densidade=linha["densidade"],
            modulo_elasticidade=linha["modulo_elasticidade"] * 1e9,
            nome=linha["nome"],
        )

        # Calcula o deslocamento teórico para este material, sem imprimir os passos
        deslocamento_teorico = calcular_deslocamento(tubo, material)

        diferenca = abs(deslocamento_teorico - deslocamento_medido)

        if diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_material = material.nome

    if melhor_material is None:
        raise RuntimeError("Não foi possível encontrar o material especificado.")

    return melhor_material, menor_diferenca


def calcular_comprimento_sympy(
    deslocamento_pinhole: dt.Positive_Float,
    tubo: dt.Tubo,
    material: dt.Material,
    verboso=False,
) -> dt.Positive_Float:
    """
    Calcula o comprimento simbolicamente usando Sympy.
    """
    if verboso:
        print("\n--- Iniciando cálculo simbólico para Comprimento (L) ---")

    comprimento_sym = sympy.Symbol("L", real=True, positive=True)
    area = calcular_area(tubo.diametro, tubo.espessura)
    momento_inercia = calcular_momento_inercia(tubo.diametro, tubo.espessura)
    eq = sympy.Eq(
        deslocamento_pinhole,
        (
            material.densidade
            * gravidade
            * area
            * comprimento_sym**3  # type:ignore
            * (3 * comprimento_sym + 4 * tubo.l_val)  # type:ignore
        )
        / (24 * material.modulo_elasticidade * momento_inercia),
    )
    solucoes = sympy.solve(eq, comprimento_sym)
    for sol in solucoes:
        if sol.is_real and sol > 0:
            return dt.Positive_Float(sol)
    raise ValueError(f"A solução encontrada não é real e positiva: {sol!s}")


def calcular_espessura_sympy(
    deslocamento_pinhole: dt.Positive_Float,
    tubo: dt.Tubo,
    material: dt.Material,
) -> dt.Positive_Float:
    """Calcula a espessura t simbolicamente usando Sympy."""
    t_sym = sympy.Symbol("t", real=True, positive=True)
    area_sym = (sympy.pi / 4) * (tubo.diametro**2 - (tubo.diametro - 2 * t_sym) ** 2)  # type:ignore
    momento_inercia_sym = (sympy.pi / 64) * (
        tubo.diametro**4 - (tubo.diametro - 2 * t_sym) ** 4  # type:ignore
    )
    eq = sympy.Eq(
        deslocamento_pinhole,
        (
            material.densidade
            * gravidade
            * area_sym
            * tubo.comprimento**3
            * (3 * tubo.comprimento + 4 * tubo.l_val)
        )
        / (24 * material.modulo_elasticidade * momento_inercia_sym),
    )

    try:
        sol = sympy.nsolve(eq, t_sym, 0.001)
    except ValueError:
        raise ValueError("Solução não encontrada. Tente um valor de deslocamento menor.")
    if not sol.is_real:
        raise ValueError("Solução real não encontrada.")
    if sol < 0:
        raise ValueError(f"A solução encontrada foi um valor negativo: {sol:.2e} m")
    if sol >= tubo.diametro / 2:
        raise ValueError(
            "Espessura maior ou igual ao raio do tubo. "
            "Tente um valor de deslocamento maior"
        )
    return dt.Positive_Float(sol)


# --- Exemplo de Uso ---
def main() -> None:
    t1 = time()
    # Exemplo de uso das funções

    caminho_arquivo_csv = obter_caminho_recurso() / ARQUIVO_CSV
    materiais = pd.read_csv(caminho_arquivo_csv)
    row = materiais[materiais["apelido"] == "aluminio_6061_t6"]

    material = dt.Material(
        densidade=row["densidade"].to_numpy(dtype=float)[0],
        modulo_elasticidade=row["modulo_elasticidade"].to_numpy(dtype=float)[0],
        nome=row["nome"].to_numpy(dtype=str)[0],
    )

    tubo = dt.Tubo(diametro=0.1, espessura=2e-3, comprimento=1)
    deslocamento_pinhole_calculado = calcular_deslocamento(tubo, material)

    print(f"Comprimento: {deslocamento_pinhole_calculado:.2f} m")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000:.2f} mm")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000000:.2f} µm")
    t2 = time()

    print(f"\nTempo de execução: {(t2 - t1) * 1000:.2f} milisegundos")
    t1 = time()
    material_identificado, diferenca = identificar_material(
        tubo, deslocamento_pinhole_calculado
    )
    print(
        f"\nMaterial identificado: {material_identificado} com diferença de {diferenca * 1000:.2f} mm"
    )
    t2 = time()
    print(f"\nTempo de execução: {(t2 - t1) * 1000:.2f} milisegundos")


if __name__ == "__main__":
    main()
