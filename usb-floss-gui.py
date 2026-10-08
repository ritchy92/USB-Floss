# ============================================================
# USB-Floss — Interface graphique
# © 2026 Richard Cogne — Tous droits réservés
# made by ritchy
# ============================================================

import os
import sys

import customtkinter as ctk
from PIL import Image

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Polices selon la plateforme
if sys.platform == "darwin":       # macOS
    FONT_MAIN = "SF Pro Display"
    FONT_MONO = "Menlo"
elif sys.platform == "win32":      # Windows
    FONT_MAIN = "Segoe UI"
    FONT_MONO = "Consolas"
else:                              # Linux
    FONT_MAIN = "DejaVu Sans"
    FONT_MONO = "DejaVu Sans Mono"

# Palette (identique à RadioVox)
BG_MAIN = "#000000"
BG_CARD = "#0F161C"
BG_ENTRY = "#1A2530"
BG_HEADER = "#14202B"
CYAN = "#00F0FF"
CYAN_DARK = "#00A8B8"
CYAN_HOVER = "#2A5A66"
TEXT_WHITE = "#FFFFFF"
TEXT_GREY = "#8A9AA9"

# Dimensions des boutons
BTN_W = 170
BTN_H = 34

# Chemin du logo (dans le même dossier que le script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

# Largeur d'affichage du logo
LOGO_WIDTH = 180


# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------
class USBFlossApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("USB-Floss")
        self.geometry("700x600")
        self.minsize(650, 500)
        self.resizable(True, True)
        self.configure(fg_color=BG_MAIN)

        self._logo_image = None

        # ----- En-tête (logo) -----
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=(18, 4))

        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                ratio = img.height / img.width
                new_w = LOGO_WIDTH
                new_h = int(new_w * ratio)
                self._logo_image = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(new_w, new_h)
                )
                ctk.CTkLabel(
                    self.header, image=self._logo_image, text=""
                ).pack(anchor="center", pady=(0, 4))
            except Exception as e:
                print(f"Erreur chargement logo : {e}")
                ctk.CTkLabel(
                    self.header,
                    text="USB-Floss",
                    font=(FONT_MAIN, 28, "bold"),
                    text_color=CYAN,
                ).pack(anchor="center")
        else:
            ctk.CTkLabel(
                self.header,
                text="USB-Floss",
                font=(FONT_MAIN, 28, "bold"),
                text_color=CYAN,
            ).pack(anchor="center")

        # ----- Zone de sélection du volume -----
        # Rempli à l'étape 3

        # ----- Zone de résultats -----
        # Rempli à l'étape 4

        # ----- Zone d'actions -----
        # Rempli à l'étape 5

        # ----- Signature -----
        self.signature = ctk.CTkLabel(
            self,
            text="made by ritchy\n2026",
            font=(FONT_MAIN, 11),
            text_color="#5A6A78",
            fg_color="transparent",
            justify="right",
        )
        self.signature.place(relx=1.0, rely=1.0, anchor="se", x=-15, y=-10)

    # ------------------------------------------------------------------
    # Style bouton commun
    # ------------------------------------------------------------------
    def _btn(self, parent, text, command, small=False):
        if small:
            w, h, f = 80, 30, 12
        else:
            w, h, f = BTN_W, BTN_H, 13
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=(FONT_MAIN, f, "bold"),
            fg_color="transparent",
            border_color=CYAN,
            border_width=1,
            corner_radius=h // 2,
            text_color=TEXT_WHITE,
            hover_color=CYAN_HOVER,
            height=h,
            width=w,
        )


if __name__ == "__main__":
    app = USBFlossApp()
    app.mainloop()