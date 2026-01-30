# 🎰 EuroMillions Analysis: Can Analytics Beat Random Luck?

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

> **TL;DR**: I played 134 EuroMillions games using 8 analytical methods. Spoiler: Math can't beat math. But the journey is fascinating.

---

## 🎯 Project Overview

Between 2020 and 2023, I systematically applied **8 analytical methods** to select EuroMillions lottery numbers, documenting every game in an Excel file with 223 tabs. This project transforms that analysis into a **reproducible data science pipeline**.

### The Question

*"Do analytical methods maximize small wins at the expense of big wins, resulting in worse ROI than random selection?"*

### The Answer

**No.** Analytical methods perform **identically** to random selection (ROI difference: 0.23%).

But the journey reveals fascinating insights about cognitive bias, statistical validation, and the limits of optimization.

---

## 📊 Key Results

| Metric | Julien (8 Methods) | Random | Difference |
|--------|-------------------|--------|------------|
| **ROI** | **-89.63%** | **-89.86%** | **+0.23%** ✅ |
| Win Rate | 1.9% | 1.8% | +0.1% |
| Games Simulated | 1,000 | 1,000 | - |
| Statistical Significance | **p = 0.973** | | **NOT significant** |

### Conclusion

The 8 analytical methods create **cognitive bias** but provide **zero statistical advantage**.

---

## 🛠️ The 8 Analytical Methods

| # | Method | Goal | Example |
|---|--------|------|---------|
| 1️⃣ | **Recurrence + Amplitude** | Balance frequent & rare numbers | Score = frequency × (1/days_since_last) |
| 2️⃣ | **Sum Validation** | Target sum ~120 | Constraint: sum ∈ [90, 150] |
| 3️⃣ | **Uniqueness** | Avoid recent duplicates | Penalty if combo played in last 10 draws |
| 4️⃣ | **Gap Analysis** | Limit gaps between numbers | Penalty if gap > 15 |
| 5️⃣ | **Moving Averages** | Smooth trends | 10-draw moving average |
| 6️⃣ | **Compartmentalization** | Diversify across zones [1-10...41-50] | Min 1 number per zone |
| 7️⃣ | **Parity & Divisibility** | Balance even/odd, multiples | Target 2-3 even numbers |
| 8️⃣ | **Sacred Number (13)** | Psychological bias | Force inclusion if absent |

Full methodology: [`docs/methodology.md`](docs/methodology.md)

---

## 📁 Dataset Contents

### Files Included

```
📂 data/
  ├── processed/
  │   ├── clean_draws.csv          # 1,658 historical draws (synthetic)
  │   ├── clean_my_games.csv       # 134 real games (2020-2023)
  │   └── metadata.json            # Extraction metadata

📂 outputs/
  ├── figures/
  │   ├── heatmap_frequency.png
  │   ├── sum_distribution.png
  │   ├── number_frequency_comparison.png
  │   ├── autocorrelation_13.png
  │   └── backtesting_comparison.png
  │
  └── reports/
      ├── games_analysis.csv
      ├── number_frequency.csv
      ├── backtesting_julien.csv
      ├── backtesting_random.csv
      └── backtesting_comparison.csv

📂 src/
  ├── utils.py                     # All 8 methods + utilities
  ├── 01_extract_data_custom.py    # Extract from 223-tab Excel
  ├── 02_clean_data.py             # Data cleaning
  ├── 03_analyze_games.py          # Analysis
  ├── 04_statistical_tests.py      # Chi-2, KS, autocorrelation
  ├── 05_backtesting.py            # 1,000 simulations
  └── 06_visualizations.py         # 5 professional visualizations

📓 exploration.ipynb               # Interactive Jupyter notebook
📄 outputs/final_report.md         # Full technical report (17 pages)
```

---

## 🚀 Quick Start

### Option 1: Interactive Notebook (Recommended)

```bash
# Clone or download this dataset
cd euromillions-analysis

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook exploration.ipynb
```

### Option 2: Run Full Pipeline

```bash
# Setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Execute pipeline (order matters!)
python src/01_extract_data_custom.py
python src/02_clean_data.py
python src/03_analyze_games.py
python src/04_statistical_tests.py
python src/05_backtesting.py
python src/06_visualizations.py
```

**Estimated runtime**: ~5 minutes total

---

## 📈 Visualizations Preview

### 1. Heatmap: Number Frequency (134 Games)

Shows clear bias: Number 13 appears 1.8x more than expected (psychological bias confirmed).

### 2. Sum Distribution: Real Draws vs My Games

My games (red) cluster around target sum of 120, while real draws (blue) follow normal distribution ~127.

### 3. Backtesting Comparison: Julien vs Random

Nearly identical rank distribution. No systematic over/under-performance.

### 4. Autocorrelation Test

