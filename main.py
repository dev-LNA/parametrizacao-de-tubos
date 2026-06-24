import os

from src.AppY import App
from src.utils import ICON_PATH, LOGO_PATH

if __name__ == "__main__":
    if not os.path.exists(LOGO_PATH):
        print(f"DEBUG: logo.png not found at {LOGO_PATH}")
    if not os.path.exists(ICON_PATH):
        print(f"DEBUG: logo.ico not found at {ICON_PATH}")
    app = App()
    app.mainloop()
