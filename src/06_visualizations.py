"""
Script 06: Génération des visualisations

Objectif:
    Créer tous les graphiques pour l'analyse EuroMillions.

Input:
    data/processed/clean_draws.csv
    data/processed/clean_my_games.csv
    outputs/reports/*.csv

Output:
    outputs/figures/*.png

Usage:
    python src/06_visualizations.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Configuration matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("viridis")


def load_data():
    """Charge toutes les données nécessaires."""
    try:
        historical = pd.read_csv("data/processed/clean_draws.csv")
        my_games = pd.read_csv("data/processed/clean_my_games.csv")

        # Optionnel: charger résultats backtesting
        try:
            bt_julien = pd.read_csv("outputs/reports/backtesting_julien.csv")
            bt_random = pd.read_csv("outputs/reports/backtesting_random.csv")
            bt_comparison = pd.read_csv("outputs/reports/backtesting_comparison.csv")
        except FileNotFoundError:
            bt_julien = bt_random = bt_comparison = None

        print("✅ Données chargées")
        return historical, my_games, bt_julien, bt_random, bt_comparison

    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)


def ensure_output_dir():
    """Crée le répertoire de sortie."""
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)


def plot_roi_evolution(my_games: pd.DataFrame):
    """
    Graphique de l'évolution du ROI cumulé.
    """
    print("📊 Génération: ROI évolution...")

    if 'Cumulative_ROI' not in my_games.columns:
        print("⚠️  Skip: Cumulative_ROI absent")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # ROI cumulé
    ax.plot(range(1, len(my_games) + 1), my_games['Cumulative_ROI'],
            linewidth=2, label='ROI observé', color='#2E86AB')

    # Ligne théorique -50%
    ax.axhline(y=-50, color='red', linestyle='--', linewidth=2,
               label='ROI théorique (-50%)', alpha=0.7)

    # Ligne 0%
    ax.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)

    ax.set_xlabel('Nombre de jeux joués', fontsize=12)
    ax.set_ylabel('ROI cumulé (%)', fontsize=12)
    ax.set_title('Évolution du ROI : Espoir et Désillusion', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('outputs/figures/roi_evolution.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/roi_evolution.png")


def plot_number_frequency_heatmap(my_games: pd.DataFrame):
    """
    Heatmap de la fréquence des numéros joués.
    """
    print("📊 Génération: Heatmap fréquence...")

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    all_numbers = my_games[ball_cols].values.flatten()

    # Fréquences
    freq = pd.Series(all_numbers).value_counts().sort_index()
    freq_full = pd.Series([freq.get(i, 0) for i in range(1, 51)])

    # Reshape en matrice 5x10
    freq_matrix = freq_full.values.reshape(5, 10)

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(freq_matrix, annot=True, fmt='d', cmap='YlOrRd',
                linewidths=0.5, cbar_kws={'label': 'Fréquence'},
                ax=ax)

    # Labels
    ax.set_xlabel('Numéros (colonnes)', fontsize=12)
    ax.set_ylabel('Groupes (lignes)', fontsize=12)
    ax.set_title('Fréquence des numéros joués (133 jeux)', fontsize=14, fontweight='bold')

    # Custom tick labels
    # X-axis: position dans la décade (1er, 2e, 3e... 10e numéro de chaque groupe)
    ax.set_xticklabels([str(i) for i in range(1, 11)])
    # Y-axis: groupes de numéros
    ax.set_yticklabels(['1-10', '11-20', '21-30', '31-40', '41-50'])

    plt.tight_layout()
    plt.savefig('outputs/figures/heatmap_frequency.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/heatmap_frequency.png")


def plot_sum_distribution(historical: pd.DataFrame, my_games: pd.DataFrame):
    """
    Distribution des sommes: tirages réels vs mes jeux.
    """
    print("📊 Génération: Distribution sommes...")

    if 'Sum_Balls' not in historical.columns or 'Sum_Balls' not in my_games.columns:
        print("⚠️  Skip: Sum_Balls absent")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogrammes
    ax.hist(historical['Sum_Balls'], bins=30, alpha=0.6, label='Tirages réels',
            color='#4ECDC4', edgecolor='black')
    ax.hist(my_games['Sum_Balls'], bins=20, alpha=0.7, label='Mes jeux',
            color='#FF6B6B', edgecolor='black')

    # Ligne cible (120)
    ax.axvline(x=120, color='green', linestyle='--', linewidth=2,
               label='Cible (config)', alpha=0.8)

    # Contraintes [90-150]
    ax.axvline(x=90, color='red', linestyle=':', linewidth=1, alpha=0.5)
    ax.axvline(x=150, color='red', linestyle=':', linewidth=1, alpha=0.5)

    ax.set_xlabel('Somme des 5 boules', fontsize=12)
    ax.set_ylabel('Fréquence', fontsize=12)
    ax.set_title('Distribution des sommes: Réalité vs Mes jeux', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/sum_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/sum_distribution.png")


def plot_rank_distribution_comparison(my_games: pd.DataFrame):
    """
    Comparaison distribution rangs: Observé vs Théorique.
    """
    print("📊 Génération: Distribution rangs...")

    if 'Rank' not in my_games.columns:
        print("⚠️  Skip: Rank absent")
        return

    # Charger résultats d'analyse
    try:
        rank_dist = pd.read_csv("outputs/reports/rank_distribution.csv")
    except FileNotFoundError:
        print("⚠️  Skip: rank_distribution.csv absent")
        return

    fig, ax = plt.subplots(figsize=(14, 7))

    x = rank_dist['Rang']
    width = 0.35

    # Barres
    ax.bar(x - width/2, rank_dist['Observé'], width, label='Observé',
           color='#FF6B6B', alpha=0.8, edgecolor='black')
    ax.bar(x + width/2, rank_dist['Attendu'], width, label='Théorique',
           color='#4ECDC4', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Rang', fontsize=12)
    ax.set_ylabel('Nombre de gains', fontsize=12)
    ax.set_title('Distribution des rangs: Observé vs Théorique (133 jeux)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/rank_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/rank_distribution.png")


def plot_backtesting_comparison(bt_comparison: pd.DataFrame):
    """
    Comparaison backtesting Julien vs Random.
    """
    print("📊 Génération: Backtesting comparison...")

    if bt_comparison is None:
        print("⚠️  Skip: Pas de données backtesting")
        return

    # Filtrer les rangs
    rank_rows = bt_comparison[bt_comparison['Métrique'].str.contains('Rang')]

    if rank_rows.empty:
        print("⚠️  Skip: Pas de données rangs")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Subplot 1: Distribution rangs absolue
    ranks = range(1, 14)
    julien_counts = []
    random_counts = []

    for rank in ranks:
        row = rank_rows[rank_rows['Métrique'].str.contains(f'Rang {rank}\\b')]
        if not row.empty:
            julien_counts.append(row['Julien'].iloc[0])
            random_counts.append(row['Random'].iloc[0])
        else:
            julien_counts.append(0)
            random_counts.append(0)

    x = np.arange(len(ranks))
    width = 0.35

    axes[0].bar(x - width/2, julien_counts, width, label='Julien',
                color='#FF6B6B', alpha=0.8)
    axes[0].bar(x + width/2, random_counts, width, label='Random',
                color='#4ECDC4', alpha=0.8)

    axes[0].set_xlabel('Rang', fontsize=12)
    axes[0].set_ylabel('Nombre de gains (sur 10k jeux)', fontsize=12)
    axes[0].set_title('Distribution des rangs', fontsize=13, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(ranks)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')

    # Subplot 2: Ratio Julien/Random
    ratios = []
    for j, r in zip(julien_counts, random_counts):
        if r > 0:
            ratios.append(j / r)
        else:
            ratios.append(0)

    colors = ['green' if ratio > 1 else 'red' for ratio in ratios]

    axes[1].bar(x, ratios, color=colors, alpha=0.7, edgecolor='black')
    axes[1].axhline(y=1, color='black', linestyle='--', linewidth=2,
                    label='Égalité', alpha=0.7)

    axes[1].set_xlabel('Rang', fontsize=12)
    axes[1].set_ylabel('Ratio Julien / Random', fontsize=12)
    axes[1].set_title('Sur/Sous-performance par rang', fontsize=13, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(ranks)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/backtesting_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/backtesting_comparison.png")


def plot_number_frequency_comparison(historical: pd.DataFrame, my_games: pd.DataFrame):
    """
    Comparaison fréquence numéros: Tirages réels vs Mes jeux.
    """
    print("📊 Génération: Comparaison fréquence numéros...")

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']

    # Fréquences
    real_numbers = historical[ball_cols].values.flatten()
    my_numbers = my_games[ball_cols].values.flatten()

    real_freq = pd.Series(real_numbers).value_counts().sort_index()
    my_freq = pd.Series(my_numbers).value_counts().sort_index()

    # Normaliser (pourcentage)
    real_freq_pct = (real_freq / real_freq.sum()) * 100
    my_freq_pct = (my_freq / my_freq.sum()) * 100

    # Assurer tous les numéros
    numbers = range(1, 51)
    real_pct = [real_freq_pct.get(i, 0) for i in numbers]
    my_pct = [my_freq_pct.get(i, 0) for i in numbers]

    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(1, 51)
    width = 0.4

    ax.bar(x - width/2, real_pct, width, label='Tirages réels', color='#4ECDC4', alpha=0.7)
    ax.bar(x + width/2, my_pct, width, label='Mes jeux', color='#FF6B6B', alpha=0.7)

    # Ligne uniforme théorique
    ax.axhline(y=2, color='green', linestyle='--', linewidth=1,
               label='Uniforme (2%)', alpha=0.6)

    ax.set_xlabel('Numéro', fontsize=12)
    ax.set_ylabel('Fréquence (%)', fontsize=12)
    ax.set_title('Fréquence des numéros: Tirages réels vs Mes jeux',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 51, 5))
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/number_frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/number_frequency_comparison.png")


def plot_autocorrelation(historical: pd.DataFrame):
    """
    Graphique d'autocorrélation pour vérifier indépendance.
    """
    print("📊 Génération: Autocorrélation...")

    if 'Has_13' not in historical.columns:
        print("⚠️  Skip: Has_13 absent")
        return

    series = historical['Has_13'].astype(int)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculer autocorrélation pour lags 1-50
    lags = range(1, 51)
    autocorr = [series.autocorr(lag=lag) for lag in lags]

    ax.bar(lags, autocorr, color='#2E86AB', alpha=0.7, edgecolor='black')

    # Seuil de significativité
    n = len(series)
    threshold = 1.96 / np.sqrt(n)
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=1,
               label=f'Seuil +{threshold:.4f}', alpha=0.7)
    ax.axhline(y=-threshold, color='red', linestyle='--', linewidth=1,
               label=f'Seuil -{threshold:.4f}', alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    ax.set_xlabel('Lag', fontsize=12)
    ax.set_ylabel('Autocorrélation', fontsize=12)
    ax.set_title('Autocorrélation: Présence du 13 (test d\'indépendance)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/autocorrelation_13.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Sauvegardé: outputs/figures/autocorrelation_13.png")


def main():
    """Pipeline principal de visualisation."""
    print("=" * 60)
    print("📊 GÉNÉRATION DES VISUALISATIONS")
    print("=" * 60)

    # Charger données
    historical, my_games, bt_julien, bt_random, bt_comparison = load_data()
    ensure_output_dir()

    # Générer graphiques
    plot_roi_evolution(my_games)
    plot_number_frequency_heatmap(my_games)
    plot_sum_distribution(historical, my_games)
    plot_rank_distribution_comparison(my_games)
    plot_number_frequency_comparison(historical, my_games)
    plot_autocorrelation(historical)

    # Backtesting (si disponible)
    if bt_comparison is not None:
        plot_backtesting_comparison(bt_comparison)

    # Résumé
    print("\n" + "=" * 60)
    print("✅ VISUALISATIONS TERMINÉES")
    print("=" * 60)
    print("\n📂 Fichiers générés dans outputs/figures/:")
    for file in sorted(Path("outputs/figures").glob("*.png")):
        print(f"  - {file.name}")

    print("\n🎉 Projet complet !")
    print("\n📋 Prochaines étapes:")
    print("  1. Créer notebook Jupyter interactif")
    print("  2. Rédiger rapport final (outputs/final_report.md)")
    print("  3. Upload sur Kaggle")
    print("  4. Partager sur LinkedIn")


if __name__ == "__main__":
    main()
