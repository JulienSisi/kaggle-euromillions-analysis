"""
Script 05: Backtesting "Style Julien" vs Aléatoire

Objectif:
    Simuler 10,000 jeux selon deux profils :
    1. Profil "Julien" : Applique les 8 méthodes analytiques
    2. Profil "Aléatoire" : Sélection purement random

    Comparer les performances pour tester l'hypothèse :
    "Les méthodes maximisent les petits gains au détriment des gros gains"

Input:
    data/processed/clean_draws.csv (pour historical context)

Output:
    outputs/reports/backtesting_julien.csv
    outputs/reports/backtesting_random.csv
    outputs/reports/backtesting_comparison.csv
    Console: Rapport comparatif

Usage:
    python src/05_backtesting.py
"""

import pandas as pd
import numpy as np
import random
import sys
from pathlib import Path
from tqdm import tqdm

# Import utils
sys.path.append(str(Path(__file__).parent))
from utils import (
    generate_combination_julien_style,
    generate_combination_random,
    calculate_rank,
    get_prize_for_rank,
    calculate_roi,
    PRIZE_RANKS
)


def load_historical_draws():
    """Charge les tirages historiques."""
    try:
        df = pd.read_csv("data/processed/clean_draws.csv")
        print("✅ Tirages historiques chargés")
        return df
    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)


def simulate_draw():
    """
    Simule un tirage EuroMillions aléatoire.

    Returns:
        Tuple (boules, étoiles)
    """
    balls = sorted(random.sample(range(1, 51), 5))
    stars = sorted(random.sample(range(1, 13), 2))
    return balls, stars


def simulate_games(
    n_games: int,
    profile: str,
    historical_draws: pd.DataFrame
) -> pd.DataFrame:
    """
    Simule n_games selon le profil spécifié.

    Args:
        n_games: Nombre de jeux à simuler
        profile: 'julien' ou 'random'
        historical_draws: DataFrame des tirages historiques (pour profil Julien)

    Returns:
        DataFrame avec résultats [B1-B5, E1-E2, Rank, Gain_CHF]
    """
    print(f"\n🎲 Simulation de {n_games:,} jeux ({profile})...")

    results = []

    for i in tqdm(range(n_games), desc=f"Profil {profile}"):
        # Générer combinaison jouée
        if profile == 'julien':
            played_balls = generate_combination_julien_style(historical_draws)
        else:
            played_balls = generate_combination_random()

        # Générer étoiles aléatoires (pas d'optimisation pour étoiles)
        played_stars = sorted(random.sample(range(1, 13), 2))

        # Simuler tirage réel
        drawn_balls, drawn_stars = simulate_draw()

        # Calculer rang
        rank = calculate_rank(played_balls, played_stars, drawn_balls, drawn_stars)
        gain = get_prize_for_rank(rank)

        results.append({
            'B1': played_balls[0],
            'B2': played_balls[1],
            'B3': played_balls[2],
            'B4': played_balls[3],
            'B5': played_balls[4],
            'E1': played_stars[0],
            'E2': played_stars[1],
            'Rank': rank if rank > 0 else None,
            'Gain_CHF': gain
        })

    return pd.DataFrame(results)


