import math
from pathlib import Path
from typing import Any

import pandas as pd
import sympy

from src.utils import ARQUIVO_CSV, D_val, gravidade, l_val


def calcular_area(espessura):
    return (math.pi / 4) * (D_val**2 - (D_val - 2 * espessura) ** 2)


def calcular_momento_inercia(espessura):
    return (math.pi / 64) * (D_val**4 - (D_val - 2 * espessura) ** 4)


def calcular_deslocamento(
    densidade, comprimento, espessura, modulo_elasticidade, verboso=True
):
    """Calcula o deslocamento. O modo 'verboso=False' é para uso interno."""
    area = calcular_area(espessura)
    momento_inercia = calcular_momento_inercia(espessura)
    E_pa = modulo_elasticidade * 1e9

    if verboso:
        print("\n--- Etapas do Cálculo de Deslocamento ---")
        print(f"Área (A): {area:.1e} m^2")
        print(f"Momento de Inércia (I): {momento_inercia:.12f} m^4")
        print(f"Módulo de Elasticidade (E): {E_pa:.2e} Pa")

    numerador = (
        densidade * gravidade * area * (comprimento**3) * (3 * comprimento + 4 * l_val)
    )
    denominador = 24 * E_pa * momento_inercia
    u_ph = numerador / denominador

    if verboso:
        print(f"Numerador da equação: {numerador:.6e}")
        print(f"Denominador da equação: {denominador:.6e}")

    return u_ph


def identificar_material(
    comprimento, espessura, u_ph_medido
) -> tuple[str | None, float | Any]:
    """Compara o deslocamento medido com o deslocamento teórico de cada material."""
    print("\n--- Iniciando Processo de Identificação ---")
    print(f"A comparar com deslocamento medido de {u_ph_medido * 1000:.4f} mm...")

    melhor_material = None
    menor_diferenca = float("inf")
    materiais = pd.read_csv(ARQUIVO_CSV)

    for _, linha in materiais.iterrows():
        densidade = linha["densidade"]
        modulo_elasticidade = linha["modulo_elasticidade"]
        nome = linha["nome"]

        # Calcula o deslocamento teórico para este material, sem imprimir os passos
        u_ph_teorico = calcular_deslocamento(
            densidade, comprimento, espessura, modulo_elasticidade, verboso=False
        )

        diferenca = abs(u_ph_teorico - u_ph_medido)

        print(
            f"  - Testando '{nome}': deslocamento teórico = {u_ph_teorico * 1000:.4f} mm (Diferença: {diferenca * 1000:.4f} mm)"
        )

        if diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_material = nome

    return melhor_material, menor_diferenca


def identificar_material_1(
    comprimento, espessura, u_ph_medido
) -> tuple[str | None, float | Any]:
    """Compara o deslocamento medido com o deslocamento teórico de cada material."""
    print("\n--- Iniciando Processo de Identificação ---")
    print(f"A comparar com deslocamento medido de {u_ph_medido * 1000:.4f} mm...")

    melhor_material = None
    menor_diferenca = float("inf")
    materiais = pd.read_csv(ARQUIVO_CSV)

    for _, linha in materiais.iterrows():
        densidade = linha["densidade"]
        modulo_elasticidade = linha["modulo_elasticidade"]
        nome = linha["nome"]

        # Calcula o deslocamento teórico para este material, sem imprimir os passos
        u_ph_teorico = calcular_deslocamento(
            densidade, comprimento, espessura, modulo_elasticidade, verboso=False
        )

        diferenca = abs(u_ph_teorico - u_ph_medido)

        print(
            f"  - Testando '{nome}': deslocamento teórico = {u_ph_teorico * 1000:.4f} mm (Diferença: {diferenca * 1000:.4f} mm)"
        )

        if diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_material = nome

    return melhor_material, menor_diferenca


# (As funções com Sympy permanecem iguais)
def calcular_comprimento_sympy(
    u_ph, densidade, espessura, modulo_elasticidade
) -> float | None:
    print("\n--- Iniciando cálculo simbólico para Comprimento (L) ---")
    L_sym = sympy.Symbol("L", real=True, positive=True)
    area = calcular_area(espessura)
    momento_inercia = calcular_momento_inercia(espessura)
    E_pa = modulo_elasticidade * 1e9
    eq = sympy.Eq(
        u_ph,
        (densidade * gravidade * area * L_sym**3 * (3 * L_sym + 4 * l_val))  # type: ignore
        / (24 * E_pa * momento_inercia),
    )
    solucoes = sympy.solve(eq, L_sym)
    for sol in solucoes:
        if sol.is_real and sol > 0:
            return float(sol)
    return None


