# Configuration du Projet

## Paramètres Globaux

### Dataset EuroMillions
```python
DATA_SOURCE = "data/raw/DataAnalyseModelPredictif-15_08_23.xlsx"
DRAWS_START_DATE = "2004-02-13"  # Premier tirage EuroMillions
DRAWS_END_DATE = "2023-08-15"    # Dernier tirage dans dataset
TOTAL_DRAWS = 1000+              # Nombre approximatif de tirages
```

### Règles du Jeu
```python
# Boules principales
N_BALLS = 5
BALL_MIN = 1
BALL_MAX = 50

# Étoiles
N_STARS = 2
STAR_MIN = 1
STAR_MAX = 12

# Coûts
GRID_COST_CHF = 3.50  # Prix par grille en Suisse
```

### Contraintes Analytiques

#### Méthode 1 : Récurrence + Amplitude
```python
RECURRENCE_WINDOWS = [7, 14, 21]  # Nombre de tirages pour fenêtre glissante
AMPLITUDE_WEIGHT = 0.5            # Poids de la composante amplitude
RECURRENCE_WEIGHT = 0.5           # Poids de la composante récurrence
```

#### Méthode 2 : Validation par Somme
```python
SUM_MIN = 90   # Somme minimale des 5 boules
SUM_MAX = 150  # Somme maximale des 5 boules
SUM_TARGET = 120  # Cible idéale (approximativement)
```

#### Méthode 3 : Unicité
```python
CHECK_DUPLICATES = True
HISTORICAL_DEPTH = 1000  # Nombre de tirages à vérifier pour unicité
```

#### Méthode 4 : Analyse des Écarts
```python
GAP_THRESHOLD_MULTIPLIER = 1.5  # Seuil = Écart moyen × ce facteur
PENALIZE_SHORT_GAPS = True      # Pénaliser numéros apparus récemment
```

#### Méthode 5 : Moving Averages
```python
MA_SHORT = 7   # Moyenne mobile courte terme
MA_MEDIUM = 21 # Moyenne mobile moyen terme
MA_LONG = 50   # Moyenne mobile long terme
```

#### Méthode 6 : Compartimentalisation
```python
COMPARTMENTS = {
    "Zone 1": (1, 10),
    "Zone 2": (11, 20),
    "Zone 3": (21, 30),
    "Zone 4": (31, 40),
    "Zone 5": (41, 50)
}

# Quotas par compartiment (nombre min/max de boules)
COMPARTMENT_QUOTAS = {
    "Zone 1": (0, 2),
    "Zone 2": (0, 2),
    "Zone 3": (1, 2),
    "Zone 4": (0, 2),
    "Zone 5": (0, 2)
}
```

#### Méthode 7 : Parité & Divisibilité
```python
# Parité
PARITY_MIN_EVEN = 1  # Min boules paires
PARITY_MAX_EVEN = 4  # Max boules paires

# Divisibilité
DIVISIBILITY_CHECKS = [3, 5, 7]
DIV_MIN_PER_TYPE = 1  # Min 1 multiple de chaque type
DIV_MAX_PER_TYPE = 2  # Max 2 multiples de chaque type
```

#### Méthode 8 : Numéro Sacré
```python
SACRED_NUMBER = 13
FORCE_INCLUDE = True  # Toujours inclure le 13
```

---

## Analyse des 133 Jeux Réels

### Période de Test
```python
REAL_GAMES_START = "2020-01-01"
REAL_GAMES_END = "2023-08-15"
TOTAL_GAMES_PLAYED = 133
TOTAL_INVESTED_CHF = 465.50  # 133 × 3.50
```

### Catégories de Gains (Rangs EuroMillions)
```python
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
```

---

## Backtesting

### Simulation Monte Carlo
```python
N_SIMULATIONS = 10000  # Nombre de jeux simulés

# Profil "Style Julien" (basé sur analyse des 133 jeux réels)
JULIEN_PROFILE = {
    "use_method_1": True,
    "use_method_2": True,
    "use_method_3": True,
    "use_method_4": True,
    "use_method_5": False,  # Rarement utilisée
    "use_method_6": True,
    "use_method_7": True,
    "use_method_8": True,   # Numéro sacré

    # Biais observés
    "preference_zone_3": 0.3,  # Préférence zone [21-30]
    "avoid_consecutive": 0.7,  # Évite numéros consécutifs (75% du temps)
    "balanced_parity": 0.8     # Équilibre pairs/impairs (80% du temps)
}

# Profil aléatoire (baseline)
RANDOM_PROFILE = {
    "use_method_1": False,
    # ... tous False
}
```

---

## Visualisations

### Types de Graphiques
```python
PLOT_CONFIG = {
    "dpi": 150,
    "figsize": (12, 8),
    "style": "seaborn-v0_8-darkgrid",
    "palette": "viridis"
}

PLOTS_TO_GENERATE = [
    "heatmap_frequency",           # Fréquence par numéro
    "timeseries_gaps",             # Évolution des écarts
    "distribution_sums",           # Distribution sommes
    "correlation_matrix",          # Corrélations inter-numéros
    "roi_evolution",               # ROI cumulé dans le temps
    "rank_distribution_comparison" # Distribution rangs: Julien vs Random
]
```

---

## Paths & Output

### Chemins de Fichiers
```python
PATHS = {
    "raw_data": "data/raw/",
    "processed_data": "data/processed/",
    "outputs": "outputs/",
    "figures": "outputs/figures/",
    "reports": "outputs/reports/",
    "docs": "docs/"
}
```

### Formats d'Export
```python
EXPORT_FORMATS = {
    "tables": "csv",      # CSV pour compatibilité maximale
    "figures": "png",     # PNG haute résolution
    "reports": "markdown" # Markdown pour Kaggle
}
```

---

## Notes de Développement

### Principes de Code
1. **Commentaires en français** sauf noms variables/fonctions (anglais)
2. **Fonctions pures** quand possible (input → output, pas d'effets de bord)
3. **Docstrings** style Google
4. **Type hints** Python 3.8+

### Exemple de Fonction
```python
def calculate_recurrence_score(
    numbers: List[int],
    window_size: int = 7
) -> Dict[int, float]:
    """
    Calcule le score de récurrence pour chaque numéro.

    Args:
        numbers: Liste des numéros tirés dans la fenêtre
        window_size: Taille de la fenêtre glissante

    Returns:
        Dictionnaire {numéro: score}

    Exemple:
        >>> calculate_recurrence_score([1, 2, 2, 3, 3, 3], window_size=6)
        {1: 0.167, 2: 0.333, 3: 0.500}
    """
    # Implementation...
```

---

**Dernière mise à jour** : Janvier 2025
