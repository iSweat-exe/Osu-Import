# Osu! Importer

Osu! Importer est un outil polyvalent conçu pour simplifier l'importation en masse de beatmaps osu! à partir de fichiers `.osz` ou d'archives `.zip` contenant ces fichiers. Il est disponible en deux versions : une interface graphique (GUI) conviviale et une interface en ligne de commande (CLI) pour les utilisateurs avancés ou l'automatisation.

## Fonctionnalités

- **Importation par lots :** Importez plusieurs fichiers `.osz` simultanément.
- **Prise en charge des archives ZIP :** Extrait et importe les fichiers `.osz` directement à partir d'archives `.zip`.
- **Détection automatique :** Détecte et attend la fin des importations osu! en cours avant de lancer de nouvelles importations.
- **Interface conviviale (GUI) :** Une interface graphique intuitive pour une utilisation facile.
- **Interface en ligne de commande (CLI) :** Pour les utilisateurs préférant le terminal ou l'intégration dans des scripts.
- **Gestion des erreurs :** Gère les erreurs courantes lors de l'importation.

## Prérequis

- Python 3.x
- osu! installé sur votre système

## Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/iSweat/Osu-Importer.git
    cd Osu-Importer
    ```

2.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

### Version GUI (Interface Graphique)

Pour lancer l'application GUI, exécutez :

```bash
python src/app.py
```

L'interface graphique vous permettra de sélectionner un dossier ou un fichier `.zip` contenant vos beatmaps `.osz` et de lancer l'importation.

### Version CLI (Ligne de Commande)

Pour utiliser la version CLI, exécutez le script `import_osz.py` avec le chemin vers votre dossier ou fichier `.zip`.

```bash
python src/import_osz.py <chemin_vers_dossier_ou_zip> [--batch-size <taille_du_lot>]
```

-   `<chemin_vers_dossier_ou_zip>` : Le chemin absolu ou relatif vers un dossier contenant des fichiers `.osz` ou vers une archive `.zip` contenant des fichiers `.osz`.
-   `--batch-size <taille_du_lot>` (optionnel) : Le nombre de fichiers `.osz` à importer simultanément. La valeur par défaut est 5.

**Exemples :**

Importation d'un dossier :
```bash
python src/import_osz.py "C:\Users\VotreNom\Downloads\OsuBeatmaps"
```

Importation d'une archive ZIP avec une taille de lot personnalisée :
```bash
python src/import_osz.py "C:\Users\VotreNom\Downloads\MyBeatmaps.zip" --batch-size 10
```

## Dépendances

Le projet utilise les bibliothèques Python suivantes :

-   `psutil`
-   `PySide6` (pour la version GUI)

Ces dépendances sont listées dans `requirements.txt`.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, n'hésitez pas à :

1.  Fork le dépôt.
2.  Créer une nouvelle branche (`git checkout -b feature/YourFeature`).
3.  Faire vos modifications.
4.  Commiter vos changements (`git commit -m 'Add some Feature'`).
5.  Pusher vers la branche (`git push origin feature/YourFeature`).
6.  Ouvrir une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Ce projet a été créé par iSweat.

-   GitHub : [iSweat](https://github.com/iSweat)
-   Osu! : [iSweat](https://osu.ppy.sh/users/35767175)
-   Discord : isweatmc

N'hésitez pas à me contacter pour toute question ou suggestion. Si vous appréciez ce projet, un `star` sur le dépôt GitHub serait très apprécié !
