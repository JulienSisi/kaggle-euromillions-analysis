# Méthodologie d'Analyse EuroMillions

## Introduction

Ce document détaille les **8 méthodes d'analyse** utilisées pour générer des combinaisons EuroMillions entre 2020 et 2023. Chaque méthode représente une tentative de détecter des patterns dans un processus aléatoire.

**Avertissement** : Aucune de ces méthodes ne peut prédire les tirages futurs. Les tirages de loterie sont indépendants et uniformément distribués.

---

## Méthode 1 : Récurrence + Amplitude

### Principe
Combine deux composantes :
1. **Récurrence** : Fréquence d'apparition d'un numéro sur une fenêtre glissante
2. **Amplitude** : Distance du numéro par rapport à la médiane de la fenêtre

### Formule mathématique

```
Score(n) = α × Fréquence(n, W) + β × (1 - |n - Médiane(W)| / Range(W))
```

Où :
- `n` = numéro candidat [1-50]
- `W` = fenêtre glissante (7, 14 ou 21 derniers tirages)
- `α` = poids récurrence (0.5)
- `β` = poids amplitude (0.5)
- `Fréquence(n, W)` = nombre d'apparitions de `n` dans `W` divisé par taille de `W`
- `Médiane(W)` = médiane de tous les numéros dans `W`
- `Range(W)` = max(W) - min(W)

### Implémentation Python

```python
def calculate_recurrence_amplitude_score(
    draws: pd.DataFrame,
    window_size: int = 7,
    alpha: float = 0.5,
    beta: float = 0.5
) -> Dict[int, float]:
    """
    Calcule le score récurrence + amplitude pour chaque numéro.

    Args:
        draws: DataFrame avec colonnes ['B1', 'B2', 'B3', 'B4', 'B5']
        window_size: Taille fenêtre glissante
        alpha: Poids récurrence
        beta: Poids amplitude

    Returns:
        Dict {numéro: score}
    """
    # Extraire les numéros de la fenêtre
    window = draws.tail(window_size)
    numbers = window[['B1', 'B2', 'B3', 'B4', 'B5']].values.flatten()

    # Calculer fréquence
    frequency = {i: np.sum(numbers == i) / len(numbers) for i in range(1, 51)}

    # Calculer amplitude
    median = np.median(numbers)
    range_val = np.ptp(numbers)  # Peak-to-peak (max - min)

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
```

### Résultat attendu
Les numéros avec score élevé sont sélectionnés. Biais vers numéros centraux et fréquents.

---

## Méthode 2 : Validation par Somme

### Principe
Les tirages EuroMillions ont une somme moyenne autour de 120 (distribution normale). Cette méthode valide qu'une combinaison respecte les contraintes statistiques.

### Contraintes

```python
SUM_MIN = 90   # Somme minimale acceptable
SUM_MAX = 150  # Somme maximale acceptable
SUM_TARGET = 120  # Somme idéale
```

### Distribution théorique

La somme de 5 nombres tirés uniformément dans [1-50] suit une distribution normale :

```
μ = 5 × 25.5 = 127.5
σ ≈ 20
```

Les bornes [90, 150] couvrent environ 95% des tirages réels.

### Implémentation

```python
def validate_sum(combination: List[int]) -> bool:
    """
    Vérifie si la somme respecte les contraintes.

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si valide, False sinon
    """
    total = sum(combination)
    return 90 <= total <= 150
```

### Application
Méthode de filtrage : élimine les combinaisons extrêmes (ex: [1,2,3,4,5] somme=15).

---

## Méthode 3 : Unicité des Combinaisons

### Principe
Éviter de jouer une combinaison déjà sortie dans l'historique.

### Probabilité théorique

Probabilité qu'une combinaison spécifique ressorte :

```
P(répétition) = 1 / C(50, 5) × C(12, 2) ≈ 1 / 139 millions
```

Sur 1000 tirages, probabilité observée de répétition : **≈ 0.0007%**

### Implémentation

```python
def is_unique(
    combination: List[int],
    historical_draws: pd.DataFrame
) -> bool:
    """
    Vérifie si la combinaison n'est jamais sortie.

    Args:
        combination: Liste de 5 numéros triés
        historical_draws: DataFrame des tirages passés

    Returns:
        True si unique, False si déjà sortie
    """
    for _, row in historical_draws.iterrows():
        draw = sorted([row['B1'], row['B2'], row['B3'], row['B4'], row['B5']])
        if draw == sorted(combination):
            return False
    return True
```

