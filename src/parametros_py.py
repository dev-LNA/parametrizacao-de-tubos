import math
from pathlib import Path
from time import time
from typing import Any

import pandas as pd
import sympy
from pydantic import PositiveFloat, validate_call

from src.utils import ARQUIVO_CSV, D_val, gravidade, l_val


@validate_call
def calcular_area(espessura, verboso=False) -> float:
    """Calcula a área A do tubo com base na espessura t."""
    return (math.pi / 4.0) * (D_val**2 - (D_val - 2 * espessura) ** 2)


@validate_call
def calcular_momento_inercia(espessura: PositiveFloat, verboso=False):
    """Calcula o momento de inércia I do tubo com base na espessura t."""
    return (math.pi / 64.0) * (D_val**4 - (D_val - 2 * espessura) ** 4)


@validate_call
def calcular_deslocamento(
    densidade: PositiveFloat,
    comprimento: PositiveFloat,
    espessura: PositiveFloat,
    modulo_elasticidade: PositiveFloat,
    verboso=False,
):
    """Calcula o deslocamento do tubo com base nos parâmetros fornecidos."""
    area = calcular_area(espessura, verboso)
    momento_inercia = calcular_momento_inercia(espessura, verboso)
    modulo_elasticidade_pa = modulo_elasticidade * 1e9

    if verboso:
        print("\n--- Etapas do Cálculo de Deslocamento ---")
        print(f"Área (A): {area:.12e} m^2")
        print(f"Momento de Inércia: {momento_inercia:.12e} m^4")
        print(f"Módulo de Elasticidade: {modulo_elasticidade_pa:.12e} Pa")

    numerador = (
        densidade * gravidade * area * (comprimento**3) * (3 * comprimento + 4 * l_val)
    )
    denominador = 24 * modulo_elasticidade_pa * momento_inercia
    deslocamento_pinhole = numerador / denominador

    if verboso:
        print(f"Numerador da equação: {numerador:.6e}")
        print(f"Denominador da equação: {denominador:.6e}")

    return deslocamento_pinhole


@validate_call
def identificar_material(
    comprimento: PositiveFloat,
    espessura: PositiveFloat,
    deslocamento_pinhole_medido: PositiveFloat,
    verboso=False,
) -> tuple[str | None, float | Any]:
    """Compara o deslocamento medido com o deslocamento teórico de cada material."""

    if verboso:
        print("\n--- Iniciando Processo de Identificação ---")
        print(
            f"A comparar com deslocamento medido de {deslocamento_pinhole_medido * 1000:.4f} mm..."
        )

    melhor_material = None
    menor_diferenca = float("inf")

    materiais = pd.read_csv(ARQUIVO_CSV)

    for _, linha in materiais.iterrows():
        densidade = linha["densidade"]
        modulo_elasticidade = linha["modulo_elasticidade"]
        nome = linha["nome"]

        # Calcula o deslocamento teórico para este material, sem imprimir os passos
        deslocamento_pinhole_teorico = calcular_deslocamento(
            densidade, comprimento, espessura, modulo_elasticidade, verboso
        )

        diferenca = abs(deslocamento_pinhole_teorico - deslocamento_pinhole_medido)

        if verboso:
            print(
                f"  - Testando '{nome}': deslocamento teórico = {deslocamento_pinhole_teorico * 1000:.4f} mm (Diferença: {diferenca * 1000:.4f} mm)"
            )
        if diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_material = nome

    return melhor_material, menor_diferenca


@validate_call
def calcular_comprimento_sympy(
    deslocamento_pinhole: PositiveFloat,
    densidade: PositiveFloat,
    espessura: PositiveFloat,
    modulo_elasticidade: PositiveFloat,
    verboso=False,
):
    """
    Calcula o comprimento simbolicamente usando Sympy.
    """
    if verboso:
        print("\n--- Iniciando cálculo simbólico para Comprimento (L) ---")

    comprimento_sym = sympy.Symbol("L", real=True, positive=True)
    area = calcular_area(espessura, verboso)
    momento_inercia = calcular_momento_inercia(espessura, verboso)
    modulo_elasticidade_pa = modulo_elasticidade * 1e9
    eq = sympy.Eq(
        deslocamento_pinhole,
        (
            densidade
            * gravidade
            * area
            * comprimento_sym**3  # type:ignore
            * (3 * comprimento_sym + 4 * l_val)  # type:ignore
        )
        / (24 * modulo_elasticidade_pa * momento_inercia),
    )
    solucoes = sympy.solve(eq, comprimento_sym)
    for sol in solucoes:
        if sol.is_real and sol > 0:
            return float(sol)
    return None


@validate_call
def calcular_espessura_sympy(
    deslocamento_pinhole: PositiveFloat,
    densidade: PositiveFloat,
    comprimento: PositiveFloat,
    modulo_elasticidade: PositiveFloat,
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

    sol = sympy.nsolve(eq, t_sym, 0.001)
    # if sol.is_real and 0 < sol < D_val / 2:
    return float(sol)


# --- Exemplo de Uso ---
def main():
    t1 = time()
    # Exemplo de uso das funções

    materiais = pd.read_csv(ARQUIVO_CSV)
    material = materiais[materiais["apelido"] == "aluminio_6061_t6"]

    rho_exemplo = material["densidade"].values[0]
    E_exemplo = material["modulo_elasticidade"].values[0]
    t_exemplo = 2e-3  # 2 mm
    L_exemplo = 1  # 1 m

    deslocamento_pinhole_calculado = calcular_deslocamento(
        rho_exemplo, L_exemplo, t_exemplo, E_exemplo, verboso=True
    )
    print(f"Comprimento: {deslocamento_pinhole_calculado:.6f} m")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000:.4f} mm")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000000:.2f} µm")
    t2 = time()

    print(f"\nTempo de execução: {(t2 - t1) * 1000:.6f} milisegundos")
    t1 = time()
    material_identificado, diferenca = identificar_material(
        L_exemplo, t_exemplo, deslocamento_pinhole_calculado, verboso=True
    )
    print(
        f"\nMaterial identificado: {material_identificado} com diferença de {diferenca * 1000:.4f} mm"
    )
    t2 = time()
    print(f"\nTempo de execução: {(t2 - t1) * 1000:.6f} milisegundos")


if __name__ == "__main__":
    main()
