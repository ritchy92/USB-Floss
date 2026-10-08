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

- .DS_Store — cache d'affichage du Finder
- ._* — métadonnées AppleDouble attachées à chaque fichier
- .Spotlight-V100/ — index de recherche Spotlight
- .Trashes/ — corbeille macOS
- .fseventsd/ — journal du système de fichiers

Ces fichiers ne servent à rien sous Windows ou Linux. Ils encombrent la
clé, polluent les listes de fichiers, et parfois empêchent une copie
propre.

## Utilisation

Aperçu (ne supprime rien) :

    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE

Nettoyage avec confirmation :

    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE --delete

Nettoyage sans confirmation :

    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE --delete --yes

## Prérequis

Python 3.10 ou supérieur. Aucune dépendance externe.

## Comment retrouver le chemin de la clé

Sur macOS, les clés sont montées dans /Volumes/. Pour voir la liste :

    ls /Volumes

Sur Windows, le chemin ressemble à D:\ ou E:\.

Sur Linux, /media/utilisateur/NOM_DE_LA_CLE ou /mnt/.

## Notes

- macOS recrée automatiquement .Spotlight-V100 et .fseventsd quand la
  clé est rebranchée sur un Mac. Il est donc conseillé de relancer
  USBFloss juste avant de donner la clé à quelqu'un qui utilise Windows.
- Les fichiers supprimés ne sont pas mis à la corbeille : la suppression
  est définitive. Les fichiers concernés n'ayant aucune valeur (ce sont
  des caches), il n'y a pas de risque de perte de données.

## Licence

MIT — voir le fichier LICENSE.