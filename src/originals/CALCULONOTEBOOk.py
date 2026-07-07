import math
import sympy

# --- Base de Dados de Materiais ---
materiais = {
    "aluminio_6061_o": {"densidade": 2700, "modulo_elasticidade": 68.9},
    "aluminio_6061_t6": {"densidade": 2700, "modulo_elasticidade": 69},
    "aluminio_5052_h32": {"densidade": 2680, "modulo_elasticidade": 70.3},
    "inox_304": {"densidade": 7990, "modulo_elasticidade": 193},
    "inox_316": {"densidade": 7990, "modulo_elasticidade": 193},
    "inox_430": {"densidade": 7800, "modulo_elasticidade": 200},
    "aco_carbono_1045": {"densidade": 7850, "modulo_elasticidade": 205},
}

# --- Parâmetros Fixos ---
g_val = 9.81
l_val = 100 / 1000
D_val = 100 / 1000

# --- Funções de Cálculo ---

def calcular_area(t):
    return (math.pi / 4) * (D_val**2 - (D_val - 2 * t) ** 2)

def calcular_momento_inercia(t):
    return (math.pi / 64) * (D_val**4 - (D_val - 2 * t) ** 4)

def calcular_deslocamento(rho, L, t, E, verboso=True):
    """Calcula o deslocamento. O modo 'verboso=False' é para uso interno."""
    A = calcular_area(t)
    I = calcular_momento_inercia(t)
    E_pa = E * 1e9

    if verboso:
        print("\n--- Etapas do Cálculo de Deslocamento ---")
        print(f"Área (A): {A:.1e} m^2")
        print(f"Momento de Inércia (I): {I:.12f} m^4")
        print(f"Módulo de Elasticidade (E): {E_pa:.2e} Pa")

    numerador = rho * g_val * A * (L**3) * (3 * L + 4 * l_val)
    denominador = 24 * E_pa * I
    u_ph = numerador / denominador

    if verboso:
        print(f"Numerador da equação: {numerador:.6e}")
        print(f"Denominador da equação: {denominador:.6e}")

    return u_ph

def identificar_material(L, t, u_ph_medido):
    """Compara o deslocamento medido com o deslocamento teórico de cada material."""
    print("\n--- Iniciando Processo de Identificação ---")
    print(f"A comparar com deslocamento medido de {u_ph_medido * 1000:.4f} mm...")

    melhor_material = None
    menor_diferenca = float('inf')

    for nome, propriedades in materiais.items():
        rho = propriedades["densidade"]
        E = propriedades["modulo_elasticidade"]

        # Calcula o deslocamento teórico para este material, sem imprimir os passos
        u_ph_teorico = calcular_deslocamento(rho, L, t, E, verboso=False)

        diferenca = abs(u_ph_teorico - u_ph_medido)

        print(f"  - Testando '{nome}': deslocamento teórico = {u_ph_teorico * 1000:.4f} mm (Diferença: {diferenca*1000:.4f} mm)")

        if diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_material = nome

    return melhor_material, menor_diferenca

# (As funções com Sympy permanecem iguais)
def calcular_comprimento_sympy(u_ph, rho, t, E):
    print("\n--- Iniciando cálculo simbólico para Comprimento (L) ---")
    L_sym = sympy.Symbol('L', real=True, positive=True)
    A = calcular_area(t)
    I = calcular_momento_inercia(t)
    E_pa = E * 1e9
    eq = sympy.Eq(u_ph, (rho * g_val * A * L_sym**3 * (3 * L_sym + 4 * l_val)) / (24 * E_pa * I))
    solucoes = sympy.solve(eq, L_sym)
    for sol in solucoes:
        if sol.is_real and sol > 0: return float(sol)
    return None

def calcular_espessura_sympy(u_ph, rho, L, E):
    print("\n--- Iniciando cálculo simbólico para Espessura (t) ---")
    t_sym = sympy.Symbol('t', real=True, positive=True)
    E_pa = E * 1e9
    A_sym = (sympy.pi / 4) * (D_val**2 - (D_val - 2 * t_sym)**2)
    I_sym = (sympy.pi / 64) * (D_val**4 - (D_val - 2 * t_sym)**4)
    eq = sympy.Eq(u_ph, (rho * g_val * A_sym * L**3 * (3 * L + 4 * l_val)) / (24 * E_pa * I_sym))
    try:
        sol = sympy.nsolve(eq, t_sym, 0.001)
        if sol.is_real and 0 < sol < D_val / 2: return float(sol)
    except Exception: pass
    return None

