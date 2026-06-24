import os
import webbrowser

import customtkinter as ctk
from PIL import Image, ImageTk

from parametros_py import (
    calcular_comprimento_sympy,
    calcular_deslocamento,
    calcular_espessura_sympy,
    identificar_material,
    materiais,
)

# =============================================================================
# --- Define Caminhos de Arquivo ---
# Obtém o caminho absoluto do diretório onde este script está localizado
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Define os caminhos completos para seus arquivos de imagem
LOGO_PATH = os.path.join(BASE_PATH, "logo.png")  # Para o cabeçalho
ICON_PATH = os.path.join(BASE_PATH, "logo.ico")  # Para o ícone da janela
# =============================================================================

LINK_URL = "https://www.linkedin.com/in/eron-pontes-795b32311/"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Parametrização de Tubos")

        self.geometry("550x600")
        # self.minsize(550, 600)
        self.minsize(650, 600)
        # screen_width = self.winfo_screenwidth()
        # screen_height = self.winfo_screenheight()
        # start_width = max(self.cget("width"), int(screen_width * 0.5))
        # start_height = max(self.cget("height"), int(screen_height * 0.75))
        # x_pos = (screen_width // 2) - (start_width // 2)
        # y_pos = (screen_height // 2) - (start_height // 2)
        # self.geometry(f"{start_width}x{start_height}+{x_pos}+{y_pos}")

        # Configurações de tema
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.button_color = "#14386e"

        self.materiais_list = [materiais[key]["nome"] for key in materiais]

        # --- Layout principal (Corrigido para 3 linhas) ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Linha 0: Cabeçalho
        self.grid_rowconfigure(1, weight=1)  # Linha 1: Abas (expansível)
        self.grid_rowconfigure(2, weight=0)  # Linha 2: Rodapé

        # --- Cabeçalho ---
        self.create_header()

        # --- Área de Abas ---
        self.create_widgets()

        # --- Rodapé ---
        self.create_footer()

    def create_header(self):
        # --- Configura ícone da janela (canto superior esquerdo) ---
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception as e:
                try:
                    pil_icon = Image.open(ICON_PATH).convert("RGBA")
                    self.icon_photo_image = ImageTk.PhotoImage(pil_icon)
                    self.iconphoto(False, self.icon_photo_image)  # type: ignore
                except Exception as e2:
                    print(
                        f"Erro ao definir ícone da janela a partir de {ICON_PATH}: {e} / {e2}"
                    )
        else:
            print(f"Aviso: Ícone da janela não encontrado em {ICON_PATH}")

        # --- Carrega logo do cabeçalho (dentro do app) ---
        self.logo_image_ctk = None
        if os.path.exists(LOGO_PATH):
            try:
                # Este código é apenas para o LOGO DO CABEÇALHO (o .png)
                pil_image = Image.open(LOGO_PATH).convert("RGBA")

                self.logo_image_ctk = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(140, 33),  # Tamanho desejado do logo
                )
            except Exception as e:
                print(f"Erro ao carregar LOGO DO CABEÇALHO de {LOGO_PATH}: {e}")
        else:
            print(f"Aviso: Logo do cabeçalho não encontrado em {LOGO_PATH}")

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

        if self.logo_image_ctk:
            self.logo_label = ctk.CTkLabel(
                self.header_frame, image=self.logo_image_ctk, text=""
            )
            self.logo_label.pack(side="left", padx=(0, 15))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Parametrização de Tubos",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(side="left")

    def create_footer(self):
        """Cria o rodapé com informações e link."""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="ew")

        link_url = LINK_URL  # substitua pela URL desejada

        # Texto inicial
        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text="Por ",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.footer_label.pack(side="left")

        # Nome clicável (estilizado como link)
        self.footer_link = ctk.CTkLabel(
            self.footer_frame,
            text="Eron Pontes Lima",
            font=ctk.CTkFont(size=12),
            text_color="#1a73e8",
            cursor="hand2",
        )
        self.footer_link.pack(side="left")
        self.footer_link.bind("<Button-1>", lambda e: webbrowser.open(link_url))

        # Texto final
        self.footer_label2 = ctk.CTkLabel(
            self.footer_frame,
            text=" -  EME2024",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.footer_label2.pack(side="left")
        self.footer_label.pack(side="left")

    def create_widgets(self):
        """Cria a visualização em abas (TabView)."""
        tab_view = ctk.CTkTabview(self, width=500)
        tab_view.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nsew")

        tabs = [
            "Calc. Deslocamento",
            "Calc. Espessura",
            "Ident. Material",
            "Calc. Comprimento",
        ]
        # Adiciona as abas
        tab_view.add(tabs[0])
        tab_view.add(tabs[1])
        tab_view.add(tabs[2])
        tab_view.add(tabs[3])

        # Popula cada aba
        self.create_tab1(tab_view.tab(tabs[0]))
        self.create_tab2(tab_view.tab(tabs[1]))
        self.create_tab3(tab_view.tab(tabs[2]))
        self.create_tab4(tab_view.tab(tabs[3]))

    # --- Funções Auxiliares de UI ---

    def _create_input_row(self, parent, label_text, row, placeholder_text=None):
        """
        Cria uma linha de Label + Entry com placeholder opcional.
        """
        label = ctk.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=250, placeholder_text=placeholder_text)

        entry.grid(row=row, column=1, padx=10, pady=10, sticky="e")
        return entry

    def _create_material_dropdown(self, parent, row):
        """Cria o dropdown de materiais."""
        label = ctk.CTkLabel(parent, text="Material:")
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        dropdown = ctk.CTkOptionMenu(parent, values=self.materiais_list, width=250)
        dropdown.grid(row=row, column=1, padx=10, pady=10, sticky="e")
        return dropdown

    def _create_result_box(self, parent, row):
        """Cria a caixa de texto para resultados."""
        label = ctk.CTkLabel(parent, text="Resultado:", font=ctk.CTkFont(weight="bold"))
        label.grid(row=row, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        textbox = ctk.CTkTextbox(
            parent, height=180, width=400, state="disabled", wrap="word"
        )
        textbox.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        return textbox

    def _update_result_box(self, box, text):
        """Atualiza o conteúdo da caixa de resultado."""
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    # --- Criação das Abas ---

    def _create_calculator_ui(self, parent_tab, input_config, button_text):
        """
        Função centralizada para criar a UI de uma aba de calculadora.

        Args:
            parent_tab: O widget da aba (tab) onde construir.
            input_config (dict): Um dicionário definindo os inputs.
                Ex: {"material": None, "L": ("Label (L):", "Placeholder..."), ...}
            button_text (str): O texto para o botão de calcular.

        Returns:
            dict: Um dicionário contendo todos os widgets criados ("material", "L", "button", etc.)
        """
        frame = ctk.CTkFrame(parent_tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        created_widgets = {}
        entries_to_validate = []
        current_row = 0

        # Itera sobre a configuração de input para criar os widgets
        for key, config in input_config.items():
            if key == "material":
                # Config é None, apenas cria o dropdown
                widget = self._create_material_dropdown(frame, current_row)
                created_widgets[key] = widget
            else:
                # Config é um tuple (label, placeholder)
                label_text = config[0]
                placeholder = config[1] if len(config) > 1 else None

                widget = self._create_input_row(
                    frame, label_text, current_row, placeholder_text=placeholder
                )

                created_widgets[key] = widget  # Salva o entry (Ex: "L", "t")
                entries_to_validate.append(widget)  # Adiciona à lista para validação

            current_row += 1

        # Cria o Botão (na próxima linha)
        calc_button = ctk.CTkButton(
            frame,
            text=button_text,
            fg_color=self.button_color,
            state="disabled",  # Começa desabilitado
        )
        calc_button.grid(row=current_row, column=0, columnspan=2, padx=10, pady=20)
        created_widgets["button"] = calc_button

        # Cria a Caixa de Resultado (depois do botão)
        result_box_row = current_row + 1
        result_box = self._create_result_box(frame, result_box_row)
        created_widgets["result_box"] = result_box

        # --- Lógica do Botão Dinâmico ---
        def validate_fields(event=None):
            """Habilita o botão se todos os campos de *entrada* estiverem preenchidos."""
            all_filled = True
            for entry in entries_to_validate:
                if not entry.get():
                    all_filled = False
                    break

            if all_filled:
                calc_button.configure(state="normal")
            else:
                calc_button.configure(state="disabled")

        # Vincula a validação a todos os campos de entrada
        for entry in entries_to_validate:
            entry.bind("<KeyRelease>", validate_fields)

        # (O botão já começa desabilitado, então a chamada inicial não é necessária)

        # Retorna todos os widgets para a função 'create_tabX' poder usá-los
        return created_widgets

    def create_tab1(self, tab):
        """Popula a Aba 1: Calcular Deslocamento (u_ph)"""
        # 1. Defina os inputs que esta aba precisa
        inputs = {
            "material": None,  # O "None" significa "crie o dropdown de material"
            "L": ("Comprimento (L) em metros:", "Ex: 1.5"),
            "t": ("Espessura (t) em mm:", "Ex: 25.4"),
        }

        # 2. Crie a UI
        ui = self._create_calculator_ui(tab, inputs, "Calcular Deslocamento")

        # 3. Conecte o botão (a única parte única desta aba)
        ui["button"].configure(
            command=lambda: self.on_calc_deslocamento(
                ui["material"].get(), ui["L"].get(), ui["t"].get(), ui["result_box"]
            )
        )

    def create_tab2(self, tab):
        """Popula a Aba 2: Calcular Espessura (t)"""
        inputs = {
            "material": None,
            "L": ("Comprimento (L) em metros:", "Ex: 1.5"),
            "u_ph": ("Deslocamento (u_ph) em mm:", "Ex: 0.123"),
        }

        ui = self._create_calculator_ui(tab, inputs, "Calcular Espessura")

        ui["button"].configure(
            command=lambda: self.on_calc_espessura(
                ui["material"].get(), ui["L"].get(), ui["u_ph"].get(), ui["result_box"]
            )
        )

    def create_tab3(self, tab):
        """Popula a Aba 3: Identificar Material"""
        inputs = {
            # Note: Sem "material" aqui!
            "L": ("Comprimento (L) em metros:", "Ex: 1.5"),
            "t": ("Espessura (t) em mm:", "Ex: 2.4"),
            "u_ph": ("Deslocamento (u_ph) medido em mm:", "Ex: 0.123"),
        }

        ui = self._create_calculator_ui(tab, inputs, "Identificar Material")

        ui["button"].configure(
            command=lambda: self.on_calc_identificar(
                ui["L"].get(), ui["t"].get(), ui["u_ph"].get(), ui["result_box"]
            )
        )

    def create_tab4(self, tab):
        """Popula a Aba 4: Calcular Comprimento (L)"""
        inputs = {
            "material": None,
            "t": ("Espessura (t) em mm:", "Ex: 25.4"),
            "u_ph": ("Deslocamento (u_ph) em mm:", "Ex: 0.123"),
        }

        ui = self._create_calculator_ui(tab, inputs, "Calcular Comprimento")

        ui["button"].configure(
            command=lambda: self.on_calc_comprimento(
                ui["material"].get(), ui["t"].get(), ui["u_ph"].get(), ui["result_box"]
            )
        )

    def _parse_float(self, text_value):
        """
        Converte um texto para float, aceitando '.' ou ',' como decimal.
        Lança um ValueError com uma mensagem clara se falhar.
        """
        if not text_value:
            # O botão dinâmico deve prevenir isso, mas é uma boa garantia
            raise ValueError("O campo não pode estar vazio.")
        try:
            # Limpa espaços e substitui vírgula por ponto
            cleaned_value = text_value.strip().replace(",", ".")
            return float(cleaned_value)
        except ValueError:
            # Lança um erro mais específico para o usuário
            raise ValueError(f"'{text_value}' não é um número válido.")

    def _get_material_props(self, mat_escolha):
        """
        Encontra e retorna o dicionário de propriedades do material.
        Lança um Exception se não encontrar.
        """
        for key, value in materiais.items():
            if value["nome"] == mat_escolha:
                return value  # Retorna o dicionário de propriedades (ex: props["densidade"])

        # Se o loop terminar sem encontrar, lança um erro
        raise Exception(
            f"Material '{mat_escolha}' não foi encontrado no banco de dados."
        )

    # --- Funções de Callback (Lógica da UI) ---

    def on_calc_deslocamento(self, mat_escolha, L_str, t_str, result_box):
        try:
            # 1. Validação e Conversão
            L = self._parse_float(L_str)
            t_mm = self._parse_float(t_str)
            t = t_mm / 1000  # Converte mm para m

            # 2. Busca de Material
            props = self._get_material_props(mat_escolha)
            rho = props["densidade"]
            E = props["modulo_elasticidade"]

            # 3. Cálculo
            resultado_m = calcular_deslocamento(rho, L, t, E)

            # 4. Formatação de Saída (SIMPLES)
            output = (
                f"Deslocamento (u_ph): {resultado_m * 1000:.4f} mm\n"
                f"Deslocamento (u_ph): {resultado_m * 1000000:.2f} µm"
            )
            self._update_result_box(result_box, output)

        except (ValueError, Exception) as e:
            # 5. Tratamento de Erro
            erro_msg = f"ERRO NA ENTRADA\n--------------------\n{e}"
            self._update_result_box(result_box, erro_msg)

    def on_calc_identificar(self, L_str, t_str, u_ph_str, result_box):
        try:
            L = self._parse_float(L_str)
            t_mm = self._parse_float(t_str)
            u_ph_mm = self._parse_float(u_ph_str)

            t = t_mm / 1000  # mm para m
            u_ph_medido = u_ph_mm / 1000  # mm para m

            if u_ph_medido == 0:
                raise Exception("Deslocamento medido não pode ser zero.")

            material_identificado, diferenca = identificar_material(L, t, u_ph_medido)

            if material_identificado is None:
                raise Exception(
                    "Não foi possível identificar o material (cálculo inválido)."
                )

            erro_percentual = (diferenca / u_ph_medido) * 100

            # 4. Formatação de Saída (SIMPLES)
            output = (
                f"O material mais provável é: '{material_identificado}'\n\n"
                f"Detalhes da Análise:\n"
                f"  Diferença absoluta: {diferenca * 1000:.4f} mm\n"
                f"  Erro percentual: {erro_percentual:.2f}%"
            )
            self._update_result_box(result_box, output)

        except (ValueError, Exception) as e:
            erro_msg = f"ERRO NA ENTRADA OU CÁLCULO\n--------------------\n{e}"
            self._update_result_box(result_box, erro_msg)

    def on_calc_comprimento(self, mat_escolha, t_str, u_ph_str, result_box):
        try:
            t_mm = self._parse_float(t_str)
            u_ph_mm = self._parse_float(u_ph_str)

            t = t_mm / 1000  # mm para m
            u_ph = u_ph_mm / 1000  # mm para m

            props = self._get_material_props(mat_escolha)
            rho = props["densidade"]
            E = props["modulo_elasticidade"]

            resultado_m = calcular_comprimento_sympy(u_ph, rho, t, E)

            if resultado_m is None:
                raise Exception(
                    "Não foi possível encontrar uma solução real e positiva."
                )

            # 4. Formatação de Saída (SIMPLES)
            output = (
                f"Comprimento (L): {resultado_m:.6f} m\n"
                f"Comprimento (L): {resultado_m * 1000:.4f} mm"
            )
            self._update_result_box(result_box, output)

        except (ValueError, Exception) as e:
            erro_msg = f"ERRO NA ENTRADA OU CÁLCULO\n--------------------\n{e}"
            self._update_result_box(result_box, erro_msg)

    def on_calc_espessura(self, mat_escolha, L_str, u_ph_str, result_box):
        try:
            L = self._parse_float(L_str)
            u_ph_mm = self._parse_float(u_ph_str)

            u_ph = u_ph_mm / 1000  # mm para m

            props = self._get_material_props(mat_escolha)
            rho = props["densidade"]
            E = props["modulo_elasticidade"]

            resultado_m = calcular_espessura_sympy(u_ph, rho, L, E)

            if resultado_m is None:
                raise Exception(
                    "Não foi possível encontrar uma solução real e positiva."
                )

            # 4. Formatação de Saída (SIMPLES)
            output = f"Espessura da Parede (t): {resultado_m * 1000:.4f} mm"
            self._update_result_box(result_box, output)

        except (ValueError, Exception) as e:
            erro_msg = f"ERRO NA ENTRADA OU CÁLCULO\n--------------------\n{e}"
            self._update_result_box(result_box, erro_msg)


if __name__ == "__main__":
    if not os.path.exists(LOGO_PATH):
        print(f"DEBUG: logo.png not found at {LOGO_PATH}")
    if not os.path.exists(ICON_PATH):
        print(f"DEBUG: logo.ico not found at {ICON_PATH}")
    app = App()
    app.mainloop()
