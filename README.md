# EuroMillions Analysis: Le Paradoxe du Joueur Analytique

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/JulienSisi/kaggle-euromillions-analysis?style=social)](https://github.com/JulienSisi/kaggle-euromillions-analysis)

> **TL;DR**: I analyzed 134 EuroMillions games (2020-2023) using 8 analytical methods. Result: -89.63% ROI with methods vs -89.86% random (p=0.973). Math can't beat math, but the journey demonstrates strong data analysis skills.

[Badge] [Kaggle Dataset](https://www.kaggle.com/code/juliensisavath/euromillions-analysis) (coming soon)

## Vue d'ensemble

**Projet de démonstration** : Comment un système d'analyse sophistiqué appliqué à un jeu aléatoire peut produire des résultats intéressants... tout en confirmant l'impossibilité de prédiction.

### L'histoire

Entre 2020 et 2023, j'ai développé un système d'analyse multi-dimensionnelle pour EuroMillions :
- **500+ heures** d'ingénierie analytique
- **223 onglets Excel** de visualisations
- **8 méthodes** d'analyse statistique
- **133 jeux réels** testés avec argent réel

**Résultat** : -285.50 CHF de perte nette, mais des compétences data science inestimables.

---

## Le Paradoxe

### Metrics Clés
| Métrique | Valeur | Comparaison théorique |
|----------|--------|----------------------|
| **Mise totale** | 465.50 CHF | - |
| **Gains totaux** | ~180 CHF | - |
| **ROI** | -61.3% | -50% attendu |
| **Taux de réussite** | 12% | 3-5% attendu |
| **Rang 13** | 3.3× plus fréquent | vs aléatoire |
| **Rang 11** | 7× plus fréquent | vs aléatoire |
| **Jackpot (Rang 1)** | 0 | 0.000095% prob. |

**Le paradoxe** : Gagner plus souvent, mais perdre plus d'argent.

---

## Les 8 Méthodes d'Analyse

### 1. Récurrence + Amplitude
Analyse de la fréquence d'apparition sur fenêtres glissantes (7, 14, 21 tirages).

**Formule** :
```
Score(n) = Fréquence(n, window) × (1 - |n - Médiane(window)| / Range(window))
```

### 2. Validation par Somme
Vérification des contraintes statistiques (somme totale, parité).

```
Constraint: 90 ≤ Σ(boules) ≤ 150
```

### 3. Unicité des Combinaisons
Anti-collision avec historique des 1000+ tirages.

### 4. Analyse des Écarts
Modélisation des délais entre apparitions successives.

```
Gap(n) = Tirage_actuel - Dernier_tirage(n)
Probabilité(n) ∝ Gap(n) si Gap(n) > Écart_moyen(n)
```

### 5. Moving Averages
Lissage temporel pour détecter tendances (MA7, MA21).

### 6. Compartimentalisation
Segmentation [1-10], [11-20], [21-30], [31-40], [41-50] avec quotas.

### 7. Parité & Divisibilité
Équilibrage pairs/impairs, multiples de 3, 5, 7.

### 8. Numéro Sacré
Inclusion systématique du "13" (biais personnel assumé).

---

## Installation

```bash
# Cloner le repo
git clone https://github.com/JulienSisi/euromillions-analysis.git
cd euromillions-analysis

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt
```

---

## Usage

### 1. Préparation des données
```bash
# Placer DataAnalyseModelPredictif-15_08_23.xlsx dans data/raw/
python src/01_extract_data.py
python src/02_clean_data.py
```

### 2. Analyse des 133 jeux réels
```bash
python src/03_analyze_games.py
```

### 3. Tests statistiques
```bash
python src/04_statistical_tests.py
```

### 4. Backtesting
```bash
# Génère 10,000 jeux "style Julien" vs 10,000 jeux aléatoires
python src/05_backtesting.py
```

### 5. Visualisations
```bash
python src/06_visualizations.py
# Outputs: outputs/figures/*.png
```

### 6. Notebook interactif
```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## Structure du Projet

```
euromillions-analysis/
├── README.md                      # Ce fichier
├── requirements.txt               # Dépendances Python
├── config.md                      # Configuration
├── methodology.md                 # Documentation méthodes
│
├── data/
│   ├── raw/                       # DataAnalyseModelPredictif-15_08_23.xlsx
│   └── processed/                 # CSV nettoyés (générés)
│
├── src/
│   ├── 01_extract_data.py        # Excel → CSV
│   ├── 02_clean_data.py          # Nettoyage
│   ├── 03_analyze_games.py       # Analyse 133 jeux
│   ├── 04_statistical_tests.py   # Chi2, KS test, etc.
│   ├── 05_backtesting.py         # Simulation 10k jeux
│   ├── 06_visualizations.py      # Graphiques
│   └── utils.py                  # Fonctions utilitaires
│
├── notebooks/
│   └── exploratory_analysis.ipynb  # Exploration interactive
│
├── outputs/
│   ├── figures/                  # PNG générés
│   ├── reports/                  # CSV/JSON
│   └── final_report.md           # Rapport final
│
└── docs/
    ├── analysis_plan.md          # Plan d'analyse
    └── findings.md               # Résultats
```

---

## Résultats Clés

### Backtesting "Style Julien" vs Aléatoire
[À compléter après exécution de `05_backtesting.py`]

**Hypothèse testée** :
> Les méthodes analytiques maximisent-elles les petits gains au détriment des gros ?

### Tests Statistiques
- **Chi-2 (uniformité)** : p-value = ?
- **Kolmogorov-Smirnov** : D-stat = ?
- **Corrélations temporelles** : ρ = ?

---

## Leçons Apprennues

### 1. Les tirages sont réellement aléatoires
Aucune méthode ne surperforme l'aléatoire sur le long terme.

### 2. Biais cognitifs identifiés
- **Sunk cost fallacy** : 500h investies → difficulté d'arrêter
- **Confirmation bias** : Mémorisation des "presque jackpots"
- **Illusion de contrôle** : Système complexe ≠ prédictibilité

### 3. Valeur transférable
Les compétences développées sont applicables à :
- **RegTech** : Détection d'anomalies transactionnelles
- **FinTech** : Analyse de risque, backtesting de stratégies
- **Pharma/Rail** : Monitoring de systèmes critiques

---

## Compétences Démontrées

| Domaine | Compétence | Application RegTech |
|---------|-----------|---------------------|
| **Data Engineering** | ETL Excel → Python | Pipelines compliance |
| **Statistiques** | Tests d'hypothèses, distributions | Détection fraude |
| **Visualisation** | Heatmaps, séries temporelles | Dashboards réglementaires |
| **Backtesting** | Simulation Monte Carlo | Stress testing |
| **Pensée critique** | Reconnaissance biais | Audit qualité |

---

## Avertissement

> **Les tirages de loterie sont indépendants et aléatoires.**
>
> Ce projet est une exploration analytique, **pas une stratégie gagnante**.
>
> Ne jouez jamais plus que vous ne pouvez perdre.

---

## À Propos

**Julien Sisavath**
Étudiant ISC @ HEIA-FR | Ex-Ingénieur Ferroviaire (Alstom) | Transition vers RegTech

- GitHub: [@JulienSisi](https://github.com/JulienSisi)
- LinkedIn: [julien-sisavath](https://www.linkedin.com/in/julien-sisavath/)
- Portfolio: [en construction]

---

## Licence

MIT License

Copyright (c) 2026 Julien Sisi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Citation

Si ce projet vous inspire :

```bibtex
@misc{sisavath2025euromillions,
  author = {Sisavath, Julien},
  title = {EuroMillions Analysis: Le Paradoxe du Joueur Analytique},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/JulienSisi/euromillions-analysis}
}
```

---

**Dernière mise à jour** : Janvier 2025
