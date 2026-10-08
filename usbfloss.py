#!/usr/bin/env python3
"""
USBFloss — Nettoyer les fichiers macOS inutiles sur une clé USB.

Version 0.1 : liste les fichiers parasites, ne supprime rien.
"""

import sys
from pathlib import Path

# Fichiers à détecter (par nom exact)
JUNK_FILES = {
    ".DS_Store",
    ".apdisk",
    ".VolumeIcon.icns",
}

# Dossiers à détecter (par nom exact)
JUNK_DIRS = {
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".TemporaryItems",
    ".DocumentRevisions-V100",
}

# Préfixes de fichiers à détecter (ex : ._monfichier.txt)
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
    found = []
    for path in root.rglob("*"):
        if is_junk(path):
            found.append(path)
    return found


def main():
    if len(sys.argv) != 2:
        print("Usage : python3 usbfloss.py /chemin/vers/la/cle")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()

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
        rel = path.relative_to(root)
        print(f"  [{kind}] {rel}")

    print()
    print("Mode aperçu uniquement — rien n'a été supprimé.")


if __name__ == "__main__":
    main()