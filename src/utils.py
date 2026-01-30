"""
Fonctions utilitaires pour l'analyse EuroMillions.

Ce module contient toutes les fonctions réutilisables :
- Calcul des scores (Méthodes 1, 4, 5)
- Validation des contraintes (Méthodes 2, 3, 6, 7, 8)
- Helpers de génération de combinaisons
- Configuration globale
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import random
from scipy.stats import norm


# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

# Règles du jeu
N_BALLS = 5
BALL_MIN = 1
BALL_MAX = 50
N_STARS = 2
STAR_MIN = 1
STAR_MAX = 12
GRID_COST_CHF = 3.50

# Méthode 2: Contraintes de somme
SUM_MIN = 90
SUM_MAX = 150
SUM_TARGET = 120

# Méthode 4: Écarts
GAP_THRESHOLD_MULTIPLIER = 1.5

# Méthode 5: Moving Averages
MA_WINDOWS = [7, 14, 21]

# Méthode 6: Compartiments
COMPARTMENTS = {
    1: (1, 10),
    2: (11, 20),
    3: (21, 30),
    4: (31, 40),
    5: (41, 50)
}

COMPARTMENT_QUOTAS = {
    1: (0, 2),
    2: (0, 2),
    3: (1, 2),  # Zone préférée
    4: (0, 2),
    5: (0, 2)
}

# Méthode 7: Parité
PARITY_MIN_EVEN = 1
PARITY_MAX_EVEN = 4

# Méthode 8: Numéro sacré
SACRED_NUMBER = 13

# Probabilités théoriques des rangs
PRIZE_RANKS = {
    1:  {"match": "5+2", "probability": 1/139838160, "avg_prize_CHF": 50000000},
    2:  {"match": "5+1", "probability": 1/6991908,   "avg_prize_CHF": 300000},
    3:  {"match": "5+0", "probability": 1/3107515,   "avg_prize_CHF": 50000},
    4:  {"match": "4+2", "probability": 1/621503,    "avg_prize_CHF": 3000},
    5:  {"match": "4+1", "probability": 1/31075,     "avg_prize_CHF": 150},
    6:  {"match": "3+2", "probability": 1/14125,     "avg_prize_CHF": 80},
    7:  {"match": "4+0", "probability": 1/13811,     "avg_prize_CHF": 60},
    8:  {"match": "2+2", "probability": 1/985,       "avg_prize_CHF": 20},
    9:  {"match": "3+1", "probability": 1/706,       "avg_prize_CHF": 15},
    10: {"match": "3+0", "probability": 1/314,       "avg_prize_CHF": 12},
    11: {"match": "1+2", "probability": 1/188,       "avg_prize_CHF": 8},
    12: {"match": "2+1", "probability": 1/49,        "avg_prize_CHF": 5},
    13: {"match": "2+0", "probability": 1/22,        "avg_prize_CHF": 4}
}


# ============================================================================
# MÉTHODE 1: RÉCURRENCE + AMPLITUDE
# ============================================================================

def calculate_recurrence_amplitude_score(
    draws: pd.DataFrame,
    window_size: int = 7,
    alpha: float = 0.5,
    beta: float = 0.5
) -> Dict[int, float]:
    """
    Calcule le score récurrence + amplitude pour chaque numéro.

    La récurrence mesure la fréquence d'apparition sur une fenêtre glissante.
    L'amplitude favorise les numéros proches de la médiane de la fenêtre.

    Args:
        draws: DataFrame avec colonnes ['B1', 'B2', 'B3', 'B4', 'B5']
        window_size: Taille de la fenêtre glissante (défaut: 7)
        alpha: Poids de la récurrence (défaut: 0.5)
        beta: Poids de l'amplitude (défaut: 0.5)

    Returns:
        Dict {numéro: score} pour numéros 1-50
    """
    # Extraire fenêtre
    window = draws.tail(window_size)
    numbers = window[['B1', 'B2', 'B3', 'B4', 'B5']].values.flatten()

    # Calculer fréquence
    frequency = {i: np.sum(numbers == i) / len(numbers) for i in range(1, 51)}

    # Calculer amplitude
    median = np.median(numbers)
    range_val = np.ptp(numbers)  # Peak-to-peak

    amplitude = {
        i: 1 - abs(i - median) / range_val if range_val > 0 else 0
        for i in range(1, 51)
    }

    # Combiner
    scores = {
        i: alpha * frequency[i] + beta * amplitude[i]
        for i in range(1, 51)
    }

    return scores


# ============================================================================
# MÉTHODE 2: VALIDATION PAR SOMME
# ============================================================================

def validate_sum(combination: List[int]) -> bool:
    """
    Vérifie si la somme des boules respecte les contraintes.

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si somme ∈ [SUM_MIN, SUM_MAX], False sinon
    """
    total = sum(combination)
    return SUM_MIN <= total <= SUM_MAX


# ============================================================================
# MÉTHODE 3: UNICITÉ
# ============================================================================

def is_unique(
    combination: List[int],
    historical_draws: pd.DataFrame
) -> bool:
    """
    Vérifie si la combinaison n'est jamais sortie dans l'historique.

    Args:
        combination: Liste de 5 numéros
        historical_draws: DataFrame des tirages passés

    Returns:
        True si unique, False si déjà sortie
    """
    combo_sorted = sorted(combination)

    for _, row in historical_draws.iterrows():
        draw = sorted([row['B1'], row['B2'], row['B3'], row['B4'], row['B5']])
        if draw == combo_sorted:
            return False

    return True


# ============================================================================
# MÉTHODE 4: ANALYSE DES ÉCARTS
# ============================================================================

def calculate_gap_scores(
    draws: pd.DataFrame,
    current_draw_number: int
) -> Dict[int, float]:
    """
    Calcule le score d'écart pour chaque numéro.

    Un numéro avec écart actuel > écart moyen est considéré "en retard".

    Args:
        draws: DataFrame avec colonnes ['Draw', 'B1', ..., 'B5']
        current_draw_number: Numéro du tirage actuel

    Returns:
        Dict {numéro: score_gap}
    """
    scores = {}

    for num in range(1, 51):
        # Trouver tous les tirages où num apparaît
        mask = (draws[['B1', 'B2', 'B3', 'B4', 'B5']] == num).any(axis=1)
        appearances = draws.loc[mask, 'Draw'].values

        if len(appearances) == 0:
            scores[num] = 0
            continue

        # Calculer gaps entre apparitions
        gaps = np.diff(appearances)
        avg_gap = np.mean(gaps) if len(gaps) > 0 else 1

        # Gap actuel
        current_gap = current_draw_number - appearances[-1]

        # Score = ratio (normalisé)
        scores[num] = current_gap / avg_gap if avg_gap > 0 else 0

    return scores


# ============================================================================
# MÉTHODE 5: MOVING AVERAGES
# ============================================================================

def calculate_moving_averages(
    draws: pd.DataFrame,
    window: int = 7
) -> Dict[int, float]:
    """
    Calcule la moyenne mobile de fréquence pour chaque numéro.

    Args:
        draws: DataFrame des tirages
        window: Taille de la fenêtre (défaut: 7)

    Returns:
        Dict {numéro: fréquence_moyenne}
    """
    scores = {}
    recent_draws = draws.tail(window)

    for num in range(1, 51):
        mask = (recent_draws[['B1', 'B2', 'B3', 'B4', 'B5']] == num).any(axis=1)
        frequency = mask.sum() / window
        scores[num] = frequency

    return scores


# ============================================================================
# MÉTHODE 6: COMPARTIMENTALISATION
# ============================================================================

def validate_compartments(combination: List[int]) -> bool:
    """
    Vérifie si la combinaison respecte les quotas par zone.

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si quotas respectés
    """
    counts = {zone_id: 0 for zone_id in COMPARTMENTS}

    for num in combination:
        for zone_id, (low, high) in COMPARTMENTS.items():
            if low <= num <= high:
                counts[zone_id] += 1

    # Vérifier quotas
    for zone_id, (min_quota, max_quota) in COMPARTMENT_QUOTAS.items():
        if not (min_quota <= counts[zone_id] <= max_quota):
            return False

    return True


# ============================================================================
# MÉTHODE 7: PARITÉ & DIVISIBILITÉ
# ============================================================================

def validate_parity_divisibility(combination: List[int]) -> bool:
    """
    Vérifie les contraintes de parité et divisibilité.

    Contraintes:
    - 1-4 numéros pairs
    - Au moins 1 multiple de 3
    - Au moins 1 multiple de 5

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si contraintes respectées
    """
    even_count = sum(1 for n in combination if n % 2 == 0)
    div_3 = sum(1 for n in combination if n % 3 == 0)
    div_5 = sum(1 for n in combination if n % 5 == 0)

    # Vérifier parité
    if not (PARITY_MIN_EVEN <= even_count <= PARITY_MAX_EVEN):
        return False

    # Vérifier divisibilité
    if div_3 < 1 or div_5 < 1:
        return False

    return True


# ============================================================================
# MÉTHODE 8: NUMÉRO SACRÉ
# ============================================================================

def force_include_sacred(combination: List[int]) -> List[int]:
    """
    Force l'inclusion du numéro sacré (13).

    Si 13 absent, remplace le dernier numéro de la combinaison.

    Args:
        combination: Liste de 5 numéros

    Returns:
        Combinaison modifiée avec 13
    """
    if SACRED_NUMBER not in combination:
        combination = list(combination)
        combination[-1] = SACRED_NUMBER

    return sorted(combination)


# ============================================================================
# GÉNÉRATION DE COMBINAISONS
# ============================================================================

def generate_combination_julien_style(
    historical_draws: pd.DataFrame,
    max_attempts: int = 1000
) -> List[int]:
    """
    Génère une combinaison selon le style Julien (8 méthodes).

    Pipeline:
    1. Calculer scores (Méthodes 1, 4, 5)
    2. Combiner scores (moyenne pondérée)
    3. Sélectionner candidats
    4. Appliquer contraintes (Méthodes 2, 3, 6, 7, 8)

    Args:
        historical_draws: DataFrame des tirages historiques
        max_attempts: Nombre max de tentatives (défaut: 1000)

    Returns:
        Liste de 5 numéros triés
    """
    # Étape 1: Calculer scores
    current_draw_number = len(historical_draws) + 1
    recurrence_scores = calculate_recurrence_amplitude_score(historical_draws)
    gap_scores = calculate_gap_scores(historical_draws, current_draw_number)
    ma_scores = calculate_moving_averages(historical_draws, window=7)

    # Étape 2: Combiner (pondération)
    combined = {
        num: (
            0.4 * recurrence_scores[num] +
            0.3 * gap_scores[num] +
            0.3 * ma_scores[num]
        )
        for num in range(1, 51)
    }

    # Trier par score décroissant
    sorted_candidates = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    # Étape 3: Essayer différentes combinaisons
    for attempt in range(max_attempts):
        # Sélectionner top 5 + aléa pour diversité
        start_idx = attempt % 10  # Décaler fenêtre
        candidates = [num for num, _ in sorted_candidates[start_idx:start_idx+5]]

        if len(candidates) < 5:  # Fallback si pas assez
            candidates = random.sample(range(1, 51), 5)

        # Étape 4: Appliquer contraintes
        if not validate_sum(candidates):
            continue

        if not is_unique(candidates, historical_draws):
            continue

        if not validate_compartments(candidates):
            continue

        if not validate_parity_divisibility(candidates):
            continue

        # Forcer 13
        candidates = force_include_sacred(candidates)

        return sorted(candidates)

    # Si aucune combinaison valide après max_attempts → aléatoire
    fallback = random.sample(range(1, 51), 5)
    return force_include_sacred(fallback)


def generate_combination_random() -> List[int]:
    """
    Génère une combinaison purement aléatoire.

    Returns:
        Liste de 5 numéros triés
    """
    return sorted(random.sample(range(1, 51), 5))


# ============================================================================
# CALCUL DU RANG
# ============================================================================

def calculate_rank(
    played: List[int],
    played_stars: List[int],
    drawn: List[int],
    drawn_stars: List[int]
) -> int:
    """
    Calcule le rang gagné selon les correspondances.

    Args:
        played: 5 boules jouées
        played_stars: 2 étoiles jouées
        drawn: 5 boules tirées
        drawn_stars: 2 étoiles tirées

    Returns:
        Rang (1-13) ou 0 si aucun gain
    """
    balls_match = len(set(played) & set(drawn))
    stars_match = len(set(played_stars) & set(drawn_stars))

    rank_map = {
        (5, 2): 1,
        (5, 1): 2,
        (5, 0): 3,
        (4, 2): 4,
        (4, 1): 5,
        (3, 2): 6,
        (4, 0): 7,
        (2, 2): 8,
        (3, 1): 9,
        (3, 0): 10,
        (1, 2): 11,
        (2, 1): 12,
        (2, 0): 13
    }

    return rank_map.get((balls_match, stars_match), 0)


def get_prize_for_rank(rank: int) -> float:
    """
    Retourne le gain moyen pour un rang donné.

    Args:
        rank: Rang (1-13)

    Returns:
        Gain en CHF (0 si rang invalide)
    """
    return PRIZE_RANKS.get(rank, {}).get('avg_prize_CHF', 0)


# ============================================================================
# STATISTIQUES
# ============================================================================

def calculate_roi(total_invested: float, total_won: float) -> float:
    """
    Calcule le ROI (Return on Investment).

    Args:
        total_invested: Montant total investi (CHF)
        total_won: Montant total gagné (CHF)

    Returns:
        ROI en pourcentage
    """
    if total_invested == 0:
        return 0.0

    return ((total_won - total_invested) / total_invested) * 100


def expected_wins_for_rank(rank: int, n_games: int) -> float:
    """
    Calcule le nombre attendu de gains pour un rang donné.

    Args:
        rank: Rang (1-13)
        n_games: Nombre de jeux joués

    Returns:
        Nombre attendu de gains (float)
    """
    probability = PRIZE_RANKS.get(rank, {}).get('probability', 0)
    return n_games * probability


# ============================================================================
# HELPERS
# ============================================================================

def ensure_directories():
    """
    Crée les répertoires nécessaires s'ils n'existent pas.
    """
    import os

    dirs = [
        'data/raw',
        'data/processed',
        'outputs/figures',
        'outputs/reports',
        'notebooks'
    ]

    for directory in dirs:
        os.makedirs(directory, exist_ok=True)


if __name__ == "__main__":
    # Tests unitaires basiques
    print("🧪 Tests utils.py\n")

    # Test Méthode 2
    assert validate_sum([10, 20, 30, 40, 50]) == True  # Somme = 150
    assert validate_sum([1, 2, 3, 4, 5]) == False  # Somme = 15
    print("✅ Méthode 2: Validation somme OK")

    # Test Méthode 7
    assert validate_parity_divisibility([3, 5, 13, 20, 30]) == True
    assert validate_parity_divisibility([1, 7, 11, 13, 17]) == False  # Pas de pair
    print("✅ Méthode 7: Parité/divisibilité OK")

    # Test Méthode 8
    combo_without_13 = [5, 10, 15, 20, 25]
    result = force_include_sacred(combo_without_13)
    assert 13 in result
    print("✅ Méthode 8: Numéro sacré OK")

    # Test calcul rang
    rank = calculate_rank([1, 2, 3, 4, 5], [1, 2], [1, 2, 6, 7, 8], [1, 3])
    assert rank == 12  # 2 boules + 1 étoile
    print("✅ Calcul rang OK")

    # Test ROI
    roi = calculate_roi(100, 50)
    assert roi == -50.0
    print("✅ Calcul ROI OK")

    print("\n🎉 Tous les tests passent !")
