#!/usr/bin/env python3
"""
USBFloss — Nettoyer les fichiers macOS inutiles sur une clé USB.

Version 0.2 : suppression réelle avec confirmation simple.
"""

import argparse
import shutil
import sys
from pathlib import Path

JUNK_FILES = {
    ".DS_Store",
    ".apdisk",
    ".VolumeIcon.icns",
}

JUNK_DIRS = {
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".TemporaryItems",
    ".DocumentRevisions-V100",
}

JUNK_PREFIXES = (
    "._",
)


def is_junk(path: Path) -> bool:
    """Renvoie True si le chemin correspond à un fichier parasite macOS."""
    name = path.name
    if name in JUNK_FILES:
        return True
    if path.is_dir() and name in JUNK_DIRS:
        return True
    if name.startswith(JUNK_PREFIXES):
        return True
    return False


def scan(root: Path) -> list[Path]:
    """Parcourt récursivement `root` et renvoie la liste des fichiers parasites."""
    return [p for p in root.rglob("*") if is_junk(p)]


def delete(paths: list[Path], root: Path) -> tuple[int, int]:
    """Supprime les chemins donnés. Renvoie (succès, échecs)."""
    ok = 0
    ko = 0
    for path in paths:
        rel = path.relative_to(root)
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  supprimé : {rel}")
            ok += 1
        except OSError as e:
            print(f"  ÉCHEC    : {rel} ({e})")
            ko += 1
    return ok, ko


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nettoie les fichiers macOS inutiles sur une clé USB.",
    )
    parser.add_argument("chemin", type=Path, help="Dossier à nettoyer (ex : /Volumes/MACLE)")
    parser.add_argument("--delete", action="store_true",
                        help="Supprime réellement les fichiers (sinon : aperçu).")
    parser.add_argument("--yes", action="store_true",
                        help="Ne pas demander de confirmation.")
    return parser.parse_args()


def main():
    args = parse_args()
    root = args.chemin.resolve()

    if not root.is_dir():
        print(f"Erreur : {root} n'est pas un dossier valide.")
        sys.exit(1)

    print(f"Analyse de : {root}")
    print()

    junk = scan(root)

    if not junk:
        print("Aucun fichier parasite trouvé. La clé est propre.")
        return

    print(f"{len(junk)} élément(s) parasite(s) trouvé(s) :\n")
    for path in junk:
        kind = "dossier" if path.is_dir() else "fichier"
        print(f"  [{kind}] {path.relative_to(root)}")

    print()

    if not args.delete:
        print("Mode aperçu — rien n'a été supprimé.")
        print("Pour supprimer, relance avec --delete")
        return

    if not args.yes:
        answer = input(f"Nettoyer {root.name} ? [o/N] ").strip().lower()
        if answer not in ("o", "oui", "y", "yes"):
            print("Annulé.")
            return

    print()
    ok, ko = delete(junk, root)
    print()
    print(f"Terminé : {ok} supprimé(s), {ko} échec(s).")


if __name__ == "__main__":
    main()