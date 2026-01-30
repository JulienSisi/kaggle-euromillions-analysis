"""
Script 03: Analyse des 133 jeux réels

Objectif:
    Analyser en profondeur les 133 jeux joués entre 2020-2023.
    Calculer ROI, distribution des rangs, patterns, et comparaison avec probabilités théoriques.

Input:
    data/processed/clean_my_games.csv
    data/processed/clean_draws.csv (pour contexte)

Output:
    outputs/reports/games_analysis.csv
    outputs/reports/rank_distribution.csv
    outputs/reports/number_frequency.csv
    Console: Rapport détaillé

Usage:
    python src/03_analyze_games.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Import configurations depuis utils.py
sys.path.append(str(Path(__file__).parent))
from utils import PRIZE_RANKS, expected_wins_for_rank, calculate_roi


def load_data():
    """
    Charge les données nettoyées.

    Returns:
        Tuple (my_games, historical_draws)
    """
    try:
        my_games = pd.read_csv("data/processed/clean_my_games.csv")
        historical = pd.read_csv("data/processed/clean_draws.csv")
        print("✅ Données chargées")
        return my_games, historical
    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        print("\n➡️  Exécuter d'abord: python src/02_clean_data.py")
        sys.exit(1)


def ensure_output_dirs():
    """Crée les répertoires de sortie."""
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)


def analyze_roi(df: pd.DataFrame) -> dict:
    """
    Analyse du ROI (Return on Investment).

    Args:
        df: DataFrame des jeux personnels

    Returns:
        Dict avec métriques ROI
    """
    print("\n💰 ANALYSE DU ROI")
    print("-" * 60)

    n_games = len(df)
    total_invested = n_games * 3.50

    if 'Gain_CHF' in df.columns:
        total_won = df['Gain_CHF'].sum()
    else:
        total_won = 0.0
        print("⚠️  Colonne 'Gain_CHF' absente, gains = 0")

    roi = calculate_roi(total_invested, total_won)
    net_result = total_won - total_invested

    # Théorique: redistribution 50%
    theoretical_roi = -50.0
    deviation = roi - theoretical_roi

    print(f"Jeux joués: {n_games}")
    print(f"Investissement total: {total_invested:.2f} CHF")
    print(f"Gains totaux: {total_won:.2f} CHF")
    print(f"Résultat net: {net_result:+.2f} CHF")
    print(f"ROI observé: {roi:.2f}%")
    print(f"ROI théorique: {theoretical_roi:.2f}%")
    print(f"Écart: {deviation:+.2f} points")

    if roi < theoretical_roi:
        print("❌ Sous-performance vs théorique")
    else:
        print("✅ Sur-performance vs théorique (mais toujours négatif)")

    return {
        'n_games': n_games,
        'total_invested': total_invested,
        'total_won': total_won,
        'net_result': net_result,
        'roi': roi,
        'theoretical_roi': theoretical_roi,
        'deviation': deviation
    }


def analyze_rank_distribution(df: pd.DataFrame, n_games: int) -> pd.DataFrame:
    """
    Analyse la distribution des rangs gagnés.

    Args:
        df: DataFrame des jeux personnels
        n_games: Nombre de jeux joués

    Returns:
        DataFrame avec comparaison observé vs théorique
    """
    print("\n🏆 DISTRIBUTION DES RANGS")
    print("-" * 60)

    # Compter les rangs observés
    if 'Rang' in df.columns:
        rank_counts = df['Rang'].value_counts().sort_index()
    else:
        rank_counts = pd.Series(dtype=int)
        print("⚠️  Colonne 'Rang' absente")

    # Créer tableau comparatif
    comparison = []

    for rank in range(1, 14):
        observed = rank_counts.get(rank, 0)
        expected = expected_wins_for_rank(rank, n_games)
        ratio = observed / expected if expected > 0 else 0

        comparison.append({
            'Rang': rank,
            'Match': PRIZE_RANKS[rank]['match'],
            'Observé': observed,
            'Attendu': expected,
            'Ratio': ratio,
            'Gain_Moyen_CHF': PRIZE_RANKS[rank]['avg_prize_CHF']
        })

    df_comparison = pd.DataFrame(comparison)

    # Afficher
    print(df_comparison.to_string(index=False))

    # Insights
    print("\n📊 INSIGHTS:")

    # Rangs sur-représentés
    over_represented = df_comparison[df_comparison['Ratio'] > 1.5]
    if not over_represented.empty:
        print("\n✅ Rangs sur-représentés (ratio > 1.5x):")
        for _, row in over_represented.iterrows():
            print(f"  - Rang {row['Rang']}: {row['Ratio']:.2f}x ({row['Match']})")

    # Rangs sous-représentés
    under_represented = df_comparison[df_comparison['Ratio'] < 0.5]
    if not under_represented.empty:
        print("\n❌ Rangs sous-représentés (ratio < 0.5x):")
        for _, row in under_represented.iterrows():
            if row['Attendu'] > 0.1:  # Seulement si attendu significatif
                print(f"  - Rang {row['Rang']}: {row['Ratio']:.2f}x ({row['Match']})")

    # Jackpot
    if df_comparison[df_comparison['Rang'] == 1]['Observé'].iloc[0] == 0:
        print("\n🎰 Jackpot (Rang 1): Jamais gagné")
        prob = PRIZE_RANKS[1]['probability']
        print(f"   Probabilité théorique: {prob:.2e} ({1/prob:.0f} tirages)")

    # Taux de réussite global
    total_wins = df_comparison['Observé'].sum()
    win_rate = (total_wins / n_games) * 100
    theoretical_win_rate = sum(PRIZE_RANKS[r]['probability'] for r in range(1, 14)) * 100

    print(f"\n📈 Taux de réussite global:")
    print(f"   Observé: {win_rate:.2f}% ({total_wins}/{n_games})")
    print(f"   Théorique: {theoretical_win_rate:.2f}%")
    print(f"   Ratio: {win_rate / theoretical_win_rate:.2f}x")

    return df_comparison


def analyze_number_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse la fréquence des numéros joués.

    Args:
        df: DataFrame des jeux personnels

    Returns:
        DataFrame avec fréquence par numéro
    """
    print("\n🔢 FRÉQUENCE DES NUMÉROS JOUÉS")
    print("-" * 60)

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    all_numbers = df[ball_cols].values.flatten()

    # Compter fréquences
    freq_series = pd.Series(all_numbers).value_counts().sort_index()

    # Distribution uniforme attendue
    n_games = len(df)
    expected_freq = (n_games * 5) / 50  # ~13.3 pour 133 jeux

    # Créer DataFrame
    freq_df = pd.DataFrame({
        'Numéro': range(1, 51),
        'Fréquence': [freq_series.get(i, 0) for i in range(1, 51)],
        'Attendu': expected_freq,
        'Écart': [freq_series.get(i, 0) - expected_freq for i in range(1, 51)]
    })

    freq_df['Ratio'] = freq_df['Fréquence'] / freq_df['Attendu']

    # Top 10 numéros les plus joués
    top10 = freq_df.nlargest(10, 'Fréquence')
    print("\n🔝 Top 10 numéros les plus joués:")
    print(top10[['Numéro', 'Fréquence', 'Ratio']].to_string(index=False))

    # Numéros jamais joués
    never_played = freq_df[freq_df['Fréquence'] == 0]
    if not never_played.empty:
        print(f"\n🚫 Numéros jamais joués: {len(never_played)}")
        print(f"   {never_played['Numéro'].tolist()}")

    # Le 13
    if 'Has_13' in df.columns:
        count_13 = df['Has_13'].sum()
        pct_13 = (count_13 / n_games) * 100
        print(f"\n⭐ Numéro sacré (13):")
        print(f"   Présence: {count_13}/{n_games} jeux ({pct_13:.1f}%)")
        print(f"   Fréquence attendue: ~10%")
        if pct_13 > 50:
            print(f"   ➡️  BIAIS MAJEUR DÉTECTÉ (surreprésentation {pct_13/10:.1f}x)")

    return freq_df


