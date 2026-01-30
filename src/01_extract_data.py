"""
Script 01: Extraction des données Excel → CSV

Objectif:
    Extraire les données du fichier Excel (DataAnalyseModelPredictif-15_08_23.xlsx)
    et les sauvegarder en fichiers CSV pour traitement ultérieur.

Input:
    data/raw/DataAnalyseModelPredictif-15_08_23.xlsx

Output:
    data/processed/historical_draws.csv  (Tous les tirages EuroMillions)
    data/processed/my_games.csv          (Les 133 jeux joués)
    data/processed/metadata.json         (Métadonnées du dataset)

Usage:
    python src/01_extract_data.py
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import sys


def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    print("✅ Répertoires créés/vérifiés")


def load_excel_file(filepath: str) -> pd.ExcelFile:
    """
    Charge le fichier Excel.

    Args:
        filepath: Chemin vers le fichier Excel

    Returns:
        Objet ExcelFile pandas
    """
    if not os.path.exists(filepath):
        print(f"❌ ERREUR: Fichier non trouvé: {filepath}")
        print("\n📋 Instructions:")
        print("1. Placer le fichier DataAnalyseModelPredictif-15_08_23.xlsx")
        print("   dans le répertoire data/raw/")
        print("2. Relancer ce script")
        sys.exit(1)

    try:
        excel_file = pd.ExcelFile(filepath)
        print(f"✅ Fichier Excel chargé: {filepath}")
        return excel_file
    except Exception as e:
        print(f"❌ ERREUR lors du chargement: {e}")
        sys.exit(1)


def extract_historical_draws(excel_file: pd.ExcelFile) -> pd.DataFrame:
    """
    Extrait les tirages historiques EuroMillions.

    Recherche l'onglet contenant l'historique des tirages (pattern: "Historique", "Tirages", etc.)

    Args:
        excel_file: Objet ExcelFile

    Returns:
        DataFrame avec colonnes [Date, Draw, B1, B2, B3, B4, B5, E1, E2]
    """
    print("\n🔍 Recherche de l'onglet 'Historique Tirages'...")

    # Pattern matching pour trouver le bon onglet
    possible_names = ['Historique', 'Tirages', 'Historical', 'Draws', 'Data']
    sheet_name = None

    for sheet in excel_file.sheet_names:
        for pattern in possible_names:
            if pattern.lower() in sheet.lower():
                sheet_name = sheet
                break
        if sheet_name:
            break

    if not sheet_name:
        # Si pas trouvé, prendre le premier onglet
        sheet_name = excel_file.sheet_names[0]
        print(f"⚠️  Onglet auto-détecté: {sheet_name}")
    else:
        print(f"✅ Onglet trouvé: {sheet_name}")

    # Charger les données
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Renommer les colonnes si nécessaire (détection automatique)
    # Format attendu: Date, Draw, B1-B5 (boules), E1-E2 (étoiles)
    expected_cols = ['Date', 'Draw', 'B1', 'B2', 'B3', 'B4', 'B5', 'E1', 'E2']

    # Si colonnes déjà correctes
    if all(col in df.columns for col in expected_cols):
        df = df[expected_cols]
    else:
        # Tentative de mapping automatique
        print("⚠️  Colonnes non standard, mapping automatique...")

        # Assumer que les colonnes sont dans l'ordre
        if len(df.columns) >= len(expected_cols):
            df = df.iloc[:, :len(expected_cols)]
            df.columns = expected_cols
        else:
            print("❌ ERREUR: Structure de données non reconnue")
            print(f"Colonnes trouvées: {df.columns.tolist()}")
            sys.exit(1)

    print(f"📊 {len(df)} tirages extraits")
    return df


def extract_my_games(excel_file: pd.ExcelFile) -> pd.DataFrame:
    """
    Extrait les jeux personnels joués (133 jeux).

    Args:
        excel_file: Objet ExcelFile

    Returns:
        DataFrame avec colonnes [Date_Jeu, B1-B5, E1-E2, Rang, Gain_CHF]
    """
    print("\n🔍 Recherche de l'onglet 'Mes Jeux'...")

    # Pattern matching
    possible_names = ['Mes Jeux', 'My Games', 'Jeux', 'Games', 'Played']
    sheet_name = None

    for sheet in excel_file.sheet_names:
        for pattern in possible_names:
            if pattern.lower() in sheet.lower():
                sheet_name = sheet
                break
        if sheet_name:
            break

    if not sheet_name:
        print("⚠️  Onglet 'Mes Jeux' non trouvé, recherche alternative...")
        # Chercher un onglet avec ~133 lignes
        for sheet in excel_file.sheet_names:
            temp_df = pd.read_excel(excel_file, sheet_name=sheet)
            if 100 <= len(temp_df) <= 150:  # Proche de 133
                sheet_name = sheet
                print(f"✅ Onglet auto-détecté (133 lignes): {sheet_name}")
                break

    if not sheet_name:
        print("⚠️  Onglet 'Mes Jeux' non trouvé, création d'un DataFrame vide")
        # Créer un DataFrame vide avec structure attendue
        return pd.DataFrame(columns=['Date_Jeu', 'B1', 'B2', 'B3', 'B4', 'B5', 'E1', 'E2', 'Rang', 'Gain_CHF'])

    # Charger
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Renommer si nécessaire
    expected_cols = ['Date_Jeu', 'B1', 'B2', 'B3', 'B4', 'B5', 'E1', 'E2', 'Rang', 'Gain_CHF']

    if all(col in df.columns for col in expected_cols):
        df = df[expected_cols]
    else:
        # Mapping automatique
        if len(df.columns) >= len(expected_cols):
            df = df.iloc[:, :len(expected_cols)]
            df.columns = expected_cols
        else:
            print("⚠️  Structure non standard, adaptation...")
            # Au minimum: Date, B1-B5, E1-E2
            min_cols = ['Date_Jeu', 'B1', 'B2', 'B3', 'B4', 'B5', 'E1', 'E2']
            if len(df.columns) >= len(min_cols):
                df = df.iloc[:, :len(min_cols)]
                df.columns = min_cols
                df['Rang'] = None
                df['Gain_CHF'] = 0.0

    print(f"🎮 {len(df)} jeux personnels extraits")
    return df


def save_to_csv(df: pd.DataFrame, filepath: str):
    """
    Sauvegarde un DataFrame en CSV.

    Args:
        df: DataFrame à sauvegarder
        filepath: Chemin du fichier CSV
    """
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"💾 Sauvegardé: {filepath}")


def create_metadata(
    historical_draws: pd.DataFrame,
    my_games: pd.DataFrame
) -> dict:
    """
    Crée un fichier de métadonnées JSON.

    Args:
        historical_draws: DataFrame des tirages historiques
        my_games: DataFrame des jeux personnels

    Returns:
        Dictionnaire de métadonnées
    """
    metadata = {
        "extraction_date": pd.Timestamp.now().isoformat(),
        "historical_draws": {
            "count": len(historical_draws),
            "date_range": {
                "start": str(historical_draws['Date'].min()),
                "end": str(historical_draws['Date'].max())
            },
            "columns": historical_draws.columns.tolist()
        },
        "my_games": {
            "count": len(my_games),
            "total_invested_CHF": len(my_games) * 3.50,
            "columns": my_games.columns.tolist()
        }
    }

    return metadata


def main():
    """Pipeline principal d'extraction."""
    print("=" * 60)
    print("📦 EXTRACTION DES DONNÉES EUROMILLIONS")
    print("=" * 60)

    # Étape 1: Créer répertoires
    ensure_directories()

    # Étape 2: Charger Excel
    excel_path = "data/raw/DataAnalyseModelPredictif-15_08_23.xlsx"
    excel_file = load_excel_file(excel_path)

    print(f"\n📋 Onglets disponibles:")
    for i, sheet in enumerate(excel_file.sheet_names, 1):
        print(f"  {i}. {sheet}")

    # Étape 3: Extraire tirages historiques
    historical_draws = extract_historical_draws(excel_file)

    # Étape 4: Extraire mes jeux
    my_games = extract_my_games(excel_file)

    # Étape 5: Sauvegarder en CSV
    print("\n💾 Sauvegarde des fichiers CSV...")
    save_to_csv(historical_draws, "data/processed/historical_draws.csv")
    save_to_csv(my_games, "data/processed/my_games.csv")

    # Étape 6: Créer métadonnées
    metadata = create_metadata(historical_draws, my_games)
    with open("data/processed/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print("💾 Sauvegardé: data/processed/metadata.json")

    # Résumé
    print("\n" + "=" * 60)
    print("✅ EXTRACTION TERMINÉE")
    print("=" * 60)
    print(f"📊 Tirages historiques: {len(historical_draws)}")
    print(f"🎮 Jeux personnels: {len(my_games)}")
    print(f"💰 Investissement total: {len(my_games) * 3.50:.2f} CHF")
    print("\n📂 Fichiers créés:")
    print("  - data/processed/historical_draws.csv")
    print("  - data/processed/my_games.csv")
    print("  - data/processed/metadata.json")
    print("\n➡️  Prochaine étape: python src/02_clean_data.py")


if __name__ == "__main__":
    main()
