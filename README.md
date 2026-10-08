# USBFloss

Un petit utilitaire qui nettoie les fichiers inutiles créés par macOS
sur une clé USB ou un disque externe.

Le nom vient du « fil dentaire » (dental floss) : l'outil nettoie les
recoins invisibles de la clé, là où l'utilisateur normal ne regarde pas.
Et « FLOSS » veut aussi dire Free/Libre and Open Source Software — ce
projet l'est.

## Le problème

Quand on branche une clé USB sur un Mac, macOS y laisse des fichiers
cachés invisibles :

- `.DS_Store` — cache d'affichage du Finder
- `._*` — métadonnées AppleDouble attachées à chaque fichier
- `.Spotlight-V100/` — index de recherche Spotlight
- `.Trashes/` — corbeille macOS
- `.fseventsd/` — journal du système de fichiers

Ces fichiers ne servent à rien sous Windows ou Linux. Ils encombrent la
clé, polluent les listes de fichiers, et parfois empêchent une copie
propre.

## Utilisation

### Aperçu (ne supprime rien)

```bash
python3 usbfloss.py /Volumes/NOM_DE_LA_CLE