# --- Interface com o Usuário ---
def main():
    print("Bem-vindo à Calculadora da Linha Elástica!")
    print("=" * 40)
    print("O que você deseja fazer?")
    print("1. Calcular Deslocamento do Pinhole (u_ph)")
    print("2. Identificar Material")
    print("3. Calcular Comprimento do Tubo (L)")
    print("4. Calcular Espessura da Parede (t)")
    escolha = input("Digite o número da sua escolha: ")

    try:
        if escolha == "2":
            print("\n--- Identificação de Material ---")
            print("Forneça os dados medidos para identificar o material.")

            L = float(input("Digite o Comprimento do Tubo (L) em metros: "))
            t = float(input("Digite a Espessura da Parede (t) em mm: ")) / 1000
            u_ph_medido = float(input("Digite o Deslocamento do Pinhole (u_ph) medido em mm: ")) / 1000

            material_identificado, diferenca = identificar_material(L, t, u_ph_medido)

            erro_percentual = (diferenca / u_ph_medido) * 100 if u_ph_medido != 0 else 0

            print(f"\n--- Resultado Final ---")
            print(f"O material mais provável é: '{material_identificado}'")
            print(f"A diferença entre o deslocamento medido e o teórico para este material foi de {diferenca*1000:.4f} mm ({erro_percentual:.2f}% de erro).")

        else:
            print("\nEscolha o material (digite o nome exato):")
            for mat in materiais:
                print(f"- {mat}")
            mat_escolha = input("Digite o nome do material: ").lower()
            if mat_escolha not in materiais:
                print("Material não encontrado!")
                return

            rho_material = materiais[mat_escolha]["densidade"]
            E_material = materiais[mat_escolha]["modulo_elasticidade"]

            print("\n--- Variáveis Conhecidas ---")
            print(f"Material: {mat_escolha}")
            print(f"Densidade (ρ): {rho_material} kg/m^3")
            print(f"Módulo de Elasticidade (E): {E_material} GPa")
            print("-" * 30)

            if escolha == "1":
                L = float(input("Digite o Comprimento do Tubo (L) em metros: "))
                t = float(input("Digite a Espessura da Parede (t) em mm: ")) / 1000
                resultado_m = calcular_deslocamento(rho_material, L, t, E_material)
                print(f"\n--- Resultado Final ---")
                print(f"Deslocamento (u_ph): {resultado_m * 1000:.4f} mm")
                print(f"Deslocamento (u_ph): {resultado_m * 1000000:.2f} µm")

            elif escolha == "3":
                t = float(input("Digite a Espessura da Parede (t) em mm: ")) / 1000
                u_ph = float(input("Digite o Deslocamento do Pinhole (u_ph) em mm: ")) / 1000
                resultado_m = calcular_comprimento_sympy(u_ph, rho_material, t, E_material)
                if resultado_m is not None:
                    print(f"\n--- Resultado Final ---")
                    print(f"Comprimento (L): {resultado_m:.6f} m")
                    print(f"Comprimento (L): {resultado_m * 1000:.4f} mm")
                    print(f"Comprimento (L): {resultado_m * 1000000:.2f} µm")
                else:
                    print("\n--- Falha no Cálculo ---")
                    print("Não foi possível encontrar uma solução real e positiva.")

            elif escolha == "4":
                L = float(input("Digite o Comprimento do Tubo (L) em metros: "))
                u_ph = float(input("Digite o Deslocamento do Pinhole (u_ph) em mm: ")) / 1000
                resultado_m = calcular_espessura_sympy(u_ph, rho_material, L, E_material)
                if resultado_m is not None:
                    print(f"\n--- Resultado Final ---")
                    print(f"Espessura da Parede (t): {resultado_m * 1000:.4f} mm")
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