### Pertinence
**Faible** : La probabilité de répétition est déjà négligeable. Cette méthode n'apporte aucun avantage statistique.

---

## Méthode 4 : Analyse des Écarts

### Principe
Modéliser le "délai" entre deux apparitions successives d'un numéro. Si un numéro a un écart actuel supérieur à son écart moyen, il est considéré "en retard".

### Formule

```
Gap(n) = Tirage_actuel - Dernier_tirage(n)
Gap_moyen(n) = Moyenne(tous les gaps de n dans l'historique)

Probabilité_ajustée(n) ∝ Gap(n) / Gap_moyen(n)
```

### Implémentation

```python
def calculate_gap_scores(
    draws: pd.DataFrame,
    current_draw_number: int
) -> Dict[int, float]:
    """
    Calcule le score d'écart pour chaque numéro.

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

        # Calculer gaps
        gaps = np.diff(appearances)
        avg_gap = np.mean(gaps) if len(gaps) > 0 else 1

        # Gap actuel
        current_gap = current_draw_number - appearances[-1]

        # Score = ratio gap actuel / gap moyen
        scores[num] = current_gap / avg_gap if avg_gap > 0 else 0

    return scores
```

### Biais psychologique
Cette méthode repose sur le **Gambler's Fallacy** : "un numéro en retard a plus de chances de sortir". Mathématiquement incorrect pour des tirages indépendants.

---

## Méthode 5 : Moving Averages (MA)

### Principe
Lissage temporel de la fréquence d'apparition via moyennes mobiles.

### Types de MA

```python
MA_7  = Moyenne mobile sur 7 tirages   (court terme)
MA_21 = Moyenne mobile sur 21 tirages  (moyen terme)
MA_50 = Moyenne mobile sur 50 tirages  (long terme)
```

### Formule

```
MA_k(n, t) = (1 / k) × Σ[i=0 to k-1] Présence(n, t-i)
```

Où `Présence(n, t) = 1` si `n` apparaît au tirage `t`, sinon `0`.

### Implémentation

```python
def calculate_moving_averages(
    draws: pd.DataFrame,
    window: int = 7
) -> Dict[int, float]:
    """
    Calcule la moyenne mobile de fréquence pour chaque numéro.

    Args:
        draws: DataFrame des tirages
        window: Taille de la fenêtre

    Returns:
        Dict {numéro: MA}
    """
    scores = {}
    recent_draws = draws.tail(window)

    for num in range(1, 51):
        mask = (recent_draws[['B1', 'B2', 'B3', 'B4', 'B5']] == num).any(axis=1)
        frequency = mask.sum() / window
        scores[num] = frequency

    return scores
```

### Stratégie
- **Croisement MA7/MA21** : Si MA7 > MA21 → numéro en tendance haussière
- **Divergence** : Si MA courte diverge de MA longue → signal d'achat (analogie trading)

### Pertinence
**Faible** : Les tirages sont indépendants, donc aucune "tendance" n'existe.

---

## Méthode 6 : Compartimentalisation

### Principe
Segmenter les 50 numéros en zones géographiques et imposer des quotas par zone.

### Zones définies

```python
Zone 1: [1-10]   → Quota: 0-2 numéros
Zone 2: [11-20]  → Quota: 0-2 numéros
Zone 3: [21-30]  → Quota: 1-2 numéros (préférence personnelle)
Zone 4: [31-40]  → Quota: 0-2 numéros
Zone 5: [41-50]  → Quota: 0-2 numéros
```

### Implémentation

```python
def validate_compartments(combination: List[int]) -> bool:
    """
    Vérifie si la combinaison respecte les quotas par zone.

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si valide
    """
    zones = {
        1: (1, 10),
        2: (11, 20),
        3: (21, 30),
        4: (31, 40),
        5: (41, 50)
    }

    counts = {z: 0 for z in zones}

    for num in combination:
        for zone_id, (low, high) in zones.items():
            if low <= num <= high:
                counts[zone_id] += 1

    # Vérifier quotas
    if counts[3] < 1 or counts[3] > 2:  # Zone 3 obligatoire
        return False

    for zone_id in [1, 2, 4, 5]:
        if counts[zone_id] > 2:
            return False

    return True
```

### Justification
Aucune. Pure superstition géographique.

---

## Méthode 7 : Parité & Divisibilité

### Principe
Équilibrer les numéros pairs/impairs et assurer présence de multiples de 3, 5, 7.

### Contraintes

