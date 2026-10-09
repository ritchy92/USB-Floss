# ============================================================
# USB-Floss — Interface graphique
# © 2026 Richard Cogne — Tous droits réservés
# made by ritchy
# ============================================================

import os
import subprocess
import sys

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from usbfloss import list_volumes, format_size, scan, delete

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
TEXT_DIM = "#5A6A78"
BTN_DISABLED = "#3A4A55"

# Dimensions des boutons
BTN_W = 100
BTN_H = 34
BTN_SMALL_W = 90
BTN_SMALL_H = 34

COMBO_HEIGHT = BTN_H

# Padding
COMBO_PADDING_X = 8
LABEL_PADDING_BOTTOM = 4
BTN_SPACING = 4
FRAME_PADDING = 30
FRAME_PADDING_BOTTOM = 60

# Chemin du logo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

LOGO_WIDTH = 480
COMBO_W = 200
VOLUME_CHECK_INTERVAL = 2000

# Dossiers protégés par macOS : détectés mais non supprimables
PROTECTED_NAMES = {
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".DocumentRevisions-V100",
}

# Version affichée dans la fenêtre d'aide
APP_VERSION = "0.5"


# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------
class USBFlossApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("USB-Floss")
        self.geometry("480x620")
        self.resizable(False, True)
        self.minsize(480, 540)
        self.configure(fg_color=BG_MAIN)

        self._logo_image = None
        self.volumes = []
        self._last_volumes_state = None
        self.current_junk = []
        self.current_volume = None

        self._build_header()
        self._build_volume_selector()
        self._build_actions()
        self._build_results_area()

        # Premier scan
        self._check_volumes()
        self._schedule_volume_check()

    # ------------------------------------------------------------------
    # En-tête (logo)
    # ------------------------------------------------------------------
    def _build_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=10, pady=(FRAME_PADDING, 4))

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

        cell = ctk.CTkFrame(block, fg_color="transparent")
        cell.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            cell,
            text="Volume à nettoyer",
            font=(FONT_MAIN, 12),
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

    # ------------------------------------------------------------------
    # Zone de résultats
    # ------------------------------------------------------------------
    def _build_results_area(self):
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
            pady=(10, 10),
        )

        self._show_message("En attente d'un volume...", italic=True)

    # ------------------------------------------------------------------
    # Zone d'actions
    # ------------------------------------------------------------------
    def _build_actions(self):
        # ---- Ligne 1 (la plus basse) : bouton « ? » en bas à droite ----
        help_frame = ctk.CTkFrame(self, fg_color="transparent")
        help_frame.pack(
            fill="x",
            side="bottom",
            padx=FRAME_PADDING,
            pady=(0, 20),
        )

        self.btn_help = ctk.CTkButton(
            help_frame,
            text="?",
            font=(FONT_MAIN, 13, "bold"),
            width=24,
            height=24,
            corner_radius=12,
            fg_color="transparent",
            border_width=0,
            text_color=CYAN,
            hover_color=CYAN_HOVER,
            command=self._open_help,
        )
        self.btn_help.pack(side="right")

        # ---- Ligne 2 (au-dessus) : Nettoyer + Éjecter ----
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(
            fill="x",
            side="bottom",
            padx=FRAME_PADDING,
            pady=(0, 20),
        )

        self.btn_clean = self._btn(frame, "Nettoyer", self.run_clean, small=True)
        self.btn_clean.configure(state="disabled", border_color=BTN_DISABLED)
        self.btn_clean.pack(side="left")

        self.var_eject = ctk.BooleanVar(value=False)
        self.chk_eject = ctk.CTkCheckBox(
            frame,
            text="Éjecter après nettoyage",
            variable=self.var_eject,
            font=(FONT_MAIN, 12),
            text_color=TEXT_WHITE,
            fg_color=CYAN_DARK,
            hover_color=CYAN,
            border_color=CYAN_BRIGHT,
            border_width=2,
            corner_radius=6,
            checkbox_width=20,
            checkbox_height=20,
        )
        self.chk_eject.pack(side="right")

    # ------------------------------------------------------------------
    # Scan périodique
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
        self._disable_clean_button()

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
            self._disable_clean_button()
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
            self._disable_clean_button()
            return

        junk = scan(vol_path)
        self._clear_results()

        self.current_volume = vol_path

        to_delete = [p for p in junk if not self._is_protected(p)]
        self.current_junk = to_delete

        if not junk:
            self._show_message("Aucun fichier parasite trouvé. La clé est propre.", italic=True)
            self._set_results_border(active=False)
            self._disable_clean_button()
            return

        self._show_message(f"{len(junk)} élément(s) trouvé(s) :", bold=True)
        for path in junk:
            rel = str(path.relative_to(vol_path))
            if self._is_protected(path):
                self._add_result_line(f"{rel}    (ignoré)", ignored=True)
            else:
                self._add_result_line(rel)

        self._set_results_border(active=True)

        if to_delete:
            self._enable_clean_button()
        else:
            self._disable_clean_button()

    def _is_protected(self, path):
        return path.name in PROTECTED_NAMES

    # ------------------------------------------------------------------
    # Action : Nettoyer
    # ------------------------------------------------------------------
    def run_clean(self):
        if not self.current_junk or self.current_volume is None:
            return

        n = len(self.current_junk)
        vol_name = self.current_volume.name

        reponse = messagebox.askyesno(
            "USB-Floss",
            f"Supprimer {n} élément(s) sur {vol_name} ?",
        )
        if not reponse:
            return

        ok, ko = delete(self.current_junk, self.current_volume)

        if ko == 0:
            messagebox.showinfo("USB-Floss", f"{ok} élément(s) supprimé(s).")
        else:
            messagebox.showwarning(
                "USB-Floss",
                f"{ok} supprimé(s), {ko} échec(s).\n"
                "Certains fichiers n'ont pas pu être supprimés.",
            )

        if self.var_eject.get():
            self._eject_volume(self.current_volume)

        self._last_volumes_state = None
        self._check_volumes()

    # ------------------------------------------------------------------
    # Éjection
    # ------------------------------------------------------------------
    def _eject_volume(self, volume_path):
        try:
            if sys.platform == "darwin":
                subprocess.run(
                    ["diskutil", "eject", str(volume_path)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:
            print(f"Erreur éjection : {e}")

    # ------------------------------------------------------------------
    # Fenêtre d'aide
    # ------------------------------------------------------------------
    def _open_help(self):
        popup = ctk.CTkToplevel(self)
        popup.title("À propos — USB-Floss")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        popup.configure(fg_color=BG_MAIN)

        self.update_idletasks()
        w_popup, h_popup = 460, 520
        x = self.winfo_x() + (self.winfo_width() - w_popup) // 2
        y = self.winfo_y() + (self.winfo_height() - h_popup) // 2
        popup.geometry(f"{w_popup}x{h_popup}+{max(x, 0)}+{max(y, 0)}")

        frame = ctk.CTkScrollableFrame(
            popup,
            fg_color=BG_CARD,
            corner_radius=10,
            scrollbar_button_color=CYAN_DARK,
            scrollbar_button_hover_color=CYAN,
        )
        frame.pack(fill="both", expand=True, padx=15, pady=(15, 8))

        contenu = [
            ("title", "USB-Floss"),
            ("text", f"Version {APP_VERSION}"),
            ("space", ""),
            ("text", "Nettoie une clé USB des fichiers inutiles"),
            ("text", "créés par macOS, pour la donner à quelqu'un"),
            ("text", "qui utilise Windows."),
            ("space", ""),
            ("title2", "Comment l'utiliser"),
            ("bullet", "1. Branche une clé USB."),
            ("bullet", "2. Elle apparaît automatiquement dans la liste."),
            ("bullet", "3. L'analyse se lance toute seule."),
            ("bullet", "4. Clique sur Nettoyer pour supprimer les fichiers."),
            ("space", ""),
            ("title2", "Fichiers ignorés"),
            ("text", "Certains dossiers protégés par macOS (comme"),
            ("text", ".Spotlight-V100 et .fseventsd) ne peuvent pas être"),
            ("text", "supprimés. Ils sont marqués « (ignoré) » et laissés"),
            ("text", "en place. C'est normal et sans danger."),
            ("space", ""),
            ("title2", "Limite de taille"),
            ("text", "Seules les clés USB et disques externes de moins"),
            ("text", "de 256 Go sont proposés automatiquement."),
            ("space", ""),
            ("sep", ""),
            ("text", "Richard Cogne"),
            ("text", "© 2026 — Licence MIT"),
            ("space", ""),
            ("code", "github.com/ritchy92/USB-Floss"),
        ]

        for kind, txt in contenu:
            if kind == "space":
                ctk.CTkLabel(frame, text="", height=6).pack()
            elif kind == "title":
                ctk.CTkLabel(
                    frame, text=txt,
                    font=(FONT_MAIN, 18, "bold"),
                    text_color=CYAN, anchor="w",
                ).pack(fill="x", pady=(4, 2))
            elif kind == "title2":
                ctk.CTkLabel(
                    frame, text=txt,
                    font=(FONT_MAIN, 14, "bold"),
                    text_color=LOGO_ACCENT, anchor="w",
                ).pack(fill="x", pady=(8, 2))
            elif kind == "bullet":
                ctk.CTkLabel(
                    frame, text="    " + txt,
                    font=(FONT_MAIN, 12),
                    text_color=TEXT_WHITE, anchor="w", justify="left",
                ).pack(fill="x")
            elif kind == "code":
                ctk.CTkLabel(
                    frame, text=txt,
                    font=(FONT_MONO, 11),
                    text_color="#7FE0E8", anchor="w",
                ).pack(fill="x", padx=(8, 0))
            elif kind == "sep":
                ctk.CTkFrame(frame, height=1, fg_color="#2A3A48").pack(fill="x", pady=8)
            else:
                ctk.CTkLabel(
                    frame, text=txt,
                    font=(FONT_MAIN, 12),
                    text_color=TEXT_WHITE, anchor="w", justify="left",
                ).pack(fill="x")

        ctk.CTkButton(
            popup,
            text="Fermer",
            font=(FONT_MAIN, 13, "bold"),
            width=140,
            height=36,
            corner_radius=18,
            fg_color="transparent",
            border_color=CYAN_BRIGHT,
            border_width=1,
            text_color=TEXT_WHITE,
            hover_color=CYAN_HOVER,
            command=popup.destroy,
        ).pack(pady=(0, 15))

    # ------------------------------------------------------------------
    # Helpers bouton
    # ------------------------------------------------------------------
    def _enable_clean_button(self):
        self.btn_clean.configure(state="normal", border_color=CYAN_BRIGHT)

    def _disable_clean_button(self):
        self.btn_clean.configure(state="disabled", border_color=BTN_DISABLED)

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

    def _add_result_line(self, text, ignored=False):
        color = TEXT_DIM if ignored else TEXT_WHITE
        style = "italic" if ignored else "normal"
        lbl = ctk.CTkLabel(
            self.results_frame,
            text=text,
            font=(FONT_MONO, 11, style),
            text_color=color,
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