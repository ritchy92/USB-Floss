# ============================================================
# USB-Floss — Interface graphique
# © 2026 Richard Cogne — Tous droits réservés
# made by ritchy
# ============================================================

import os
import sys

import customtkinter as ctk
from PIL import Image

from usbfloss import list_volumes, format_size

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
LOGO_ACCENT = "#3DDFA0"   # à ajuster selon le rendu
CYAN = "#00F0FF"
CYAN_DARK = "#00A8B8"
CYAN_BRIGHT = "#3BFCFF"   # contour lumineux (combo + boutons)
CYAN_HOVER = "#23A7C8"
TEXT_WHITE = "#FFFFFF"
TEXT_GREY = "#8A9AA9"

# Dimensions des boutons
BTN_W = 100
BTN_H = 34
BTN_SMALL_W = 90
BTN_SMALL_H = 34

# Constante pour la hauteur de la combo (même que les boutons)
COMBO_HEIGHT = BTN_H

# Padding pour l'alignement
COMBO_PADDING_X = 8          # espacement horizontal entre combo et boutons
COMBO_PADDING_TOP = 18       # décalage vertical pour aligner les boutons avec le haut de la combo
LABEL_PADDING_BOTTOM = 4     # espacement entre label et combo
BTN_SPACING = 4              # espacement entre les boutons

# Chemin du logo (dans le même dossier que le script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

# Largeur d'affichage du logo
LOGO_WIDTH = 140

# Largeur de la combo volume
COMBO_W = 200


# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------
class USBFlossApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("USB-Floss")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        self._logo_image = None
        self.volumes = []

        # ----- En-tête (logo) -----
        self._build_header()

        # ----- Zone de sélection du volume -----
        self._build_volume_selector()

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

        # ----- Premier scan des volumes -----
        self.refresh_volumes()

    # ------------------------------------------------------------------
    # Construction : en-tête (logo)
    # ------------------------------------------------------------------
    def _build_header(self):
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
                lbl = ctk.CTkLabel(self.header, image=self._logo_image, text="")
                lbl.pack(anchor="center", pady=(0, 4))
            except Exception as e:
                print(f"Erreur chargement logo : {e}")
                lbl = ctk.CTkLabel(
                    self.header,
                    text="USB-Floss",
                    font=(FONT_MAIN, 28, "bold"),
                    text_color=CYAN,
                )
                lbl.pack(anchor="center")
        else:
            lbl = ctk.CTkLabel(
                self.header,
                text="USB-Floss",
                font=(FONT_MAIN, 28, "bold"),
                text_color=CYAN,
            )
            lbl.pack(anchor="center")

    # ------------------------------------------------------------------
    # Construction : sélection du volume
    # ------------------------------------------------------------------
    def _build_volume_selector(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(10, 10))

        # Bloc centré contenant : [cellule label+combo] à gauche, boutons à droite.
        block = ctk.CTkFrame(frame, fg_color="transparent")
        block.pack(anchor="center", pady=10)

        block.grid_columnconfigure(0, weight=0)
        block.grid_columnconfigure(1, weight=0)

        # ----- Cellule : label + combo empilés, label centré -----
        cell = ctk.CTkFrame(block, fg_color="transparent")
        cell.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            cell,
            text="Volume à nettoyer",
            font=(FONT_MAIN, 14),
            text_color=LOGO_ACCENT,
            anchor="center",
        ).pack(anchor="center", pady=(0, LABEL_PADDING_BOTTOM))

        self.combo_volume = ctk.CTkComboBox(
            cell,
            values=["Aucun volume détecté"],
            width=COMBO_W,
            font=(FONT_MAIN, 13),
            dropdown_font=(FONT_MAIN, 13),
            fg_color=BG_CARD,
            border_color=CYAN_BRIGHT,
            border_width=1,
            button_color=CYAN_DARK,
            button_hover_color=CYAN,
            text_color=TEXT_WHITE,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_WHITE,
            dropdown_hover_color=CYAN_HOVER,
            corner_radius=17,
            height=COMBO_HEIGHT,
            state="readonly",
        )
        self.combo_volume.pack(anchor="center")

        # ----- Boutons : colonne 1, alignés avec le bas de la cellule -----
        btns = ctk.CTkFrame(block, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="s", padx=(COMBO_PADDING_X, 0), pady=(0, 0))

        self._btn(btns, "Rafraîchir", self.refresh_volumes, small=True).pack(side="left", padx=BTN_SPACING)
        self._btn(btns, "Analyser", self.analyser, small=True).pack(side="left", padx=BTN_SPACING)

    # ------------------------------------------------------------------
    # Rafraîchissement de la liste des volumes
    # ------------------------------------------------------------------
    def refresh_volumes(self):
        self.volumes = list_volumes()

        if not self.volumes:
            self.combo_volume.configure(values=["Aucun volume détecté"])
            self.combo_volume.set("Aucun volume détecté")
            return

        labels = [f"{vol.name}  ({format_size(size)})" for vol, size in self.volumes]
        self.combo_volume.configure(values=labels)
        self.combo_volume.set(labels[0])

    # ------------------------------------------------------------------
    # Action : Analyser (placeholder pour l'instant)
    # ------------------------------------------------------------------
    def analyser(self):
        selected = self.combo_volume.get()
        print(f"[Analyser] Volume sélectionné : {selected}")
        print("[Analyser] Fonctionnalité à venir à l'étape 4.")

    # ------------------------------------------------------------------
    # Style bouton commun
    # ------------------------------------------------------------------
    def _btn(self, parent, text, command, small=False):
        if small:
            w, h, f = BTN_SMALL_W, BTN_SMALL_H, 12
        else:
            w, h, f = BTN_W, BTN_H, 13
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=(FONT_MAIN, f, "bold"),
            fg_color="transparent",
            border_color=CYAN_BRIGHT,
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