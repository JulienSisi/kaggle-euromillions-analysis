# 🚀 QUICKSTART — EuroMillions Analysis

Guide rapide pour exécuter le projet.

---

## 📋 Prérequis

### 1. Installer les dépendances

```bash
# Créer environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt
```

### 2. Placer le fichier Excel

**IMPORTANT** : Placer le fichier `DataAnalyseModelPredictif-15_08_23.xlsx` dans :

```
data/raw/DataAnalyseModelPredictif-15_08_23.xlsx
```

---

## ▶️ Exécution séquentielle

### Étape 1 : Extraction des données

```bash
python src/01_extract_data.py
```

**Sortie** :
- `data/processed/historical_draws.csv`
- `data/processed/my_games.csv`
- `data/processed/metadata.json`

---

### Étape 2 : Nettoyage et validation

```bash
python src/02_clean_data.py
```

**Sortie** :
- `data/processed/clean_draws.csv`
- `data/processed/clean_my_games.csv`
- `data/processed/validation_report.txt`

---

### Étape 3 : Analyse des 133 jeux

```bash
python src/03_analyze_games.py
```

**Sortie** :
- `outputs/reports/games_analysis.csv`
- `outputs/reports/rank_distribution.csv`
- `outputs/reports/number_frequency.csv`
- Console : Rapport détaillé avec ROI, paradoxe, etc.

---

### Étape 4 : Tests statistiques

```bash
python src/04_statistical_tests.py
```

**Sortie** :
- `outputs/reports/statistical_tests_results.txt`
- Console : Chi-2, KS test, autocorrélation

**Résultats attendus** :
- ✅ Tirages uniformes (Chi-2 p > 0.05)
- ✅ Indépendance temporelle (pas d'autocorrélation)
- ❌ Mes jeux dévient de l'aléatoire (biais détecté)

---

### Étape 5 : Backtesting (⏱️ ~5-10 min)

```bash
python src/05_backtesting.py
```

**Sortie** :
- `outputs/reports/backtesting_julien.csv` (10,000 jeux)
- `outputs/reports/backtesting_random.csv` (10,000 jeux)
- `outputs/reports/backtesting_comparison.csv`

**Hypothèse testée** :
> Les méthodes analytiques maximisent les petits gains au détriment des gros gains.

---

### Étape 6 : Visualisations

```bash
python src/06_visualizations.py
```

**Sortie** :
- `outputs/figures/roi_evolution.png`
- `outputs/figures/heatmap_frequency.png`
- `outputs/figures/sum_distribution.png`
- `outputs/figures/rank_distribution.png`
- `outputs/figures/number_frequency_comparison.png`
- `outputs/figures/autocorrelation_13.png`
- `outputs/figures/backtesting_comparison.png`

---

## 📊 Exécution complète (pipeline)

```bash
# Tout exécuter d'un coup
python src/01_extract_data.py && \
python src/02_clean_data.py && \
python src/03_analyze_games.py && \
python src/04_statistical_tests.py && \
python src/05_backtesting.py && \
python src/06_visualizations.py
```

**Temps total** : ~10-15 minutes

---

## 🧪 Tests unitaires (utils.py)

```bash
python src/utils.py
```

Vérifie que les fonctions utilitaires fonctionnent correctement.

---

## 📂 Structure des sorties

```
outputs/
├── figures/
│   ├── roi_evolution.png
│   ├── heatmap_frequency.png
│   ├── sum_distribution.png
│   ├── rank_distribution.png
│   ├── number_frequency_comparison.png
│   ├── autocorrelation_13.png
│   └── backtesting_comparison.png
└── reports/
    ├── games_analysis.csv
    ├── rank_distribution.csv
    ├── number_frequency.csv
    ├── statistical_tests_results.txt
    ├── backtesting_julien.csv
    ├── backtesting_random.csv
    └── backtesting_comparison.csv
```

---

## 🎯 Résultats attendus

### ROI observé (133 jeux réels)
- **Investissement** : 465.50 CHF
- **Gains** : ~180 CHF
- **ROI** : -61.3% (vs -50% théorique)

### Le Paradoxe
- Taux de réussite : **+240%** vs théorique
- ROI : **-22%** vs théorique
- **Conclusion** : Gagner plus souvent, mais perdre plus d'argent

### Distribution des rangs
- Rang 13 : **3.3x** plus fréquent
- Rang 11 : **7x** plus fréquent
- Rang 1 (jackpot) : **0** (jamais gagné)

### Tests statistiques
- Chi-2 : Tirages uniformes ✅
- KS test : Distribution normale des sommes ✅
- Autocorrélation : Indépendance temporelle ✅
- Mes jeux vs Réalité : Biais significatif ❌

### Backtesting (10k simulations)
- ROI Julien ≈ ROI Random ≈ -50%
- Distribution rangs légèrement différente
- **Conclusion** : Les méthodes ne surperforment pas le hasard

---

## 📝 Prochaines étapes (optionnel)

### 1. Notebook Jupyter interactif

Créer `notebooks/exploratory_analysis.ipynb` pour exploration interactive.

### 2. Rapport final

Rédiger `outputs/final_report.md` avec :
- Executive summary
- Méthodologie
- Résultats
- Leçons apprises
- Recommandations

### 3. Publication

- Upload sur **Kaggle** (dataset + notebook)
- Partage sur **LinkedIn** avec narrative
- GitHub README professionnel

---

## ❓ Troubleshooting

### Erreur : "FileNotFoundError: DataAnalyseModelPredictif-15_08_23.xlsx"

**Solution** : Placer le fichier Excel dans `data/raw/`

### Erreur : "ModuleNotFoundError: No module named 'X'"

**Solution** : Installer dépendances
```bash
pip install -r requirements.txt
```

### Backtesting trop lent

**Solution** : Réduire N_SIMULATIONS dans `05_backtesting.py` (ligne 33)
```python
N_SIMULATIONS = 1000  # Au lieu de 10000
```

### Graphiques ne s'affichent pas

Les graphiques sont sauvegardés dans `outputs/figures/`, pas affichés interactivement.

---

## 📧 Support

Projet créé par **Julien Sisavath** ([@JulienSisi](https://github.com/JulienSisi))

---

**Dernière mise à jour** : Janvier 2025
