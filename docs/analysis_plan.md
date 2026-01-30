# Plan d'Analyse EuroMillions

## Objectif du Projet

Transformer un système d'analyse Excel artisanal (223 onglets) en pipeline Python reproductible pour :
1. Valider/invalider les méthodes analytiques
2. Quantifier le paradoxe "gagner plus souvent, perdre plus d'argent"
3. Créer un portfolio Kaggle démontrant compétences data science
4. Documenter les biais cognitifs identifiés

---

## Phase 1 : Extraction & Nettoyage des Données

### 1.1 Source de données

**Fichier** : `data/raw/DataAnalyseModelPredictif-15_08_23.xlsx`

**Contenu attendu** :
- Onglet "Historique Tirages" : Tous les tirages EuroMillions (2004-2023)
- Onglet "Mes Jeux" : Les 133 jeux joués + résultats
- Onglets "Méthode 1-8" : Analyses Excel par méthode

**Structure des colonnes (Historique Tirages)** :
```
| Date       | Draw | B1 | B2 | B3 | B4 | B5 | E1 | E2 |
|------------|------|----|----|----|----|----|----|-----|
| 2004-02-13 | 1    | 8  | 12 | 29 | 34 | 48 | 2  | 7   |
| ...        | ...  | .. | .. | .. | .. | .. | .. | ..  |
```

**Structure des colonnes (Mes Jeux)** :
```
| Date_Jeu   | B1 | B2 | B3 | B4 | B5 | E1 | E2 | Rang | Gain_CHF |
|------------|----|----|----|----|----|----|-----|------|----------|
| 2020-03-15 | 7  | 13 | 22 | 38 | 45 | 3  | 9   | 13   | 4.00     |
| ...        | .. | .. | .. | .. | .. | .. | ..  | ...  | ...      |
```

### 1.2 Script d'extraction (`01_extract_data.py`)

**Entrée** : Excel multi-onglets
**Sortie** : 3 fichiers CSV
- `data/processed/historical_draws.csv`
- `data/processed/my_games.csv`
- `data/processed/metadata.json` (stats générales)

**Actions** :
1. Charger Excel avec `openpyxl` ou `pandas.read_excel()`
2. Identifier les onglets pertinents (pattern matching)
3. Valider structure des colonnes
4. Exporter en CSV UTF-8

**Métrics de validation** :
- Nombre de tirages attendus : ~1000+
- Nombre de jeux joués : 133
- Colonnes obligatoires présentes : `['Date', 'B1', ..., 'E2']`

---

## Phase 2 : Nettoyage & Validation (`02_clean_data.py`)

### 2.1 Vérifications d'intégrité

#### Tirages historiques
```python
# Valider ranges
assert all(1 <= draws[f'B{i}'] <= 50 for i in range(1, 6))
assert all(1 <= draws[f'E{i}'] <= 12 for i in range(1, 3))

# Pas de doublons
assert draws['Draw'].is_unique

# Chronologie
assert draws['Date'].is_monotonic_increasing

# Pas de valeurs manquantes
assert draws.notna().all().all()
```

#### Mes jeux
```python
# Total investi = 133 × 3.50 CHF
assert len(my_games) == 133
expected_investment = 133 * 3.50
actual_investment = 133 * 3.50  # Toujours vrai si constant

# Gains valides
assert all(my_games['Gain_CHF'] >= 0)

# Rangs valides
assert all(my_games['Rang'].isin(range(1, 14)))
```

### 2.2 Feature Engineering

Créer colonnes dérivées :

```python
# Somme des boules
draws['Sum_Balls'] = draws[['B1', 'B2', 'B3', 'B4', 'B5']].sum(axis=1)

# Parité
draws['Even_Count'] = draws[['B1', 'B2', 'B3', 'B4', 'B5']].apply(
    lambda row: sum(x % 2 == 0 for x in row), axis=1
)

# Écarts entre numéros
draws['Max_Gap'] = draws[['B1', 'B2', 'B3', 'B4', 'B5']].apply(
    lambda row: max(np.diff(sorted(row))), axis=1
)

# Contient 13 ?
draws['Has_13'] = draws[['B1', 'B2', 'B3', 'B4', 'B5']].apply(
    lambda row: 13 in row.values, axis=1
)
```