```python
# Parité
PARITY_MIN_EVEN = 1  # Minimum 1 pair
PARITY_MAX_EVEN = 4  # Maximum 4 pairs

# Divisibilité
DIV_3_MIN = 1  # Minimum 1 multiple de 3
DIV_5_MIN = 1  # Minimum 1 multiple de 5
DIV_7_MIN = 0  # Optionnel pour multiple de 7
```

### Implémentation

```python
def validate_parity_divisibility(combination: List[int]) -> bool:
    """
    Vérifie parité et divisibilité.

    Args:
        combination: Liste de 5 numéros

    Returns:
        True si valide
    """
    even_count = sum(1 for n in combination if n % 2 == 0)
    div_3 = sum(1 for n in combination if n % 3 == 0)
    div_5 = sum(1 for n in combination if n % 5 == 0)

    # Vérifier contraintes
    if not (1 <= even_count <= 4):
        return False
    if div_3 < 1:
        return False
    if div_5 < 1:
        return False

    return True
```

### Observation empirique
Sur 1000 tirages réels, distribution pairs/impairs :
- 2 pairs / 3 impairs : ~31%
- 3 pairs / 2 impairs : ~31%
- Distribution uniforme : ~20% chacun

---

## Méthode 8 : Numéro Sacré (13)

### Principe
Inclusion systématique du numéro **13** dans toutes les combinaisons.

### Justification
**Ésotérique** : Aucune base statistique. Biais personnel assumé.

### Probabilité théorique

```
P(13 dans un tirage) = 1 - P(13 absent)
                      = 1 - C(49, 5) / C(50, 5)
                      = 1 - 0.90
                      = 10%
```

Le 13 apparaît dans ~10% des tirages (comme tout autre numéro).

### Implémentation

```python
def force_include_13(combination: List[int]) -> List[int]:
    """
    Force l'inclusion du 13.

    Args:
        combination: Liste de 5 numéros

    Returns:
        Combinaison modifiée avec 13
    """
    if 13 not in combination:
        # Remplacer le numéro avec le score le plus faible
        combination[-1] = 13
    return sorted(combination)
```

### Résultat observé
Sur 133 jeux joués, le 13 apparaissait dans **133 jeux** (100%). Biais de confirmation total.

---

## Synthèse : Pipeline de Génération

### Étapes d'exécution

```python
def generate_combination(draws: pd.DataFrame) -> List[int]:
    """
    Génère une combinaison selon les 8 méthodes.

    Returns:
        Liste de 5 numéros triés
    """
    # 1. Calculer scores
    recurrence_scores = calculate_recurrence_amplitude_score(draws)
    gap_scores = calculate_gap_scores(draws, len(draws))
    ma_scores = calculate_moving_averages(draws, window=7)

    # 2. Combiner scores (moyenne pondérée)
    combined = {}
    for num in range(1, 51):
        combined[num] = (
            0.4 * recurrence_scores[num] +
            0.3 * gap_scores[num] +
            0.3 * ma_scores[num]
        )

    # 3. Sélectionner top 5
    top_numbers = sorted(combined, key=combined.get, reverse=True)[:5]

    # 4. Appliquer contraintes
    while True:
        candidate = top_numbers[:5]

        # Méthode 2: Somme
        if not validate_sum(candidate):
            continue

        # Méthode 3: Unicité
        if not is_unique(candidate, draws):
            continue

        # Méthode 6: Compartiments
        if not validate_compartments(candidate):
            continue

        # Méthode 7: Parité
        if not validate_parity_divisibility(candidate):
            continue

        # Méthode 8: Forcer 13
        candidate = force_include_13(candidate)

        break

    return sorted(candidate)
```

---

## Limitations & Biais Identifiés

### 1. Illusion de contrôle
Un système complexe ≠ prédictibilité. Les 8 méthodes créent une illusion de maîtrise.

### 2. Confirmation bias
Mémorisation sélective des "presque gagnants" (ex: 4/5 numéros corrects).

### 3. Sunk cost fallacy
500h investies → difficulté psychologique d'arrêter.

### 4. Gambler's fallacy
Croire qu'un numéro "en retard" a plus de chances de sortir.

### 5. Ancrage sur le 13
Biais émotionnel/superstitieux réduisant l'espace de recherche.

---

## Conclusion

Ces méthodes représentent une exploration intellectuelle fascinante, mais **ne surperforment pas le hasard**. Le véritable gain : compétences en analyse de données, pensée critique, et humilité statistique.

**Morale** : Les patterns perçus dans l'aléatoire sont souvent du bruit. La rigueur scientifique exige de l'accepter.

---

**Dernière mise à jour** : Janvier 2025
