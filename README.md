# EuroMillions Analysis: The Analytical Gambler's Paradox

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/JulienSisi/kaggle-euromillions-analysis?style=social)](https://github.com/JulienSisi/kaggle-euromillions-analysis)

> **TL;DR**: I analyzed 134 EuroMillions games (2020-2023) using 8 analytical methods. Result: -89.63% ROI with methods vs -89.86% random (p=0.973). Math can't beat math, but the journey demonstrates strong data analysis skills.

[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-blue?logo=kaggle)](https://www.kaggle.com/code/juliensisavath/euromillions-analysis) (coming soon)

---

## Overview

**Demonstration project**: How a sophisticated analytical system applied to a random game can produce interesting results... while confirming the impossibility of prediction.

### The Story

Between 2020 and 2023, I developed a multi-dimensional analysis system for EuroMillions:
- **500+ hours** of analytical engineering
- **223 Excel tabs** of visualizations
- **8 analytical methods** (statistical analysis)
- **134 real games** tested with real money

**Result**: -285.50 CHF net loss, but invaluable data science skills.

---

## The Paradox

### Key Metrics
| Metric | Value | Theoretical Comparison |
|--------|-------|------------------------|
| **Total Invested** | 469.00 CHF | - |
| **Total Won** | ~180 CHF (estimated) | - |
| **ROI** | -61.3% | -50% expected |
| **Win Rate** | ~12% | 3-5% expected |
| **Rank 13** | 3.3× more frequent | vs random |
| **Rank 11** | 7× more frequent | vs random |
| **Jackpot (Rank 1)** | 0 | 0.000095% probability |

**The paradox**: Winning more often, but losing more money.

---

## The 8 Analytical Methods

### 1. Recurrence + Amplitude
Frequency analysis over sliding windows (7, 14, 21 draws).

**Formula**:
```
Score(n) = Frequency(n, window) × (1 - |n - Median(window)| / Range(window))
```

### 2. Sum Validation
Statistical constraint verification (total sum, parity).

```
Constraint: 90 ≤ Σ(balls) ≤ 150
Target: sum ≈ 120
```

### 3. Combination Uniqueness
Anti-collision with 1,658 historical draws.

### 4. Gap Analysis
Modeling delays between successive appearances.

```
Gap(n) = Current_draw - Last_draw(n)
Probability(n) ∝ Gap(n) if Gap(n) > Average_gap(n)
```

### 5. Moving Averages
Temporal smoothing to detect trends (MA7, MA21).

### 6. Compartmentalization
Segmentation [1-10], [11-20], [21-30], [31-40], [41-50] with quotas.

### 7. Parity & Divisibility
Balancing even/odd, multiples of 3, 5, 7.

### 8. Sacred Number
Systematic inclusion of "13" (acknowledged personal bias).

**Full methodology**: See [docs/methodology.md](docs/methodology.md)

---

## Installation

```bash
# Clone the repo
git clone https://github.com/JulienSisi/kaggle-euromillions-analysis.git
cd kaggle-euromillions-analysis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Data Preparation
```bash
# Place DataAnalyseModelPredictif-15_08_23.xlsx in data/raw/
python src/01_extract_data_custom.py
python src/02_clean_data.py
```

### 2. Analyze 134 Real Games
```bash
python src/03_analyze_games.py
```

### 3. Statistical Tests
```bash
python src/04_statistical_tests.py
```

### 4. Backtesting
```bash
# Generates 1,000 "Julien style" games vs 1,000 random games
python src/05_backtesting.py
```

### 5. Visualizations
```bash
python src/06_visualizations.py
# Outputs: outputs/figures/*.png
```

### 6. Interactive Notebook
```bash
jupyter notebook exploration.ipynb
```

---

## Project Structure

```
kaggle-euromillions-analysis/
├── README.md                      # This file
├── KAGGLE_README.md               # Kaggle-specific README
├── requirements.txt               # Python dependencies
├── config.md                      # Configuration
├── exploration.ipynb              # Interactive Jupyter notebook
│
├── data/
│   ├── raw/                       # DataAnalyseModelPredictif-15_08_23.xlsx
│   └── processed/                 # Cleaned CSVs (generated)
│
├── src/
│   ├── 01_extract_data_custom.py # Excel → CSV
│   ├── 02_clean_data.py          # Data cleaning
│   ├── 03_analyze_games.py       # Analyze 134 games
│   ├── 04_statistical_tests.py   # Chi-2, KS test, etc.
│   ├── 05_backtesting.py         # Simulate 1,000 games
│   ├── 06_visualizations.py      # Generate charts
│   └── utils.py                  # Utility functions
│
├── outputs/
│   ├── figures/                  # Generated PNGs (5 files)
│   ├── reports/                  # CSV/JSON results (6 files)
│   └── final_report.md           # Complete technical report (17 pages)
│
└── docs/
    ├── analysis_plan.md          # 6-phase analysis plan
    └── methodology.md            # Detailed methods documentation
```

---

## Key Results

### Backtesting: "Julien Style" vs Random

**Tested Hypothesis**:
> Do analytical methods maximize small wins at the expense of big wins?

| Metric | Julien (8 Methods) | Random | Difference |
|--------|-------------------|--------|------------|
| **ROI** | **-89.63%** | **-89.86%** | **+0.23%** ✅ |
| Win Rate | 1.9% | 1.8% | +0.1% |
| Games Simulated | 1,000 | 1,000 | - |
| Statistical Significance | **p = 0.973** | | **NOT significant** |

**Conclusion**: The 8 analytical methods **DO NOT outperform** random selection.

### Statistical Tests
- **Chi-2 (uniformity)**: p-value = 0.86 ✅ Uniform distribution
- **Kolmogorov-Smirnov (normality)**: p-value = 0.80 ✅ Normal distribution
- **Autocorrelation**: No significant lags ✅ Independent draws

---

## Lessons Learned

### 1. Lottery Draws are Truly Random
No method outperforms random selection in the long run.

### 2. Cognitive Biases Identified
- **Sunk cost fallacy**: 500h invested → difficulty stopping
- **Confirmation bias**: Remembering "near-misses"
- **Illusion of control**: Complex system ≠ predictability
- **Sacred number bias**: Number 13 over-represented 1.8x

### 3. Transferable Value
The skills developed are applicable to:
- **RegTech**: Transaction anomaly detection
- **FinTech**: Risk analysis, strategy backtesting
- **Pharma/Rail**: Critical systems monitoring

---

## Skills Demonstrated

| Domain | Skill | RegTech Application |
|--------|-------|---------------------|
| **Data Engineering** | ETL Excel → Python | Compliance pipelines |
| **Statistics** | Hypothesis testing, distributions | Fraud detection |
| **Visualization** | Heatmaps, time series | Regulatory dashboards |
| **Backtesting** | Monte Carlo simulation | Stress testing |
| **Critical Thinking** | Bias recognition | Quality auditing |

**Background**:
- 5+ years Industrial Engineering (Alstom/Bombardier - rail diagnostics, EN50128)
- CMMS Pharmaceutical (Oracle, GxP compliance)
- Current: ISC Student @ HEIA-FR, transitioning to RegTech

---

## Visualizations

Generated in `outputs/figures/`:

1. **heatmap_frequency.png** - Number frequency heatmap (5×10 matrix)
2. **sum_distribution.png** - Ball sum distribution (real vs my games)
3. **number_frequency_comparison.png** - Frequency comparison
4. **autocorrelation_13.png** - Independence test
5. **backtesting_comparison.png** - Julien vs Random performance

---

## Documentation

- **[Complete Report](outputs/final_report.md)** (17 pages): Full analysis, methodology, conclusions
- **[Methodology](docs/methodology.md)**: Detailed explanation of 8 methods with formulas
- **[Analysis Plan](docs/analysis_plan.md)**: 6-phase roadmap
- **[Interactive Notebook](exploration.ipynb)**: Jupyter notebook for exploration

---

## Warning

> **Lottery draws are independent and random.**
>
> This project is an analytical exploration, **not a winning strategy**.
>
> Never gamble more than you can afford to lose.

---

## About

**Julien Sisavath**
ISC Student @ HEIA-FR | Ex-Railway Engineer (Alstom) | Transitioning to RegTech

- GitHub: [@JulienSisi](https://github.com/JulienSisi)
- LinkedIn: [julien-sisavath](https://www.linkedin.com/in/julien-sisavath/)
- Portfolio: [Kaggle](https://www.kaggle.com/code/juliensisavath/euromillions-analysis)

---

## License

MIT License

Copyright (c) 2026 Julien Sisavath

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

If this project inspires you:

```bibtex
@misc{sisavath2026euromillions,
  author = {Sisavath, Julien},
  title = {EuroMillions Analysis: The Analytical Gambler's Paradox},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/JulienSisi/kaggle-euromillions-analysis}
}
```

---

**Last Updated**: January 2026
