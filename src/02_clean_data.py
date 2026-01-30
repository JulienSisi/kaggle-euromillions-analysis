"""
Script 02: Nettoyage et validation des données

Objectif:
    Nettoyer les données extraites, valider l'intégrité, et créer des features dérivées.

Input:
    data/processed/historical_draws.csv
    data/processed/my_games.csv

Output:
    data/processed/clean_draws.csv
    data/processed/clean_my_games.csv
    data/processed/validation_report.txt

Usage:
    python src/02_clean_data.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path


def load_data():
    """
    Charge les données extraites.

    Returns:
        Tuple (historical_draws, my_games)
    """
    try:
        historical = pd.read_csv("data/processed/historical_draws.csv")
        my_games = pd.read_csv("data/processed/my_games.csv")
        print("✅ Données chargées")
        return historical, my_games
    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        print("\n➡️  Exécuter d'abord: python src/01_extract_data.py")
        sys.exit(1)


def validate_historical_draws(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valide l'intégrité des tirages historiques.

    Vérifications:
    - Ranges des boules [1-50] et étoiles [1-12]
    - Pas de doublons
    - Pas de valeurs manquantes
    - Chronologie cohérente

    Args:
        df: DataFrame des tirages historiques

    Returns:
        DataFrame nettoyé
    """
    print("\n🔍 Validation des tirages historiques...")

    initial_count = len(df)

    # 1. Convertir Date en datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # 2. Supprimer lignes avec valeurs manquantes
    df = df.dropna()
    if len(df) < initial_count:
        print(f"⚠️  {initial_count - len(df)} lignes avec NaN supprimées")

    # 3. Valider ranges
    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    star_cols = ['E1', 'E2']

    for col in ball_cols:
        invalid_balls = ~df[col].between(1, 50)
        if invalid_balls.any():
            print(f"⚠️  {invalid_balls.sum()} valeurs invalides dans {col} supprimées")
            df = df[~invalid_balls]

    for col in star_cols:
        invalid_stars = ~df[col].between(1, 12)
        if invalid_stars.any():
            print(f"⚠️  {invalid_stars.sum()} valeurs invalides dans {col} supprimées")
            df = df[~invalid_stars]

    # 4. Vérifier unicité des tirages (sur Draw si existe)
    if 'Draw' in df.columns:
        duplicates = df['Draw'].duplicated()
        if duplicates.any():
            print(f"⚠️  {duplicates.sum()} tirages dupliqués supprimés")
            df = df[~duplicates]
    else:
        # Créer colonne Draw
        df = df.sort_values('Date').reset_index(drop=True)
        df.insert(1, 'Draw', range(1, len(df) + 1))

    # 5. Trier par date
    df = df.sort_values('Date').reset_index(drop=True)

    print(f"✅ Validation OK: {len(df)} tirages valides")
    return df


