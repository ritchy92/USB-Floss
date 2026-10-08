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

### Mode interactif (le plus simple)

    python3 usbfloss.py

Le script liste les volumes éligibles et te demande lequel nettoyer :

    Volumes détectés :
      1. DRIVE64            (32 Go)

    Quel volume nettoyer ? [1-1]

Aucune commande à retenir, aucun chemin à taper.

### Mode direct (chemin précis)

    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE

Utile si tu connais déjà le chemin de ta clé, ou si tu veux cibler
un volume qui n'est pas proposé par le mode interactif (voir plus bas).

### Aperçu (ne supprime rien)

Par défaut, toutes les commandes ci-dessus sont en mode aperçu :
elles affichent la liste des fichiers parasites trouvés, mais ne
suppriment rien.

### Nettoyage avec confirmation

Ajoute --delete pour supprimer réellement :

    python3 usbfloss.py --delete
    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE --delete

Le script affiche la liste, puis demande confirmation avant de
supprimer.

### Nettoyage sans confirmation

    python3 usbfloss.py /Volumes/NOM_DE_LA_CLE --delete --yes

Pour automatiser (scripts, cron, etc.).

## Volumes proposés en mode interactif

Le mode interactif ne propose pas tous les volumes montés. Sont
automatiquement exclus :

- Le disque de démarrage
- Les volumes Time Machine (détectés via leur marqueur système)
- Les volumes système (com.apple.TimeMachine.localsnapshots)
- Les volumes de plus de 256 Go

Cette limite existe parce qu'USBFloss est prévu pour les clés USB
et les petits disques externes qui servent de navette entre Mac et
PC. Un gros disque de stockage (1 To ou plus) n'a pas vocation à
être nettoyé de cette façon : il est utilisé différemment, et le
risque de manipuler un volume contenant des données importantes
n'en vaut pas la peine.

Pour cibler malgré tout un gros volume, utilise le mode direct en
indiquant son chemin :

    python3 usbfloss.py /Volumes/NOM_DU_GROS_DISQUE

Le script fera le scan normalement, sans filtre de taille. Il restera
en mode aperçu tant que tu n'ajoutes pas --delete.

## Prérequis

Python 3.10 ou supérieur. Aucune dépendance externe.

## Comment retrouver le chemin d'une clé

Sur macOS, les clés sont montées dans /Volumes/. Pour voir la liste :

    ls /Volumes

Sur Windows, le chemin ressemble à D:\ ou E:\.

Sur Linux, /media/utilisateur/NOM_DE_LA_CLE ou /mnt/.

## Notes

- macOS recrée automatiquement .Spotlight-V100 et .fseventsd quand la
  clé est rebranchée sur un Mac. Il est donc conseillé de relancer
  USBFloss juste avant de donner la clé à quelqu'un qui utilise
  Windows.
- Les fichiers supprimés ne sont pas mis à la corbeille : la suppression
  est définitive. Les fichiers concernés n'ayant aucune valeur (ce sont
  des caches), il n'y a pas de risque de perte de données.

## Licence

MIT — voir le fichier LICENSE.