def analyze_results(df: pd.DataFrame, profile_name: str) -> dict:
    """
    Analyse les résultats d'une simulation.

    Args:
        df: DataFrame des résultats
        profile_name: Nom du profil

    Returns:
        Dict avec statistiques
    """
    print(f"\n📊 Analyse Profil '{profile_name}'")
    print("-" * 60)

    n_games = len(df)
    total_invested = n_games * 3.50
    total_won = df['Gain_CHF'].sum()
    roi = calculate_roi(total_invested, total_won)

    # Distribution des rangs
    rank_counts = df['Rank'].value_counts().sort_index()

    # Taux de réussite
    wins = df['Rank'].notna().sum()
    win_rate = (wins / n_games) * 100

    # Stats générales
    print(f"Jeux joués: {n_games:,}")
    print(f"Investissement: {total_invested:,.2f} CHF")
    print(f"Gains totaux: {total_won:,.2f} CHF")
    print(f"ROI: {roi:.2f}%")
    print(f"Taux de réussite: {win_rate:.2f}% ({wins:,}/{n_games:,})")

    # Distribution par rang
    print(f"\nDistribution des rangs:")
    for rank in range(1, 14):
        count = rank_counts.get(rank, 0)
        pct = (count / n_games) * 100
        expected = PRIZE_RANKS[rank]['probability'] * n_games
        ratio = count / expected if expected > 0 else 0

        if count > 0:
            print(f"  Rang {rank:2d}: {count:5d} ({pct:5.2f}%) - "
                  f"Attendu: {expected:6.2f} - Ratio: {ratio:.2f}x")

    return {
        'profile': profile_name,
        'n_games': n_games,
        'total_invested': total_invested,
        'total_won': total_won,
        'roi': roi,
        'wins': wins,
        'win_rate': win_rate,
        'rank_distribution': rank_counts.to_dict()
    }


def compare_profiles(stats_julien: dict, stats_random: dict) -> pd.DataFrame:
    """
    Compare les deux profils.

    Args:
        stats_julien: Stats profil Julien
        stats_random: Stats profil Random

    Returns:
        DataFrame de comparaison
    """
    print("\n" + "=" * 60)
    print("⚖️  COMPARAISON JULIEN VS RANDOM")
    print("=" * 60)

    comparison = []

    # ROI
    comparison.append({
        'Métrique': 'ROI (%)',
        'Julien': stats_julien['roi'],
        'Random': stats_random['roi'],
        'Écart': stats_julien['roi'] - stats_random['roi']
    })

    # Taux de réussite
    comparison.append({
        'Métrique': 'Taux de réussite (%)',
        'Julien': stats_julien['win_rate'],
        'Random': stats_random['win_rate'],
        'Écart': stats_julien['win_rate'] - stats_random['win_rate']
    })

    # Gains totaux
    comparison.append({
        'Métrique': 'Gains totaux (CHF)',
        'Julien': stats_julien['total_won'],
        'Random': stats_random['total_won'],
        'Écart': stats_julien['total_won'] - stats_random['total_won']
    })

    # Distribution par rang
    for rank in range(1, 14):
        julien_count = stats_julien['rank_distribution'].get(rank, 0)
        random_count = stats_random['rank_distribution'].get(rank, 0)

        comparison.append({
            'Métrique': f'Rang {rank} ({PRIZE_RANKS[rank]["match"]})',
            'Julien': julien_count,
            'Random': random_count,
            'Écart': julien_count - random_count
        })

    df_comparison = pd.DataFrame(comparison)

    print(df_comparison.to_string(index=False))

    # Insights
    print("\n" + "=" * 60)
    print("🔍 INSIGHTS CLÉS")
    print("=" * 60)

    roi_diff = stats_julien['roi'] - stats_random['roi']
    win_rate_diff = stats_julien['win_rate'] - stats_random['win_rate']

    print(f"\n1. ROI:")
    if abs(roi_diff) < 1:
        print(f"   ≈ Similaire ({roi_diff:+.2f}% écart)")
    elif roi_diff > 0:
        print(f"   ✅ Julien sur-performe: {roi_diff:+.2f}%")
    else:
        print(f"   ❌ Julien sous-performe: {roi_diff:+.2f}%")

    print(f"\n2. Taux de réussite:")
    if abs(win_rate_diff) < 0.5:
        print(f"   ≈ Similaire ({win_rate_diff:+.2f}% écart)")
    elif win_rate_diff > 0:
        print(f"   ✅ Julien gagne plus souvent: {win_rate_diff:+.2f}%")
    else:
        print(f"   ❌ Julien gagne moins souvent: {win_rate_diff:+.2f}%")

    # Paradoxe ?
    if win_rate_diff > 0 and roi_diff < 0:
        print(f"\n🎭 PARADOXE DÉTECTÉ:")
        print(f"   Julien gagne PLUS SOUVENT (+{win_rate_diff:.2f}%)")
        print(f"   mais ROI INFÉRIEUR ({roi_diff:+.2f}%)")
        print(f"\n   Explication probable:")
        print(f"   - Plus de petits gains (rangs 11-13)")
        print(f"   - Moins de gros gains (rangs 1-5)")

    # Analyser distribution rangs
    print(f"\n3. Distribution des rangs:")

    # Petits gains (11-13)
    julien_small = sum(stats_julien['rank_distribution'].get(r, 0) for r in [11, 12, 13])
    random_small = sum(stats_random['rank_distribution'].get(r, 0) for r in [11, 12, 13])
    small_diff = julien_small - random_small

    print(f"   Petits gains (rangs 11-13):")
    print(f"     Julien: {julien_small:,} | Random: {random_small:,} | Écart: {small_diff:+,}")

    # Gros gains (1-5)
    julien_big = sum(stats_julien['rank_distribution'].get(r, 0) for r in [1, 2, 3, 4, 5])
    random_big = sum(stats_random['rank_distribution'].get(r, 0) for r in [1, 2, 3, 4, 5])
    big_diff = julien_big - random_big

    print(f"   Gros gains (rangs 1-5):")
    print(f"     Julien: {julien_big:,} | Random: {random_big:,} | Écart: {big_diff:+,}")

    if small_diff > 0 and big_diff < 0:
        print(f"\n   ➡️  CONFIRMATION: Julien maximise petits gains, minimise gros gains")

    return df_comparison