def analyze_temporal_evolution(df: pd.DataFrame):
    """
    Analyse l'évolution temporelle du ROI.

    Args:
        df: DataFrame des jeux personnels
    """
    print("\n📈 ÉVOLUTION TEMPORELLE DU ROI")
    print("-" * 60)

    if 'Cumulative_ROI' not in df.columns:
        print("⚠️  Feature 'Cumulative_ROI' absente, skip analyse temporelle")
        return

    # Quartiles de ROI
    q1_idx = len(df) // 4
    q2_idx = len(df) // 2
    q3_idx = 3 * len(df) // 4

    print(f"ROI après 25% des jeux (n={q1_idx}): {df.iloc[q1_idx-1]['Cumulative_ROI']:.2f}%")
    print(f"ROI après 50% des jeux (n={q2_idx}): {df.iloc[q2_idx-1]['Cumulative_ROI']:.2f}%")
    print(f"ROI après 75% des jeux (n={q3_idx}): {df.iloc[q3_idx-1]['Cumulative_ROI']:.2f}%")
    print(f"ROI final (n={len(df)}): {df.iloc[-1]['Cumulative_ROI']:.2f}%")

    # Identifier plus longue série de pertes
    if 'Gain_CHF' in df.columns:
        df['Loss'] = df['Gain_CHF'] == 0
        loss_streaks = (
            df['Loss']
            .groupby((df['Loss'] != df['Loss'].shift()).cumsum())
            .sum()
        )
        longest_streak = loss_streaks.max()
        print(f"\n🎲 Plus longue série de pertes consécutives: {longest_streak} jeux")

        # Série de gains
        df['Win'] = df['Gain_CHF'] > 0
        win_streaks = (
            df['Win']
            .groupby((df['Win'] != df['Win'].shift()).cumsum())
            .sum()
        )
        longest_win_streak = win_streaks.max()
        print(f"🎉 Plus longue série de gains consécutifs: {longest_win_streak} jeux")