**Sortie** : `data/processed/clean_draws.csv`, `data/processed/clean_my_games.csv`

---

## Phase 3 : Analyse des 133 Jeux Réels (`03_analyze_games.py`)

### 3.1 Statistiques descriptives

#### ROI global
```python
total_invested = 133 * 3.50  # 465.50 CHF
total_won = my_games['Gain_CHF'].sum()
roi = (total_won - total_invested) / total_invested * 100
print(f"ROI: {roi:.2f}%")  # Attendu: -61.3%
```

#### Distribution des rangs
```python
rank_distribution = my_games['Rang'].value_counts().sort_index()

# Comparaison avec probabilités théoriques
theoretical_probs = {
    13: 1/22,
    12: 1/49,
    11: 1/188,
    # ... (voir config.md)
}

for rank, prob in theoretical_probs.items():
    expected_wins = 133 * prob
    observed_wins = rank_distribution.get(rank, 0)
    ratio = observed_wins / expected_wins if expected_wins > 0 else 0
    print(f"Rang {rank}: {observed_wins:.0f} obs vs {expected_wins:.2f} att (ratio: {ratio:.2f}x)")
```

**Résultat attendu** :
```
Rang 13: 44 obs vs 13.36 att (ratio: 3.3x)  ← Paradoxe !
Rang 12: 12 obs vs 5.44 att  (ratio: 2.2x)
Rang 11: 8 obs vs 1.42 att   (ratio: 5.6x)
Rang 1-10: 0 obs             (jackpot jamais gagné)
```

### 3.2 Analyse temporelle

#### Évolution du ROI cumulé
```python
my_games['Cumulative_Invested'] = my_games.index * 3.50
my_games['Cumulative_Won'] = my_games['Gain_CHF'].cumsum()
my_games['Cumulative_ROI'] = (
    (my_games['Cumulative_Won'] - my_games['Cumulative_Invested']) /
    my_games['Cumulative_Invested'] * 100
)

# Plot
plt.plot(my_games['Cumulative_ROI'])
plt.axhline(y=-50, color='r', linestyle='--', label='Théorique')
plt.xlabel('Nombre de jeux')
plt.ylabel('ROI cumulé (%)')
plt.title('Évolution du ROI : Espoir et Désillusion')
plt.savefig('outputs/figures/roi_evolution.png')
```

#### Streaks de pertes/gains
```python
# Identifier plus longue série de pertes consécutives
my_games['Loss'] = my_games['Gain_CHF'] == 0
longest_loss_streak = (
    my_games['Loss']
    .groupby((my_games['Loss'] != my_games['Loss'].shift()).cumsum())
    .sum()
    .max()
)
print(f"Plus longue série de pertes: {longest_loss_streak} jeux")
```

### 3.3 Analyse des numéros joués

#### Fréquence des numéros dans mes jeux
```python
all_my_numbers = my_games[['B1', 'B2', 'B3', 'B4', 'B5']].values.flatten()
my_freq = pd.Series(all_my_numbers).value_counts().sort_index()

# Comparaison avec distribution uniforme attendue
expected_freq = 133 * 5 / 50  # ~13.3 apparitions par numéro

plt.bar(range(1, 51), my_freq, alpha=0.7, label='Mes jeux')
plt.axhline(y=expected_freq, color='r', linestyle='--', label='Uniforme')
plt.xlabel('Numéro')
plt.ylabel('Fréquence')
plt.title('Distribution des numéros joués vs uniforme')
plt.savefig('outputs/figures/my_numbers_distribution.png')
```

**Observation attendue** : Pic massif sur le 13 (133 apparitions = 100%).

---

## Phase 4 : Tests Statistiques (`04_statistical_tests.py`)

### 4.1 Test d'uniformité (Chi-2)

