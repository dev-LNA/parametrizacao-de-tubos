import os
import sys
from pathlib import Path

from pydantic import BaseModel, PositiveFloat

# --- Parâmetros Fixos ---
gravidade = 9.81
l_val = 100 / 1000
D_val = 100 / 1000

# =============================================================================
# --- Define Caminhos de Arquivo ---
# Obtém o caminho absoluto do diretório onde este script está localizado
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Define os caminhos completos para seus arquivos de imagem
LOGO_PATH = os.path.join(BASE_PATH, "logo.png")  # Para o cabeçalho
ICON_PATH = os.path.join(BASE_PATH, "logo.ico")  # Para o ícone da janela
# =============================================================================

LINK_URL = "https://www.linkedin.com/in/eron-pontes-795b32311/"

ARQUIVO_CSV = Path("src/csv/materiais.csv")


def obter_caminho_recurso() -> Path:
    """Retorna o caminho absoluto para o recurso, tanto em desenvolvimento quanto no .exe"""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")

    return Path(base_path)