def analyze_sum_distribution(df: pd.DataFrame):
    """
    Analyse la distribution des sommes des boules.

    Args:
        df: DataFrame des jeux personnels
    """
    print("\n➕ DISTRIBUTION DES SOMMES")
    print("-" * 60)

    if 'Sum_Balls' not in df.columns:
        print("⚠️  Feature 'Sum_Balls' absente")
        return

    sums = df['Sum_Balls']

    print(f"Minimum: {sums.min()}")
    print(f"Maximum: {sums.max()}")
    print(f"Moyenne: {sums.mean():.2f}")
    print(f"Médiane: {sums.median():.0f}")
    print(f"Écart-type: {sums.std():.2f}")

    # Comparaison avec contraintes (Méthode 2)
    SUM_MIN = 90
    SUM_MAX = 150
    SUM_TARGET = 120

    within_constraints = sums.between(SUM_MIN, SUM_MAX).sum()
    pct_valid = (within_constraints / len(df)) * 100

    print(f"\nContraintes [90-150]:")
    print(f"  Respectées: {within_constraints}/{len(df)} ({pct_valid:.1f}%)")

    # Distance au target
    avg_distance = abs(sums - SUM_TARGET).mean()
    print(f"\nDistance moyenne au target (120): {avg_distance:.2f}")


def main():
    """Pipeline principal d'analyse."""
    print("=" * 60)
    print("📊 ANALYSE DES 133 JEUX RÉELS")
    print("=" * 60)

    # Charger données
    my_games, historical = load_data()
    ensure_output_dirs()

    # Analyse 1: ROI
    roi_stats = analyze_roi(my_games)

    # Analyse 2: Distribution rangs
    rank_dist = analyze_rank_distribution(my_games, len(my_games))

    # Analyse 3: Fréquence numéros
    number_freq = analyze_number_frequency(my_games)

    # Analyse 4: Évolution temporelle
    analyze_temporal_evolution(my_games)

    # Analyse 5: Distribution sommes
    analyze_sum_distribution(my_games)

    # Sauvegarder résultats
    print("\n💾 Sauvegarde des rapports...")

    # ROI stats
    pd.DataFrame([roi_stats]).to_csv(
        "outputs/reports/games_analysis.csv",
        index=False
    )

    # Distribution rangs
    rank_dist.to_csv(
        "outputs/reports/rank_distribution.csv",
        index=False
    )

    # Fréquence numéros
    number_freq.to_csv(
        "outputs/reports/number_frequency.csv",
        index=False
    )

    print("✅ Rapports sauvegardés dans outputs/reports/")

    # Conclusion
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION CLÉS")
    print("=" * 60)
    print(f"ROI: {roi_stats['roi']:.2f}% (vs {roi_stats['theoretical_roi']:.2f}% théorique)")

    # Identifier le paradoxe
    total_wins = rank_dist['Observé'].sum()
    expected_total_wins = rank_dist['Attendu'].sum()
    win_ratio = total_wins / expected_total_wins if expected_total_wins > 0 else 0

    print(f"Taux de réussite: {win_ratio:.2f}x supérieur au théorique")

    if win_ratio > 1 and roi_stats['roi'] < roi_stats['theoretical_roi']:
        print("\n🎭 PARADOXE DÉTECTÉ:")
        print("   ➡️  Gagner PLUS SOUVENT, mais perdre PLUS D'ARGENT")
        print("   ➡️  Explication: Maximisation petits gains, absence gros gains")

    print("\n➡️  Prochaine étape: python src/04_statistical_tests.py")


if __name__ == "__main__":
    main()
