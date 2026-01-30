"""
Script 04: Tests statistiques

Objectif:
    Réaliser des tests statistiques pour valider/invalider les hypothèses :
    - Uniformité des tirages (Chi-2)
    - Distribution normale des sommes (Kolmogorov-Smirnov)
    - Indépendance temporelle (autocorrélation)
    - Comparaison mes jeux vs tirages réels

Input:
    data/processed/clean_draws.csv
    data/processed/clean_my_games.csv

Output:
    outputs/reports/statistical_tests_results.txt
    Console: Résultats détaillés

Usage:
    python src/04_statistical_tests.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from scipy import stats
from scipy.stats import chisquare, kstest, norm


def load_data():
    """Charge les données nettoyées."""
    try:
        historical = pd.read_csv("data/processed/clean_draws.csv")
        my_games = pd.read_csv("data/processed/clean_my_games.csv")
        print("✅ Données chargées")
        return historical, my_games
    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)


def test_uniformity_draws(df: pd.DataFrame) -> dict:
    """
    Test Chi-2 d'uniformité des tirages historiques.

    H0: Les numéros suivent une distribution uniforme.

    Args:
        df: DataFrame des tirages historiques

    Returns:
        Dict avec résultats du test
    """
    print("\n" + "=" * 60)
    print("TEST 1: UNIFORMITÉ DES TIRAGES (Chi-2)")
    print("=" * 60)

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']
    all_numbers = df[ball_cols].values.flatten()

    # Fréquences observées
    observed_freq = pd.Series(all_numbers).value_counts().sort_index()

    # Fréquences attendues (uniforme)
    total_balls = len(all_numbers)
    expected_freq = np.full(50, total_balls / 50)

    # Test Chi-2
    chi2_stat, p_value = chisquare(observed_freq, expected_freq)

    print(f"\nHypothèse nulle (H0): Distribution uniforme")
    print(f"Statistique Chi-2: {chi2_stat:.4f}")
    print(f"P-value: {p_value:.4e}")
    print(f"Degrés de liberté: {50 - 1}")

    # Interprétation
    alpha = 0.05
    if p_value > alpha:
        conclusion = "✅ ACCEPTER H0: Les tirages sont uniformément distribués"
        is_uniform = True
    else:
        conclusion = "❌ REJETER H0: Déviation significative détectée"
        is_uniform = False

    print(f"\nConclusion (α={alpha}):")
    print(f"  {conclusion}")

    # Détails
    freq_df = pd.DataFrame({
        'Numéro': range(1, 51),
        'Observé': observed_freq,
        'Attendu': expected_freq,
        'Écart': observed_freq - expected_freq
    })

    max_deviation = freq_df['Écart'].abs().max()
    most_deviant = freq_df.loc[freq_df['Écart'].abs().idxmax(), 'Numéro']

    print(f"\nÉcart maximal: {max_deviation:.2f} (Numéro {most_deviant})")

    return {
        'test': 'Chi-2 Uniformity',
        'chi2_stat': chi2_stat,
        'p_value': p_value,
        'is_uniform': is_uniform,
        'max_deviation': max_deviation,
        'most_deviant_number': most_deviant
    }


def test_normality_sums(df: pd.DataFrame) -> dict:
    """
    Test de normalité (Kolmogorov-Smirnov) sur les sommes des boules.

    H0: Les sommes suivent une distribution normale.

    Args:
        df: DataFrame des tirages

    Returns:
        Dict avec résultats
    """
    print("\n" + "=" * 60)
    print("TEST 2: NORMALITÉ DES SOMMES (Kolmogorov-Smirnov)")
    print("=" * 60)

    if 'Sum_Balls' not in df.columns:
        print("⚠️  Colonne 'Sum_Balls' absente, test skippé")
        return {}

    sums = df['Sum_Balls'].dropna()

    # Paramètres observés
    mean_obs = sums.mean()
    std_obs = sums.std()

    print(f"\nDistribution observée:")
    print(f"  Moyenne: {mean_obs:.2f}")
    print(f"  Écart-type: {std_obs:.2f}")

    # Distribution théorique (normale)
    # Pour 5 nombres uniformes [1-50]: μ ≈ 5×25.5 = 127.5
    theoretical_mean = 127.5
    theoretical_std = 20  # Approximation

    print(f"\nDistribution théorique:")
    print(f"  Moyenne: {theoretical_mean:.2f}")
    print(f"  Écart-type: {theoretical_std:.2f}")

    # Test KS
    ks_stat, p_value = kstest(
        sums,
        lambda x: norm.cdf(x, loc=mean_obs, scale=std_obs)
    )

    print(f"\nHypothèse nulle (H0): Distribution normale")
    print(f"Statistique KS: {ks_stat:.4f}")
    print(f"P-value: {p_value:.4e}")

    # Interprétation
    alpha = 0.05
    if p_value > alpha:
        conclusion = "✅ ACCEPTER H0: Distribution normale"
        is_normal = True
    else:
        conclusion = "❌ REJETER H0: Déviation significative"
        is_normal = False

    print(f"\nConclusion (α={alpha}):")
    print(f"  {conclusion}")

    return {
        'test': 'KS Normality',
        'ks_stat': ks_stat,
        'p_value': p_value,
        'is_normal': is_normal,
        'mean_observed': mean_obs,
        'std_observed': std_obs
    }


def test_independence_autocorrelation(df: pd.DataFrame) -> dict:
    """
    Test d'indépendance via autocorrélation.

    Vérifie si les tirages sont indépendants (pas de corrélation temporelle).

    Args:
        df: DataFrame des tirages

    Returns:
        Dict avec résultats
    """
    print("\n" + "=" * 60)
    print("TEST 3: INDÉPENDANCE TEMPORELLE (Autocorrélation)")
    print("=" * 60)

    if 'Has_13' not in df.columns:
        print("⚠️  Colonne 'Has_13' absente, test skippé")
        return {}

    # Utiliser présence du 13 comme série binaire
    series = df['Has_13'].astype(int)

    # Calculer autocorrélation pour lags 1-10
    lags = range(1, 11)
    autocorr = [series.autocorr(lag=lag) for lag in lags]

    print(f"\nAutocorrélation de la présence du 13:")
    print(f"{'Lag':<6} {'Autocorr':<10} {'Significatif?'}")
    print("-" * 30)

    # Seuil de significativité: ±1.96 / sqrt(N)
    n = len(series)
    threshold = 1.96 / np.sqrt(n)

    significant_lags = []
    for lag, corr in zip(lags, autocorr):
        is_sig = abs(corr) > threshold
        sig_mark = "⚠️  OUI" if is_sig else "✅ Non"
        print(f"{lag:<6} {corr:<10.4f} {sig_mark}")

        if is_sig:
            significant_lags.append((lag, corr))

    print(f"\nSeuil de significativité: ±{threshold:.4f}")

    if significant_lags:
        print(f"\n❌ {len(significant_lags)} lags significatifs détectés:")
        for lag, corr in significant_lags:
            print(f"   Lag {lag}: {corr:.4f}")
        is_independent = False
    else:
        print("\n✅ Aucune autocorrélation significative → Tirages indépendants")
        is_independent = True

    return {
        'test': 'Autocorrelation',
        'is_independent': is_independent,
        'significant_lags': len(significant_lags),
        'max_autocorr': max(autocorr, key=abs)
    }


def test_my_games_vs_reality(my_games: pd.DataFrame, historical: pd.DataFrame) -> dict:
    """
    Compare la distribution de mes numéros vs tirages réels.

    H0: Mes choix suivent la même distribution que les tirages réels.

    Args:
        my_games: Mes jeux
        historical: Tirages historiques

    Returns:
        Dict avec résultats
    """
    print("\n" + "=" * 60)
    print("TEST 4: MES JEUX VS TIRAGES RÉELS (Chi-2)")
    print("=" * 60)

    ball_cols = ['B1', 'B2', 'B3', 'B4', 'B5']

    # Fréquences de mes numéros
    my_numbers = my_games[ball_cols].values.flatten()
    my_freq = pd.Series(my_numbers).value_counts().sort_index()

    # Fréquences des tirages réels
    real_numbers = historical[ball_cols].values.flatten()
    real_freq = pd.Series(real_numbers).value_counts().sort_index()

    # Normaliser les fréquences réelles au même total que mes jeux
    total_my = len(my_numbers)
    real_freq_normalized = (real_freq / real_freq.sum()) * total_my

    # Assurer que tous les numéros 1-50 sont présents
    my_freq_full = pd.Series([my_freq.get(i, 0) for i in range(1, 51)])
    real_freq_full = pd.Series([real_freq_normalized.get(i, total_my/50) for i in range(1, 51)])

    # Test Chi-2
    chi2_stat, p_value = chisquare(my_freq_full, real_freq_full)

    print(f"\nHypothèse nulle (H0): Mes choix ~ Tirages réels")
    print(f"Statistique Chi-2: {chi2_stat:.4f}")
    print(f"P-value: {p_value:.4e}")

    # Interprétation
    alpha = 0.05
    if p_value > alpha:
        conclusion = "✅ ACCEPTER H0: Pas de différence significative"
        is_similar = True
    else:
        conclusion = "❌ REJETER H0: Mes choix dévient significativement"
        is_similar = False

    print(f"\nConclusion (α={alpha}):")
    print(f"  {conclusion}")

    # Identifier numéros les plus divergents
    divergence = pd.DataFrame({
        'Numéro': range(1, 51),
        'Mes_Jeux': my_freq_full,
        'Réalité_Normalisée': real_freq_full,
        'Écart': my_freq_full - real_freq_full
    })

    top_overplayed = divergence.nlargest(5, 'Écart')
    top_underplayed = divergence.nsmallest(5, 'Écart')

    print(f"\n🔝 Top 5 numéros sur-joués:")
    print(top_overplayed[['Numéro', 'Mes_Jeux', 'Réalité_Normalisée', 'Écart']].to_string(index=False))

    print(f"\n🔽 Top 5 numéros sous-joués:")
    print(top_underplayed[['Numéro', 'Mes_Jeux', 'Réalité_Normalisée', 'Écart']].to_string(index=False))

    return {
        'test': 'Chi-2 My Games vs Reality',
        'chi2_stat': chi2_stat,
        'p_value': p_value,
        'is_similar': is_similar
    }


def test_sum_constraints_compliance(my_games: pd.DataFrame) -> dict:
    """
    Vérifie le respect des contraintes de somme (Méthode 2).

    Args:
        my_games: Mes jeux

    Returns:
        Dict avec résultats
    """
    print("\n" + "=" * 60)
    print("TEST 5: RESPECT DES CONTRAINTES (Méthode 2)")
    print("=" * 60)

    if 'Sum_Balls' not in my_games.columns:
        print("⚠️  Colonne 'Sum_Balls' absente")
        return {}

    sums = my_games['Sum_Balls']

    SUM_MIN = 90
    SUM_MAX = 150
    SUM_TARGET = 120

    # Conformité
    within_range = sums.between(SUM_MIN, SUM_MAX)
    compliance_rate = within_range.sum() / len(my_games) * 100

    print(f"Contraintes: Somme ∈ [{SUM_MIN}, {SUM_MAX}]")
    print(f"Taux de conformité: {compliance_rate:.2f}% ({within_range.sum()}/{len(my_games)})")

    # Distance au target
    distance_to_target = (sums - SUM_TARGET).abs()
    avg_distance = distance_to_target.mean()
    median_distance = distance_to_target.median()

    print(f"\nDistance au target ({SUM_TARGET}):")
    print(f"  Moyenne: {avg_distance:.2f}")
    print(f"  Médiane: {median_distance:.2f}")

    # Concentration autour du target
    tolerance = 10
    near_target = sums.between(SUM_TARGET - tolerance, SUM_TARGET + tolerance)
    near_target_rate = near_target.sum() / len(my_games) * 100

    print(f"\nConcentration autour {SUM_TARGET} ± {tolerance}:")
    print(f"  {near_target_rate:.2f}% des jeux")

    return {
        'test': 'Sum Constraints',
        'compliance_rate': compliance_rate,
        'avg_distance_to_target': avg_distance,
        'near_target_rate': near_target_rate
    }


def save_results(results: list):
    """Sauvegarde les résultats dans un fichier."""
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)

    with open("outputs/reports/statistical_tests_results.txt", "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("RÉSULTATS DES TESTS STATISTIQUES\n")
        f.write("=" * 60 + "\n\n")

        for result in results:
            if not result:
                continue

            f.write(f"Test: {result.get('test', 'Unknown')}\n")
            f.write("-" * 60 + "\n")

            for key, value in result.items():
                if key != 'test':
                    f.write(f"  {key}: {value}\n")

            f.write("\n")

    print("\n💾 Résultats sauvegardés: outputs/reports/statistical_tests_results.txt")


def main():
    """Pipeline principal de tests."""
    print("=" * 60)
    print("🧪 TESTS STATISTIQUES")
    print("=" * 60)

    # Charger données
    historical, my_games = load_data()

    results = []

    # Test 1: Uniformité tirages
    results.append(test_uniformity_draws(historical))

    # Test 2: Normalité sommes
    results.append(test_normality_sums(historical))

    # Test 3: Indépendance
    results.append(test_independence_autocorrelation(historical))

    # Test 4: Mes jeux vs réalité
    results.append(test_my_games_vs_reality(my_games, historical))

    # Test 5: Contraintes
    results.append(test_sum_constraints_compliance(my_games))

    # Sauvegarder
    save_results(results)

    # Synthèse
    print("\n" + "=" * 60)
    print("📋 SYNTHÈSE")
    print("=" * 60)

    test1 = results[0]
    test3 = results[2]
    test4 = results[3]

    print(f"\n✅ Tirages EuroMillions:")
    if test1.get('is_uniform'):
        print("   - Distribution uniforme confirmée")
    if test3.get('is_independent'):
        print("   - Indépendance temporelle confirmée")

    print(f"\n🎮 Mes jeux:")
    if not test4.get('is_similar'):
        print("   - ❌ Dévient significativement des tirages réels")
        print("   - ➡️  BIAIS dans la sélection des numéros détecté")
    else:
        print("   - ✅ Similaires aux tirages réels")

    print("\n➡️  Prochaine étape: python src/05_backtesting.py")


if __name__ == "__main__":
    main()