**Hypothèse nulle** : Les tirages EuroMillions suivent une distribution uniforme.

```python
from scipy.stats import chisquare

# Fréquence de chaque numéro dans l'historique
historical_numbers = clean_draws[['B1', 'B2', 'B3', 'B4', 'B5']].values.flatten()
observed_freq = pd.Series(historical_numbers).value_counts().sort_index()

# Fréquence attendue (uniforme)
total_draws = len(clean_draws)
expected_freq = np.full(50, total_draws * 5 / 50)

# Test Chi-2
chi2_stat, p_value = chisquare(observed_freq, expected_freq)

print(f"Chi-2: {chi2_stat:.4f}, p-value: {p_value:.4e}")
if p_value > 0.05:
    print("✅ Distribution uniforme (tirages aléatoires)")
else:
    print("❌ Déviation significative détectée")
```

### 4.2 Test d'indépendance (Autocorrélation)

**Hypothèse nulle** : Les tirages sont indépendants (pas de corrélation temporelle).

```python
from statsmodels.graphics.tsaplots import plot_acf

# Prendre un numéro arbitraire (ex: 13)
num_13_present = clean_draws['Has_13'].astype(int)

plot_acf(num_13_present, lags=50)
plt.title('Autocorrélation: Présence du 13')
plt.savefig('outputs/figures/autocorrelation_13.png')
```

**Résultat attendu** : Aucune corrélation significative (tirages indépendants).

### 4.3 Test Kolmogorov-Smirnov (distribution sommes)

```python
from scipy.stats import kstest

# Distribution observée des sommes
observed_sums = clean_draws['Sum_Balls']

# Distribution théorique (normale μ=127.5, σ=20)
from scipy.stats import norm
theoretical_distribution = norm(loc=127.5, scale=20)

ks_stat, p_value = kstest(observed_sums, theoretical_distribution.cdf)

print(f"KS stat: {ks_stat:.4f}, p-value: {p_value:.4e}")
```

### 4.4 Comparaison "Mes jeux" vs "Aléatoire"

**Test** : Les numéros que j'ai joués suivent-ils la même distribution que les tirages réels ?

```python
# Fréquence de mes numéros
my_numbers_freq = pd.Series(all_my_numbers).value_counts().sort_index()

# Fréquence des tirages réels (normalisée)
real_freq_normalized = observed_freq / observed_freq.sum() * len(all_my_numbers)

# Test Chi-2
chi2, p = chisquare(my_numbers_freq, real_freq_normalized)

print(f"Mes jeux vs Réalité: Chi-2={chi2:.2f}, p={p:.4f}")
if p < 0.05:
    print("❌ Mes choix dévient significativement de l'aléatoire")
```

---

## Phase 5 : Backtesting (`05_backtesting.py`)

### 5.1 Objectif

Simuler **10,000 jeux** selon deux profils :
1. **Profil "Julien"** : Applique les 8 méthodes (basé sur analyse des 133 jeux réels)
2. **Profil "Aléatoire"** : Sélection purement aléatoire

**Question** : Le profil "Julien" maximise-t-il les petits gains au détriment des gros ?

### 5.2 Implémentation du profil "Julien"

```python
def generate_julien_style_game(historical_draws: pd.DataFrame) -> List[int]:
    """
    Génère une combinaison style Julien (8 méthodes).

    Returns:
        Liste de 5 numéros triés
    """
    # Étape 1: Calculer scores
    recurrence = calculate_recurrence_amplitude_score(historical_draws)
    gaps = calculate_gap_scores(historical_draws)
    ma = calculate_moving_averages(historical_draws)

    # Étape 2: Combiner (moyenne pondérée)
    combined = {
        num: 0.4 * recurrence[num] + 0.3 * gaps[num] + 0.3 * ma[num]
        for num in range(1, 51)
    }

    # Étape 3: Sélectionner top numéros
    candidates = sorted(combined, key=combined.get, reverse=True)

    # Étape 4: Appliquer contraintes
    for i in range(0, 45):  # Essayer différentes combinaisons
        combo = candidates[i:i+5]

        if not (90 <= sum(combo) <= 150):  # Méthode 2
            continue
        if not validate_compartments(combo):  # Méthode 6
            continue
        if not validate_parity_divisibility(combo):  # Méthode 7
            continue

        # Méthode 8: Forcer 13
        if 13 not in combo:
            combo = list(combo)
            combo[-1] = 13

        return sorted(combo)

    # Fallback: aléatoire si aucune combinaison valide
    return sorted(random.sample(range(1, 51), 5))
```

