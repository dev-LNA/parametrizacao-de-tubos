import math
from time import time
from typing import Any

import pandas as pd
import sympy
from pydantic import PositiveFloat, validate_call
from scipy.constants import g as gravidade

from src import data_types as dt
from src.utils import ARQUIVO_CSV, obter_caminho_recurso


@validate_call
def calcular_area(diametro: float, espessura: float) -> float:
    """Calcula a área A do tubo com base na espessura t."""

    return (math.pi / 4.0) * (diametro**2 - (diametro - 2 * espessura) ** 2)


@validate_call
def calcular_momento_inercia(diametro: float, espessura: float) -> float:
    """Calcula o momento de inércia I do tubo com base na espessura t."""
    return (math.pi / 64.0) * (diametro**4 - (diametro - 2 * espessura) ** 4)


@validate_call
def calcular_deslocamento(
    tubo: dt.Tubo,
    material: dt.Material,
    verboso=False,
) -> float:
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
    deslocamento_pinhole = numerador / denominador

    if verboso:
        print("\n--- Etapas do Cálculo de Deslocamento ---")
        print(f"Área (A): {area:.12e} m^2")
        print(f"Momento de Inércia: {momento_inercia:.12e} m^4")
        print(f"Módulo de Elasticidade: {material.modulo_elasticidade:.3e} Pa")
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

    caminho_arquivo_csv = obter_caminho_recurso() / ARQUIVO_CSV
    materiais = pd.read_csv(caminho_arquivo_csv)

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
    tubo: dt.Tubo,
    material: dt.Material,
    verboso=False,
) -> float:
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
            return float(sol)
    raise ValueError(f"A solução encontrada não é real e positiva: {sol!s}")


@validate_call
def calcular_espessura_sympy(
    deslocamento_pinhole: PositiveFloat,
    densidade: PositiveFloat,
    comprimento: PositiveFloat,
    modulo_elasticidade: PositiveFloat,
    verboso=False,
) -> float:
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

    try:
        sol = sympy.nsolve(eq, t_sym, 0.001)
    except Exception:
        raise ValueError("Solução não encontrada. Tente um valor de deslocamento menor.")
    if not sol.is_real:
        raise ValueError("Não existe uma solução real.")
    sol = float(sol)
    if sol < 0:
        raise ValueError(
            f"A solução encontrada foi um valor negativo: {sol * 1e3:.3f} mm"
        )
    if sol >= D_val / 2:
        raise ValueError(f"Espessura maior ou igual ao raio do tubo: {sol * 1e3:.3f} mm")
    return sol


# --- Exemplo de Uso ---
def main() -> None:
    t1 = time()
    # Exemplo de uso das funções

    caminho_arquivo_csv = obter_caminho_recurso() / ARQUIVO_CSV
    materiais = pd.read_csv(caminho_arquivo_csv)
    material = materiais[materiais["apelido"] == "aluminio_6061_t6"]

    rho_exemplo = material["densidade"].to_numpy(dtype=float)[0]
    E_exemplo = material["modulo_elasticidade"].to_numpy(dtype=float)[0]
    t_exemplo = 2e-3  # 2 mm
    L_exemplo = 1  # 1 m

    deslocamento_pinhole_calculado = calcular_deslocamento(
        rho_exemplo, L_exemplo, t_exemplo, E_exemplo, verboso=True
    )
    print(f"Comprimento: {deslocamento_pinhole_calculado:.2f} m")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000:.2f} mm")
    print(f"Comprimento: {deslocamento_pinhole_calculado * 1000000:.2f} µm")
    t2 = time()

    print(f"\nTempo de execução: {(t2 - t1) * 1000:.2f} milisegundos")
    t1 = time()
    material_identificado, diferenca = identificar_material(
        L_exemplo, t_exemplo, deslocamento_pinhole_calculado, verboso=True
    )
    print(
        f"\nMaterial identificado: {material_identificado} com diferença de {diferenca * 1000:.2f} mm"
    )
    t2 = time()
    print(f"\nTempo de execução: {(t2 - t1) * 1000:.2f} milisegundos")


if __name__ == "__main__":
    main()