def validate_my_games(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valide les jeux personnels.

    Args:
        df: DataFrame des jeux personnels

    Returns:
        DataFrame nettoyé
    """
    print("\n🔍 Validation des jeux personnels...")

    initial_count = len(df)

    # 1. Convertir Date
    if 'Date_Jeu' in df.columns:
        df['Date_Jeu'] = pd.to_datetime(df['Date_Jeu'], errors='coerce')

    # 2. Valider boules/étoiles
    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    star_cols = ['E1', 'E2']

    for col in ball_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            invalid = ~df[col].between(1, 50)
            if invalid.any():
                print(f"⚠️  {invalid.sum()} valeurs invalides dans {col}")

    for col in star_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            invalid = ~df[col].between(1, 12)
            if invalid.any():
                print(f"⚠️  {invalid.sum()} valeurs invalides dans {col}")

    # 3. Valider Rang (1-13 ou NaN)
    if 'Rang' in df.columns:
        df['Rang'] = pd.to_numeric(df['Rang'], errors='coerce')
        invalid_ranks = ~(df['Rang'].isna() | df['Rang'].between(1, 13))
        if invalid_ranks.any():
            print(f"⚠️  {invalid_ranks.sum()} rangs invalides")

    # 4. Valider Gain_CHF (>= 0)
    if 'Gain_CHF' in df.columns:
        df['Gain_CHF'] = pd.to_numeric(df['Gain_CHF'], errors='coerce').fillna(0)
        invalid_gains = df['Gain_CHF'] < 0
        if invalid_gains.any():
            print(f"⚠️  {invalid_gains.sum()} gains négatifs corrigés à 0")
            df.loc[invalid_gains, 'Gain_CHF'] = 0

    # Supprimer lignes avec trop de NaN
    df = df.dropna(subset=ball_cols[:3])  # Au moins B1, B2, B3 valides

    print(f"✅ Validation OK: {len(df)} jeux valides")
    return df


def create_features_draws(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée des features dérivées pour les tirages historiques.

    Features:
    - Sum_Balls: Somme des 5 boules
    - Even_Count: Nombre de boules paires
    - Max_Gap: Écart maximal entre boules consécutives
    - Has_13: Présence du numéro 13
    - Div_3_Count: Nombre de multiples de 3
    - Div_5_Count: Nombre de multiples de 5

    Args:
        df: DataFrame des tirages

    Returns:
        DataFrame enrichi
    """
    print("\n🔧 Création de features (tirages)...")

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']

    # Somme
    df['Sum_Balls'] = df[ball_cols].sum(axis=1)

    # Parité
    df['Even_Count'] = df[ball_cols].apply(
        lambda row: sum(x % 2 == 0 for x in row), axis=1
    )

    # Écart maximal
    def max_gap(row):
        sorted_balls = sorted(row[ball_cols])
        gaps = [sorted_balls[i+1] - sorted_balls[i] for i in range(4)]
        return max(gaps)

    df['Max_Gap'] = df.apply(max_gap, axis=1)

    # Présence du 13
    df['Has_13'] = df[ball_cols].apply(
        lambda row: 13 in row.values, axis=1
    )

    # Divisibilité
    df['Div_3_Count'] = df[ball_cols].apply(
        lambda row: sum(x % 3 == 0 for x in row), axis=1
    )

    df['Div_5_Count'] = df[ball_cols].apply(
        lambda row: sum(x % 5 == 0 for x in row), axis=1
    )

    print(f"✅ {df.shape[1] - len(ball_cols) - 3} features créées")
    return df


def create_features_my_games(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée des features pour mes jeux.

    Args:
        df: DataFrame des jeux personnels

    Returns:
        DataFrame enrichi
    """
    print("\n🔧 Création de features (mes jeux)...")

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']

    # Somme
    df['Sum_Balls'] = df[ball_cols].sum(axis=1)

    # Parité
    df['Even_Count'] = df[ball_cols].apply(
        lambda row: sum(x % 2 == 0 for x in row), axis=1
    )

    # Présence du 13
    df['Has_13'] = df[ball_cols].apply(
        lambda row: 13 in row.values, axis=1
    )

    # ROI cumulé
    if 'Gain_CHF' in df.columns:
        df['Cumulative_Invested'] = (df.index + 1) * 3.50
        df['Cumulative_Won'] = df['Gain_CHF'].cumsum()
        df['Cumulative_ROI'] = (
            (df['Cumulative_Won'] - df['Cumulative_Invested']) /
            df['Cumulative_Invested'] * 100
        )

    print(f"✅ Features créées")
    return df


def generate_validation_report(
    historical: pd.DataFrame,
    my_games: pd.DataFrame
) -> str:
    """
    Génère un rapport de validation.

    Args:
        historical: DataFrame des tirages historiques
        my_games: DataFrame des jeux personnels

    Returns:
        Texte du rapport
    """
    report = []
    report.append("=" * 60)
    report.append("RAPPORT DE VALIDATION DES DONNÉES")
    report.append("=" * 60)
    report.append("")

    # Section 1: Tirages historiques
    report.append("📊 TIRAGES HISTORIQUES")
    report.append("-" * 60)
    report.append(f"Nombre de tirages: {len(historical)}")
    report.append(f"Période: {historical['Date'].min()} → {historical['Date'].max()}")
    report.append(f"Colonnes: {', '.join(historical.columns.tolist())}")
    report.append("")

    # Stats boules
    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    all_balls = historical[ball_cols].values.flatten()
    report.append(f"Distribution boules:")
    report.append(f"  - Min: {all_balls.min()}")
    report.append(f"  - Max: {all_balls.max()}")
    report.append(f"  - Moyenne: {all_balls.mean():.2f}")
    report.append(f"  - Médiane: {np.median(all_balls):.0f}")
    report.append("")

    # Stats sommes
    report.append(f"Sommes des boules:")
    report.append(f"  - Min: {historical['Sum_Balls'].min()}")
    report.append(f"  - Max: {historical['Sum_Balls'].max()}")
    report.append(f"  - Moyenne: {historical['Sum_Balls'].mean():.2f}")
    report.append(f"  - Écart-type: {historical['Sum_Balls'].std():.2f}")
    report.append("")

    # Section 2: Mes jeux
    report.append("🎮 MES JEUX")
    report.append("-" * 60)
    report.append(f"Nombre de jeux: {len(my_games)}")

    if 'Date_Jeu' in my_games.columns and not my_games['Date_Jeu'].isna().all():
        report.append(f"Période: {my_games['Date_Jeu'].min()} → {my_games['Date_Jeu'].max()}")

    total_invested = len(my_games) * 3.50
    report.append(f"Investissement total: {total_invested:.2f} CHF")

    if 'Gain_CHF' in my_games.columns:
        total_won = my_games['Gain_CHF'].sum()
        roi = ((total_won - total_invested) / total_invested) * 100
        report.append(f"Gains totaux: {total_won:.2f} CHF")
        report.append(f"ROI: {roi:.2f}%")

    if 'Has_13' in my_games.columns:
        count_13 = my_games['Has_13'].sum()
        pct_13 = (count_13 / len(my_games)) * 100
        report.append(f"Jeux avec 13: {count_13} ({pct_13:.1f}%)")

    report.append("")

    # Section 3: Validation
    report.append("✅ VALIDATIONS")
    report.append("-" * 60)

    # Check ranges
    all_balls_my = my_games[ball_cols].values.flatten()
    balls_ok = np.all((all_balls_my >= 1) & (all_balls_my <= 50))
    report.append(f"Boules dans [1-50]: {'✅ OK' if balls_ok else '❌ ERREUR'}")

    if 'E1' in my_games.columns and 'E2' in my_games.columns:
        all_stars = my_games[['E1', 'E2']].values.flatten()
        stars_ok = np.all((all_stars >= 1) & (all_stars <= 12))
        report.append(f"Étoiles dans [1-12]: {'✅ OK' if stars_ok else '❌ ERREUR'}")

    # Check chronologie
    chrono_ok = historical['Date'].is_monotonic_increasing
    report.append(f"Chronologie cohérente: {'✅ OK' if chrono_ok else '⚠️  Warning'}")

    report.append("")
    report.append("=" * 60)
    report.append("FIN DU RAPPORT")
    report.append("=" * 60)

    return "\n".join(report)


def main():
    """Pipeline principal de nettoyage."""
    print("=" * 60)
    print("🧹 NETTOYAGE ET VALIDATION DES DONNÉES")
    print("=" * 60)

    # Étape 1: Charger
    historical, my_games = load_data()

    # Étape 2: Valider
    historical = validate_historical_draws(historical)
    my_games = validate_my_games(my_games)

    # Étape 3: Créer features
    historical = create_features_draws(historical)
    my_games = create_features_my_games(my_games)

    # Étape 4: Sauvegarder
    print("\n💾 Sauvegarde des données nettoyées...")
    historical.to_csv("data/processed/clean_draws.csv", index=False)
    my_games.to_csv("data/processed/clean_my_games.csv", index=False)
    print("✅ Sauvegarde terminée")

    # Étape 5: Rapport de validation
    report = generate_validation_report(historical, my_games)
    with open("data/processed/validation_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("💾 Rapport sauvegardé: data/processed/validation_report.txt")

    # Afficher rapport
    print("\n" + report)

    print("\n➡️  Prochaine étape: python src/03_analyze_games.py")


if __name__ == "__main__":
    main()