def main():
    """Pipeline principal de backtesting."""
    print("=" * 60)
    print("🔄 BACKTESTING: JULIEN VS RANDOM")
    print("=" * 60)

    # Configuration
    N_SIMULATIONS = 1000  # Réduit pour rapidité (était 10000)

    print(f"\nConfiguration:")
    print(f"  Nombre de simulations par profil: {N_SIMULATIONS:,}")
    print(f"  Temps estimé: ~2-3 minutes")

    # Charger données historiques
    historical_draws = load_historical_draws()

    # Fixer seed pour reproductibilité
    random.seed(42)
    np.random.seed(42)

    # Simulation Profil Julien
    print("\n" + "=" * 60)
    print("PROFIL 1: JULIEN (8 méthodes analytiques)")
    print("=" * 60)
    results_julien = simulate_games(N_SIMULATIONS, 'julien', historical_draws)

    # Simulation Profil Random
    print("\n" + "=" * 60)
    print("PROFIL 2: RANDOM (pure aléatoire)")
    print("=" * 60)
    results_random = simulate_games(N_SIMULATIONS, 'random', historical_draws)

    # Analyser résultats
    stats_julien = analyze_results(results_julien, "Julien")
    stats_random = analyze_results(results_random, "Random")

    # Comparaison
    comparison = compare_profiles(stats_julien, stats_random)

    # Sauvegarder
    print("\n💾 Sauvegarde des résultats...")
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)

    results_julien.to_csv("outputs/reports/backtesting_julien.csv", index=False)
    results_random.to_csv("outputs/reports/backtesting_random.csv", index=False)
    comparison.to_csv("outputs/reports/backtesting_comparison.csv", index=False)

    print("✅ Fichiers sauvegardés:")
    print("  - outputs/reports/backtesting_julien.csv")
    print("  - outputs/reports/backtesting_random.csv")
    print("  - outputs/reports/backtesting_comparison.csv")

    # Conclusion
    print("\n" + "=" * 60)
    print("✅ BACKTESTING TERMINÉ")
    print("=" * 60)
    print(f"\nRésultats sur {N_SIMULATIONS:,} jeux:")
    print(f"  Julien: ROI = {stats_julien['roi']:.2f}%")
    print(f"  Random: ROI = {stats_random['roi']:.2f}%")
    print(f"\nConclusion: {'Les méthodes analytiques ne surperforment pas le hasard' if abs(stats_julien['roi'] - stats_random['roi']) < 1 else 'Différence significative détectée'}")

    print("\n➡️  Prochaine étape: python src/06_visualizations.py")


if __name__ == "__main__":
    main()