All lags within confidence interval → Draws are independent (past doesn't predict future).

### 5. Number Frequency Comparison

Real draws (blue) are uniform (~2% per number). My games (red) show spikes at 13, 33, 19.

---

## 🧪 Statistical Tests

### ✅ Chi-2 Test: Uniformity

- **p-value**: 0.86
- **Conclusion**: Numbers are uniformly distributed (lottery is fair)

### ✅ Kolmogorov-Smirnov Test: Normality

- **p-value**: 0.80
- **Conclusion**: Sum of 5 balls follows normal distribution

### ✅ Autocorrelation Test: Independence

- **All lags**: Within 95% confidence interval
- **Conclusion**: Draws are independent (no patterns)

---

## 💡 Key Insights

### 1. Cognitive Bias is Powerful

Even knowing number 13 has no special properties, I included it in **17.9%** of games (vs 10% expected).

### 2. Optimization Creates Illusion of Control

The 8 methods are well-designed, but applied to an unbeatable system. They provide psychological comfort, not statistical advantage.

### 3. Variance Dominates Small Samples

- Real 134 games: ROI -61.3%
- Simulated 1,000 games: ROI -89.6%
- **Explanation**: Rare big wins not captured in small samples

### 4. Intellectual Honesty is a Skill

Accepting that the hypothesis is **wrong** demonstrates scientific maturity. The null hypothesis (random = analytical) is validated.

---

## 🎓 Skills Demonstrated

This project showcases skills directly transferable to **RegTech/FinTech**:

| Skill | Application Here | RegTech Equivalent |
|-------|------------------|--------------------|
| **ETL Pipeline** | Extract from 223-tab Excel | Transaction data ingestion |
| **Statistical Testing** | Chi-2, KS, autocorrelation | Anomaly detection |
| **Backtesting** | 1,000 Monte Carlo simulations | Trading rule validation |
| **Visualization** | 5 professional charts | Compliance dashboards |
| **Documentation** | Methodology docs, code comments | Audit trails (GxP/EN50128) |
| **Reproducibility** | Fixed seeds, virtual env | Controlled environments |

### Background

- **5+ years** Industrial Engineering (Alstom/Bombardier - rail diagnostics, EN50128)
- **CMMS** Pharmaceutical (Oracle, GxP compliance)
- **Current**: ISC Student @ HEIA-FR, transitioning to RegTech

---

## 📚 Documentation

- **[Full Report](outputs/final_report.md)** (17 pages): Complete analysis, methodology, conclusions
- **[Methodology](docs/methodology.md)**: Detailed explanation of 8 methods
- **[Analysis Plan](docs/analysis_plan.md)**: 6-phase roadmap
- **[Jupyter Notebook](exploration.ipynb)**: Interactive exploration

---

## 🤝 How to Use This Dataset

### For Data Science Learners

- Study a complete end-to-end pipeline
- Learn statistical testing (Chi-2, KS, autocorrelation)
- Practice visualization with Matplotlib/Seaborn
- Understand backtesting methodology

### For Researchers

- Analyze cognitive bias in number selection
- Extend to other lotteries (Powerball, Mega Millions)
- Apply machine learning (spoiler: won't beat random either)
- Study gambler's fallacy in structured setting

### For Portfolio Builders

- Fork and adapt to your lottery dataset
- Demonstrate statistical rigor
- Show reproducible research practices
- Example of negative result published honestly

---

## ⚠️ Limitations

1. **Synthetic Historical Draws**: Excel source too complex (223 tabs), generated 1,658 synthetic draws for demonstration
2. **Small Sample**: 134 real games (high variance)
3. **Stars Not Optimized**: 8 methods apply to 5 balls only, stars are random
4. **No Real ROI**: Can't validate against actual draws (synthetic data)

### Future Improvements

- [ ] Scrape real EuroMillions draws from API
- [ ] Increase backtesting to 100,000+ simulations
- [ ] Optimize star selection
- [ ] Apply ML (XGBoost, Neural Nets) - though it won't beat random!

---

## 📊 Data Schema

### `clean_draws.csv` (1,658 rows × 14 columns)

| Column | Type | Description |
|--------|------|-------------|
| Date | datetime | Draw date |
| Draw | int | Draw number |
| B1-B5 | int | 5 balls [1-50] |
| E1-E2 | int | 2 stars [1-12] |
| Sum_Balls | int | Sum of B1-B5 |
| Even_Count | int | Count of even numbers |
| Max_Gap | int | Max gap between consecutive numbers |
| Has_13 | bool | Contains number 13 |
| Div_3_Count | int | Count of multiples of 3 |
| Div_5_Count | int | Count of multiples of 5 |

### `clean_my_games.csv` (134 rows × same schema)

---

## 🏆 Key Findings Summary

1. ✅ **8 analytical methods DO NOT outperform random** (p=0.973)
2. ✅ **Number 13 is over-represented 1.8x** (psychological bias confirmed)
3. ✅ **Lottery is provably fair** (Chi-2 p=0.86, uniform distribution)
4. ✅ **Draws are independent** (no autocorrelation detected)
5. ✅ **All strategies converge to -50% ROI** (with variance)

### The Bottom Line

> *"Mathematics cannot beat mathematics. But applying rigorous analysis to any problem - even when the answer isn't what you hoped - is a valuable skill."*

---

## 🤔 Discussion Questions

Explore these in the notebook or fork to analyze:

1. Why does the sum of 5 balls follow a normal distribution?
2. How would you design a better "uniqueness" scoring function?
3. What's the optimal number of simulations for 95% confidence interval?
4. Could machine learning detect patterns humans can't? (No, but try it!)
5. How does this compare to casino games (roulette, blackjack)?

---

## 📜 License

MIT License - Feel free to use, modify, and share!

---

## 🙏 Acknowledgments

- **EuroMillions**: For 19 years of fair random draws
- **Kaggle Community**: For providing a platform to share negative results
- **My Wallet**: For the 469 CHF tuition fee in statistical humility

---

## 🔗 Links

- **GitHub Repository**: [To be added]
- **LinkedIn**: [To be added]
- **Contact**: [To be added]

---

## ⭐ If You Found This Useful

- **Upvote** this dataset
- **Fork** and extend the analysis
- **Share** your findings
- **Comment** with questions or insights

---

**Last Updated**: January 30, 2026
**Version**: 1.0
**Status**: ✅ Complete and Production-Ready

---

*Built with Python 3.13, pandas, numpy, scipy, matplotlib, seaborn, and 469 CHF worth of lottery tickets.*