### 5.3 Simulation Monte Carlo

```python
def simulate_games(
    n_games: int,
    profile: str,  # 'julien' ou 'random'
    historical_draws: pd.DataFrame
) -> pd.DataFrame:
    """
    Simule n_games selon le profil spécifié.

    Returns:
        DataFrame avec colonnes [B1, B2, B3, B4, B5, Rank, Gain_CHF]
    """
    results = []

    for _ in range(n_games):
        # Générer combinaison
        if profile == 'julien':
            combo = generate_julien_style_game(historical_draws)
        else:
            combo = sorted(random.sample(range(1, 51), 5))

        # Simuler tirage réel (aléatoire)
        real_draw = sorted(random.sample(range(1, 51), 5))
        real_stars = sorted(random.sample(range(1, 13), 2))

        # Calculer rang
        matches = len(set(combo) & set(real_draw))
        # (Simplification: ignorer étoiles pour analyse boules)

        rank = get_rank_from_matches(matches)
        gain = PRIZE_RANKS[rank]['avg_prize_CHF'] if rank in PRIZE_RANKS else 0

        results.append({
            'B1': combo[0], 'B2': combo[1], 'B3': combo[2],
            'B4': combo[3], 'B5': combo[4],
            'Rank': rank, 'Gain_CHF': gain
        })

    return pd.DataFrame(results)
```

### 5.4 Analyse comparative

```python
# Simuler
julien_results = simulate_games(10000, 'julien', clean_draws)
random_results = simulate_games(10000, 'random', clean_draws)

# Comparer ROI
julien_roi = (julien_results['Gain_CHF'].sum() - 10000 * 3.50) / (10000 * 3.50) * 100
random_roi = (random_results['Gain_CHF'].sum() - 10000 * 3.50) / (10000 * 3.50) * 100

print(f"ROI Julien: {julien_roi:.2f}%")
print(f"ROI Random: {random_roi:.2f}%")

# Comparer distribution rangs
julien_ranks = julien_results['Rank'].value_counts()
random_ranks = random_results['Rank'].value_counts()

comparison = pd.DataFrame({
    'Julien': julien_ranks,
    'Random': random_ranks,
    'Ratio': julien_ranks / random_ranks
})
print(comparison.sort_index())
```

**Hypothèse à tester** :
- Julien a plus de rangs 11-13 (petits gains)
- Julien a moins de rangs 1-5 (gros gains)
- ROI similaire (~-50%) mais variance différente

---

## Phase 6 : Visualisations (`06_visualizations.py`)

### 6.1 Heatmap: Fréquence des numéros

```python
import seaborn as sns

# Créer matrice 5×10 (numéros 1-50)
freq_matrix = my_freq.values.reshape(5, 10)

sns.heatmap(freq_matrix, annot=True, fmt='d', cmap='YlOrRd')
plt.title('Fréquence des numéros joués (mes 133 jeux)')
plt.savefig('outputs/figures/heatmap_my_numbers.png', dpi=150)
```

### 6.2 Timeline: ROI cumulé

(Déjà implémenté en Phase 3.2)

### 6.3 Distribution des sommes

```python
plt.hist(clean_draws['Sum_Balls'], bins=50, alpha=0.7, label='Tirages réels')
plt.axvline(x=120, color='r', linestyle='--', label='Cible (config)')
plt.xlabel('Somme des 5 boules')
plt.ylabel('Fréquence')
plt.title('Distribution des sommes: Réalité vs Contrainte')
plt.legend()
plt.savefig('outputs/figures/sum_distribution.png')
```