def calcular_espessura_sympy(
    u_ph, densidade, comprimento, modulo_elasticidade
) -> float | None:
    print("\n--- Iniciando cálculo simbólico para Espessura ---")
    t_sym = sympy.Symbol("t", real=True, positive=True)
    E_pa = modulo_elasticidade * 1e9
    A_sym = (sympy.pi / 4) * (D_val**2 - (D_val - 2 * t_sym) ** 2)  # type: ignore
    I_sym = (sympy.pi / 64) * (D_val**4 - (D_val - 2 * t_sym) ** 4)  # type: ignore
    eq = sympy.Eq(
        u_ph,
        (densidade * gravidade * A_sym * comprimento**3 * (3 * comprimento + 4 * l_val))
        / (24 * E_pa * I_sym),
    )
    try:
        sol = sympy.nsolve(eq, t_sym, 0.001)
        if sol.is_real and 0 < sol < D_val / 2:
            return float(sol)
    except Exception:
        pass
    return None


# --- Interface com o Usuário ---
def main():
    print("Bem-vindo à Calculadora da Linha Elástica!")
    print("=" * 40)
    print("O que você deseja fazer?")
    print("1. Calcular Deslocamento do Pinhole (u_ph)")
    print("2. Identificar Material")
    print("3. Calcular Comprimento do Tubo")
    print("4. Calcular Espessura da Parede")
    escolha = input("Digite o número da sua escolha: ")

    try:
        if escolha == "2":
            print("\n--- Identificação de Material ---")
            print("Forneça os dados medidos para identificar o material.")

            comprimento = float(input("Digite o Comprimento do Tubo em metros: "))
            espessura = float(input("Digite a Espessura da Parede em mm: ")) / 1000
            u_ph_medido = (
                float(input("Digite o Deslocamento do Pinhole (u_ph) medido em mm: "))
                / 1000
            )

            material_identificado, diferenca = identificar_material(
                comprimento, espessura, u_ph_medido
            )

            erro_percentual = (diferenca / u_ph_medido) * 100 if u_ph_medido != 0 else 0

            print("\n--- Resultado Final ---")
            print(f"O material mais provável é: '{material_identificado}'")
            print(
                f"A diferença entre o deslocamento medido e o teórico para este material foi de {diferenca * 1000:.4f} mm ({erro_percentual:.2f}% de erro)."
            )

        else:
            print("\nEscolha o material (digite o nome exato):")
            materiais = pd.read_csv(ARQUIVO_CSV)

            for apelido in materiais["apelido"]:
                print(f"- {apelido}")
            mat_escolha = input("Digite o nome do material: ").lower()
            if mat_escolha not in materiais["apelido"]:
                print("Material não encontrado!")
                return

            material = materiais[materiais["apelido"] == mat_escolha]
            rho_material = material["densidade"].values[0]
            E_material = material["modulo_elasticidade"].values[0]

            print("\n--- Variáveis Conhecidas ---")
            print(f"Material: {mat_escolha}")
            print(f"Densidade (ρ): {rho_material} kg/m^3")
            print(f"Módulo de Elasticidade (E): {E_material} GPa")
            print("-" * 30)

            if escolha == "1":
                comprimento = float(
                    input("Digite o Comprimento do Tubo (L) em metros: ")
                )
                espessura = float(input("Digite a Espessura da Parede em mm: ")) / 1000
                resultado_m = calcular_deslocamento(
                    rho_material, comprimento, espessura, E_material
                )
                print("\n--- Resultado Final ---")
                print(f"Deslocamento (u_ph): {resultado_m * 1000:.4f} mm")
                print(f"Deslocamento (u_ph): {resultado_m * 1000000:.2f} µm")

            elif escolha == "3":
                espessura = float(input("Digite a Espessura da Parede em mm: ")) / 1000
                u_ph = (
                    float(input("Digite o Deslocamento do Pinhole (u_ph) em mm: "))
                    / 1000
                )
                resultado_m = calcular_comprimento_sympy(
                    u_ph, rho_material, espessura, E_material
                )
                if resultado_m is not None:
                    print("\n--- Resultado Final ---")
                    print(f"Comprimento (L): {resultado_m:.6f} m")
                    print(f"Comprimento (L): {resultado_m * 1000:.4f} mm")
                    print(f"Comprimento (L): {resultado_m * 1000000:.2f} µm")
                else:
                    print("\n--- Falha no Cálculo ---")
                    print("Não foi possível encontrar uma solução real e positiva.")

            elif escolha == "4":
                comprimento = float(
                    input("Digite o Comprimento do Tubo (L) em metros: ")
                )
                u_ph = (
                    float(input("Digite o Deslocamento do Pinhole (u_ph) em mm: "))
                    / 1000
                )
                resultado_m = calcular_espessura_sympy(
                    u_ph, rho_material, comprimento, E_material
                )
                if resultado_m is not None:
                    print("\n--- Resultado Final ---")
                    print(f"Espessura da Parede: {resultado_m * 1000:.4f} mm")
                else:
                    print("\n--- Falha no Cálculo ---")
                    print("Não foi possível encontrar uma solução real e positiva.")

            else:
                print("Escolha inválida!")

    except ValueError:
        print("\nErro: Por favor, insira um número válido.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
