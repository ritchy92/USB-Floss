# ============================================================
# USB-Floss — Interface graphique
# © 2026 Richard Cogne — Tous droits réservés
# made by ritchy
# ============================================================

import os
import sys

import customtkinter as ctk
from PIL import Image

from usbfloss import list_volumes, format_size, scan

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Polices selon la plateforme
if sys.platform == "darwin":
    FONT_MAIN = "SF Pro Display"
    FONT_MONO = "Menlo"
elif sys.platform == "win32":
    FONT_MAIN = "Segoe UI"
    FONT_MONO = "Consolas"
else:
    FONT_MAIN = "DejaVu Sans"
    FONT_MONO = "DejaVu Sans Mono"

# Palette
BG_MAIN = "#000000"
BG_CARD = "#0F161C"
BG_ENTRY = "#1A2530"
BG_HEADER = "#14202B"
LOGO_ACCENT = "#3DDFA0"
CYAN = "#00F0FF"
CYAN_DARK = "#00A8B8"
CYAN_BRIGHT = "#3BFCFF"
CYAN_HOVER = "#23A7C8"
TEXT_WHITE = "#FFFFFF"
TEXT_GREY = "#8A9AA9"

# Dimensions des boutons
BTN_W = 100
BTN_H = 34
BTN_SMALL_W = 90
BTN_SMALL_H = 34

# Constante pour la hauteur de la combo
COMBO_HEIGHT = BTN_H

# Padding
COMBO_PADDING_X = 8
LABEL_PADDING_BOTTOM = 4
BTN_SPACING = 4
FRAME_PADDING = 30         # marge uniforme autour des blocs
FRAME_PADDING_BOTTOM = 60   # marge basse (3x la marge standard)

# Chemin du logo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

# ------------------------------------------------------------------
# LOGO
# Espace réservé pour le logo : largeur 140 px, hauteur ~140 px
# (l'image est carrée dans le fichier logo.png, elle s'affiche à 140x140)
# ------------------------------------------------------------------
LOGO_WIDTH = 140

# Largeur de la combo volume
COMBO_W = 200

# Intervalle de scan automatique des volumes (en ms)
VOLUME_CHECK_INTERVAL = 2000


# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------
class USBFlossApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("USB-Floss")
        self.geometry("440x620")
        self.resizable(False, True)
        self.minsize(440, 540)
        self.configure(fg_color=BG_MAIN)

        self._logo_image = None
        self.volumes = []
        self._last_volumes_state = None

        self._build_header()
        self._build_volume_selector()
        self._build_results_area()

        # ----- Zone d'actions (étape 5) -----
        # Rempli plus tard

        # ----- Premier scan des volumes -----
        self._check_volumes()
        self._schedule_volume_check()

    # ------------------------------------------------------------------
    # En-tête (logo)
    # ------------------------------------------------------------------
    def _build_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=FRAME_PADDING, pady=(FRAME_PADDING, 4))

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
    # Sélection du volume
    # ------------------------------------------------------------------
    def _build_volume_selector(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 10))

        block = ctk.CTkFrame(frame, fg_color="transparent")
        block.pack(anchor="center", pady=6)

        block.grid_columnconfigure(0, weight=0)
        block.grid_columnconfigure(1, weight=0)

        # ----- Cellule : label + combo -----
        cell = ctk.CTkFrame(block, fg_color="transparent")
        cell.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            cell,
            text="Volume à nettoyer",
            font=(FONT_MAIN, 12),           # typo réduite (avant : 14)
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

        # ----- Bouton Nettoyer (fonctionnel à l'étape 5) -----
        btns = ctk.CTkFrame(block, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="s", padx=(COMBO_PADDING_X, 0))

        self._btn(btns, "Nettoyer", self.run_clean, small=True).pack(side="left", padx=BTN_SPACING)

    # ------------------------------------------------------------------
    # Zone de résultats (frame simple, pas scrollable)
    # ------------------------------------------------------------------
    def _build_results_area(self):
        # Le CTkScrollableFrame affiche toujours sa barre. On utilise donc
        # un CTkFrame classique : si la liste dépasse, on tronque proprement
        # (les fichiers parasites sont rares sur une clé de moins de 256 Go).
        self.results_frame = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=10,
            border_color=CYAN_DARK,
            border_width=1,
        )
        self.results_frame.pack(
            fill="both",
            expand=True,
            padx=FRAME_PADDING,
            pady=(10, FRAME_PADDING_BOTTOM),
        )

        # Message d'invite
        self._show_message("Sélectionne un volume puis clique sur Analyser.", italic=True)

    # ------------------------------------------------------------------
    # Scan périodique des volumes
    # ------------------------------------------------------------------
    def _schedule_volume_check(self):
        self._check_volumes()
        self.after(VOLUME_CHECK_INTERVAL, self._schedule_volume_check)

    def _check_volumes(self):
        new_volumes = list_volumes()

        new_state = tuple((str(v), s) for v, s in new_volumes)
        if new_state == self._last_volumes_state:
            return

        self._last_volumes_state = new_state
        self.volumes = new_volumes

        self._clear_results()
        self._set_results_border(active=False)

        if not new_volumes:
            self.combo_volume.configure(values=["Aucun volume détecté"])
            self.combo_volume.set("Aucun volume détecté")
            self._show_message("Aucun volume détecté.", italic=True)
            return

        labels = [f"{vol.name}  ({format_size(size)})" for vol, size in new_volumes]
        self.combo_volume.configure(values=labels)

        current = self.combo_volume.get()
        if current not in labels:
            self.combo_volume.set(labels[0])

        # ---- Analyse AUTOMATIQUE du volume sélectionné ----
        self._analyse_current_volume()

    # ------------------------------------------------------------------
    # Analyse du volume courant
    # ------------------------------------------------------------------
    def _analyse_current_volume(self):
        selected = self.combo_volume.get()

        if not selected or selected == "Aucun volume détecté":
            self._clear_results()
            self._show_message("Aucun volume à analyser.", italic=True)
            self._set_results_border(active=False)
            return

        vol_path = None
        for vol, size in self.volumes:
            label = f"{vol.name}  ({format_size(size)})"
            if label == selected:
                vol_path = vol
                break

        if vol_path is None:
            self._clear_results()
            self._show_message("Volume introuvable.", italic=True)
            self._set_results_border(active=False)
            return

        junk = scan(vol_path)
        self._clear_results()

        if not junk:
            self._show_message("Aucun fichier parasite trouvé. La clé est propre.", italic=True)
            self._set_results_border(active=False)
            return

        self._show_message(f"{len(junk)} élément(s) trouvé(s) :", bold=True)
        for path in junk:
            kind = "dossier" if path.is_dir() else "fichier"
            rel = path.relative_to(vol_path)
            self._add_result_line(f"[{kind}] {rel}")

        self._set_results_border(active=True)

    # ------------------------------------------------------------------
    # Action : Nettoyer (placeholder pour l'étape 5)
    # ------------------------------------------------------------------
    def run_clean(self):
        print("[Nettoyer] Fonctionnalité à venir à l'étape 5.")

    # ------------------------------------------------------------------
    # Helpers affichage
    # ------------------------------------------------------------------
    def _clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def _show_message(self, text, italic=False, bold=False):
        if italic:
            font_style = (FONT_MAIN, 12, "italic")
            color = "#3DDFA0"
        elif bold:
            font_style = (FONT_MAIN, 12, "bold")
            color = TEXT_WHITE
        else:
            font_style = (FONT_MAIN, 12)
            color = TEXT_WHITE

        lbl = ctk.CTkLabel(
            self.results_frame,
            text=text,
            font=font_style,
            text_color=color,
            anchor="w",
        )
        lbl.pack(fill="x", padx=8, pady=(4, 4))

    def _add_result_line(self, text):
        lbl = ctk.CTkLabel(
            self.results_frame,
            text=text,
            font=(FONT_MONO, 11),
            text_color=TEXT_WHITE,
            anchor="w",
        )
        lbl.pack(fill="x", padx=8, pady=1)

    def _set_results_border(self, active):
        color = CYAN_BRIGHT if active else CYAN_DARK
        self.results_frame.configure(border_color=color)

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