### 6.4 Comparaison backtesting

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Subplot 1: Distribution rangs
axes[0].bar(comparison.index - 0.2, comparison['Julien'], width=0.4, label='Julien', alpha=0.7)
axes[0].bar(comparison.index + 0.2, comparison['Random'], width=0.4, label='Random', alpha=0.7)
axes[0].set_xlabel('Rang')
axes[0].set_ylabel('Nombre de gains')
axes[0].set_title('Distribution des rangs (10k jeux)')
axes[0].legend()

# Subplot 2: Ratio Julien/Random
axes[1].bar(comparison.index, comparison['Ratio'], color='purple', alpha=0.7)
axes[1].axhline(y=1, color='r', linestyle='--', label='Égalité')
axes[1].set_xlabel('Rang')
axes[1].set_ylabel('Ratio Julien/Random')
axes[1].set_title('Sur-/Sous-performance par rang')
axes[1].legend()

plt.tight_layout()
plt.savefig('outputs/figures/backtesting_comparison.png', dpi=150)
```

---

## Livrables Finaux

### 1. Rapport technique (`outputs/final_report.md`)

Structure :
```markdown
# Rapport Final : EuroMillions Analysis

## 1. Executive Summary
- ROI observé : -61.3%
- Paradoxe identifié : Taux réussite +240%, ROI -22%
- Conclusion : Méthodes inefficaces

## 2. Méthodologie
- 8 méthodes documentées
- 133 jeux réels analysés
- 10k simulations backtestées

## 3. Résultats
### 3.1 Analyse réelle
- [Tableaux, graphiques]

### 3.2 Backtesting
- [Comparaison Julien vs Random]

### 3.3 Tests statistiques
- Chi-2: p=0.XX → Uniformité confirmée
- KS: p=0.XX → Distribution normale OK

## 4. Biais cognitifs identifiés
- Sunk cost fallacy
- Gambler's fallacy
- Confirmation bias

## 5. Leçons apprises
- Compétences transférables
- Importance de la rigueur
- Humilité statistique

## 6. Recommandations
- NE PAS jouer selon ces méthodes
- Considérer loterie comme divertissement
- Investir temps dans learning, pas gambling
```

### 2. Notebook Jupyter (`notebooks/exploratory_analysis.ipynb`)

Sections :
1. Import & exploration données
2. Tests statistiques interactifs
3. Visualisations dynamiques (Plotly)
4. Simulation backtesting en temps réel

### 3. Fichiers d'outputs

```
outputs/
├── figures/
│   ├── roi_evolution.png
│   ├── heatmap_my_numbers.png
│   ├── sum_distribution.png
│   ├── backtesting_comparison.png
│   └── autocorrelation_13.png
├── reports/
│   ├── summary_stats.csv
│   ├── rank_distribution.csv
│   └── backtesting_results.json
└── final_report.md
```

---

## Timeline d'Exécution

| Phase | Script | Temps estimé | Dépendances |
|-------|--------|--------------|-------------|
| 1 | `01_extract_data.py` | 5 min | Excel présent |
| 2 | `02_clean_data.py` | 10 min | Phase 1 OK |
| 3 | `03_analyze_games.py` | 15 min | Phase 2 OK |
| 4 | `04_statistical_tests.py` | 10 min | Phase 2 OK |
| 5 | `05_backtesting.py` | 30 min | Phase 2 OK, utils.py |
| 6 | `06_visualizations.py` | 20 min | Phases 3-5 OK |

**Total** : ~1h30 (hors rédaction rapport final)

---

## Prochaines Étapes

1. ✅ Placer `DataAnalyseModelPredictif-15_08_23.xlsx` dans `data/raw/`
2. ▶️ Exécuter scripts séquentiellement
3. ▶️ Rédiger `final_report.md`
4. ▶️ Créer notebook interactif
5. ▶️ Upload sur Kaggle
6. ▶️ Partager sur LinkedIn avec narrative

---

**Dernière mise à jour** : Janvier 2025
