# Seizure Forecasting and Crash Risk Analysis

**Supplementary Materials for JAMA Neurology Paper**

This repository contains the complete analysis code, mathematical methods, and supplementary materials examining the relationship between seizure forecasting algorithm performance and driving safety.

---

## Table of Contents

### 1. [Overview](#1-overview)
### 2. [Repository Contents](#2-repository-contents)
### 3. [Key Results](#3-key-results)
   - 3.1 [Main Findings Table](#31-main-findings-table)
   - 3.2 [ROC Shape Sensitivity Analysis](#32-roc-shape-sensitivity-analysis)
### 4. [Figures](#4-figures)
   - 4.1 [Figure 1: Driving Days vs. AUC (Main)](#41-figure-1-driving-days-per-year-vs-auc-main-text)
   - 4.2 [Figure S1: Crash Risk vs. Days in Warning](#42-figure-s1-crash-risk-vs-days-in-warning-per-year)
   - 4.3 [Figure S2: Binormal Forecast Model](#43-figure-s2-binormal-forecast-model-schematic)
   - 4.4 [Figure S3: Minimum Warning Days vs. AUC](#44-figure-s3-minimum-warning-days-required-for-legal-limit-safety)
   - 4.5 [Figure S4: ROC Shape Sensitivity](#45-figure-s4-sensitivity-to-roc-curve-shape)
   - 4.6 [Figure S5: ROC Curve Comparison](#46-figure-s5-comparison-of-roc-geometries)
### 5. [Mathematical Methods](#5-mathematical-methods)
   - 5.1 [Binormal ROC Model](#51-binormal-roc-model)
   - 5.2 [Sensitivity and False Positive Rate](#52-sensitivity-and-false-positive-rate)
   - 5.3 [Daily Seizure Probability](#53-daily-seizure-probability)
   - 5.4 [Posterior Probability (Bayes' Rule)](#54-posterior-probability-of-seizure-on-safe-days)
   - 5.5 [Crash Risk Calculation](#55-crash-risk-on-safe-days)
   - 5.6 [Time in Warning](#56-time-in-warning)
   - 5.7 [Legal-Limit Safety Threshold](#57-minimum-warning-days-for-legal-limit-safety)
   - 5.8 [AUC Performance Curves](#58-minimum-warning-days-vs-auc-figure-s1)
   - 5.9 [Reproducibility](#59-reproducibility)
   - 5.10 [ROC Shape Analysis](#510-why-roc-shape-matters-and-why-it-doesnt)
   - 5.11 [Alternative ROC Models](#511-alternative-roc-models-tested)
   - 5.12 [Mathematical Formulations](#512-mathematical-formulations-of-alternative-roc-shapes)
   - 5.13 [Impact on Conclusions](#513-impact-on-driving-safety-conclusions)
### 6. [Discussion: Validity of Binormal Assumption](#6-discussion-validity-of-the-binormal-roc-assumption)
### 7. [Running the Code](#7-running-the-code)
### 8. [Citation & Contact](#8-citation-and-contact)

---

## 1. Overview

This analysis quantifies the trade-offs between seizure forecasting accuracy (measured by AUC) and driving restrictions required to maintain crash risk at or below legal intoxication levels (approximately 16× baseline risk).

**Key finding:** Even high-performance forecasting algorithms (AUC = 0.90) require substantial driving restrictions for patients with frequent seizures. Only patients with rare seizures (≤1 per year) can achieve near-daily driving with excellent forecasting performance.

---

## 2. Repository Contents

### Code
- **[`crashes_vs_TiW.ipynb`](crashes_vs_TiW.ipynb)** - Complete Jupyter notebook with all analysis code
  - Cell 0: Figure S1 (crash risk vs. warning days)
  - Cell 1: Empty
  - Cell 2: Figure 1 (driving days vs. AUC) for main text
  - Cell 3: Figure S3 (minimum warning days vs. AUC)
  - Cell 4: Figure S2 (binormal model schematic)
  - Cell 5: ROC shape sensitivity analysis (Figures S4 and S5)
  - Cell 6: Markdown for extended AUC table
  - Cell 7: Extended AUC table code

### Figures (PDF and PNG formats)
- **`Figure_1`** - Driving days/year vs. AUC (main text figure)
- **`Figure_S1`** - Crash risk vs. warning days (supplementary)
- **`Figure_S2`** - Binormal forecast model schematic (supplementary)
- **`Figure_S3`** - Minimum warning days vs. AUC (supplementary)
- **`Figure_S4`** - ROC shape sensitivity analysis (supplementary)
- **`Figure_S5`** - ROC curve geometries comparison (supplementary)

*PNG versions are displayed in this README; PDF versions are provided for publication.*

---

## 3. Key Results

### 3.1 Main Findings Table

**Driving Restrictions Required to Achieve Legal-Limit Crash Risk by Seizure Frequency and Forecasting Performance**

At the legal-limit safety threshold (16× baseline crash risk):

| Seizure Frequency | AUC | Warning Days/Year | Driving Days/Year | Avg Days Between Drives |
|------------------|-----|-------------------|-------------------|------------------------|
| **1/week** | 0.60 | — | — | Cannot reach safety threshold |
| | 0.70 | 365 | 0 | ∞ |
| | 0.80 | 365 | 0 | 59,333 |
| | 0.90 | 358 | 7 | 55 |
| | 0.95 | 314 | 51 | 7.2 |
| | 0.99 | 159 | 206 | 1.8 |
| **1/month** | 0.60 | — | — | Cannot reach safety threshold |
| | 0.70 | 365 | 0 | 17,394,297 |
| | 0.80 | 364 | 1 | 396 |
| | 0.90 | 318 | 47 | 7.8 |
| | 0.95 | 221 | 144 | 2.5 |
| | 0.99 | 69 | 296 | 1.2 |
| **1/year** | 0.60 | 365 | 0 | 680,859 |
| | 0.70 | 349 | 16 | 23.1 |
| | 0.80 | 238 | 127 | 2.9 |
| | 0.90 | 97 | 268 | 1.4 |
| | 0.95 | 38 | 327 | 1.1 |
| | 0.99 | 5 | 360 | 1.0 |

**Key Insights:**
- **AUC < 0.70** is insufficient for practical driving policies at any seizure frequency
- **AUC = 0.90** enables ~7 days/year for weekly seizures, ~47 days/year for monthly seizures, ~268 days/year for yearly seizures
- **Even AUC = 0.99** (near-perfect) limits weekly seizure patients to ~56% of days
- **Seizure frequency is the dominant factor** determining driving feasibility

### 3.2 ROC Shape Sensitivity Analysis

Comparison of driving days allowed per year across different ROC shapes (all AUC ≈ 0.90):

| Seizure Frequency | Equal-variance binormal | S-shaped (unequal variance) | Hooked (mixture) |
|------------------|------------------------|----------------------------|------------------|
| **1/week** | 7 days | Cannot reach safety | 0 days |
| **1/month** | 47 days | Cannot reach safety | 0 days |
| **1/year** | 268 days | **288 days** | 223 days |

**Key Observations:**
1. **High seizure frequencies:** ROC shape doesn't matter—all models struggle
2. **Low seizure frequency:** S-shaped ROC can outperform (288 vs 268 days/year)
3. **Overall:** Limited AUC, not ROC geometry, is the fundamental barrier

---

## 4. Figures

### 4.1 Figure 1: Driving Days per Year vs. AUC (Main Text)

![Figure 1](Figure_1.png)

**Description:** Annual driving days permitted under forecasting-based driving policy to maintain crash risk below legal intoxication threshold (16× baseline).

**Key features:**
- **Three colored curves:** Show relationship between AUC and safe driving days for different seizure frequencies
  - Green: 1 seizure/year
  - Blue: 1 seizure/month
  - Orange: 1 seizure/week
- **Filled circles:** Mark key AUC values (0.60, 0.70, 0.80, 0.90, 0.95, 0.99)
- **Smooth curves:** Calculated analytically using equal-variance binormal ROC model with Bayes' theorem

**Key finding:** Even high-performance algorithms (AUC = 0.90) require substantial driving restrictions for patients with frequent seizures. For weekly seizures, only ~7 days/year are permitted; for yearly seizures, ~268 days/year.

---

### 4.2 Figure S1: Crash Risk vs. Days in Warning per Year

![Figure S1](Figure_S1.png)

**Description:** Crash risk when driving after a negative seizure forecast, as a function of time in warning. Each panel shows crash risk for patients with different baseline seizure frequencies: 1 seizure per week (top), 1 seizure per month (middle), and 1 seizure per year (bottom).

**Key features:**
- **Black curves:** Algorithms with AUROC = 0.60, 0.80, and 0.90 (thicker lines = higher AUC)
- **X-axis:** Days per year the algorithm advises against driving ("time in warning")
- **Y-axis:** Crash risk as a multiple of baseline sober driving risk
- **Horizontal dashed lines:** Crash risks equivalent to driving after 1, 3, 4 (legal limit at 0.08% BAC), and 6 alcoholic drinks
- **Black circles:** Minimum warning time required to achieve the legal-limit threshold (~16× baseline)
- **Light green region:** "Safe" zone (below 1-drink equivalent)
- **Light yellow region:** "Caution" zone (1-4 drinks equivalent)
- **Light pink region:** "Unsafe" zone (above legal limit)

**Calculations:** Crash risk calculated assuming 50% probability of crash given a seizure while driving and baseline crash risk of 1.5 × 10⁻⁵ per trip. Alcohol-related relative risks derived from Zador et al. (2000), with risk approximately doubling per 0.02% increase in BAC.

**Trade-off:** Higher crash risk reduction requires more days in warning (fewer driving days).

---

### 4.3 Figure S2: Binormal Forecast Model Schematic

![Figure S2](Figure_S2.png)

**Description:** Illustrates the statistical model underlying the primary analysis.

**Model components:**
- Forecast scores on non-seizure days: N(0,1)
- Forecast scores on seizure days: N(m,1)
- Threshold *t* defines the operating point
- Bayes' theorem combines sensitivity, specificity, and base rate to compute posterior seizure risk

This schematic shows how the forecasting algorithm separates seizure from non-seizure days and how Bayes' rule computes crash risk on "safe" days.

---

### 4.4 Figure S3: Minimum Warning Days Required for Legal-Limit Safety

![Figure S3](Figure_S3.png)

**Description:** Shows the minimum number of warning days per year needed to achieve legal-limit driving safety as a function of AUC, for three seizure frequencies.

**Key elements:**
- **Solid line:** 1 seizure/week
- **Dashed line:** 1 seizure/month
- **Dotted line:** 1 seizure/year
- **Right y-axis:** Converts warning days to maximum allowed driving days (365 − warning days)

This figure demonstrates that achieving safety with high seizure frequencies requires extremely high AUC values (>0.90).

---

### 4.5 Figure S4: Sensitivity to ROC Curve Shape

![Figure S4](Figure_S4.png)

**Question addressed:** *"Do our conclusions depend on assuming a binormal (symmetric) ROC curve?"*

**Comparison:** Three different ROC curve shapes, all calibrated to AUC ≈ 0.90:

1. **Equal-variance binormal** (black): Standard symmetric ROC curve
2. **Unequal-variance binormal** (blue): S-shaped ROC from different class variances
3. **Mixture model** (red): "Hooked" ROC from heterogeneous positive class

**Key finding:** While ROC shape affects the *specific number* of allowable driving days, it does not change the qualitative conclusion that high seizure frequencies require severe driving restrictions even with excellent forecasting (AUC = 0.90).

---

### 4.6 Figure S5: Comparison of ROC Geometries

![Figure S5](Figure_S5.png)

**Description:** Shows the actual ROC curves for the three different models, all with AUC ≈ 0.90.

**Shape characteristics:**
- **Equal-variance:** Smooth, symmetric curve
- **S-shaped:** Convex near (0,0), concave near (1,1)
- **Hooked:** Rises quickly at low FPR, then flattens

Despite similar overall discriminative ability (AUC), the curves have visibly different shapes, leading to different optimal operating points, particularly for low-frequency seizures.

---

## 5. Mathematical Methods

### 5.1 Binormal ROC Model

We model the forecast score $S$ as:

$$S | \text{no seizure} \sim N(0,1)$$

$$S | \text{seizure} \sim N(m,1)$$

The separation parameter $m$ determines discrimination. The AUC is:

$$\text{AUC} = \Phi\left(\frac{m}{\sqrt{2}}\right)$$

Therefore:

$$m = \sqrt{2} \cdot \Phi^{-1}(\text{AUC})$$

---

### 5.2 Sensitivity and False Positive Rate

A day is labeled "warning" if $S \geq t$ and "safe" if $S < t$:

$$\text{Sensitivity} = 1 - \Phi(t - m)$$

$$\text{FPR} = 1 - \Phi(t)$$

---

### 5.3 Daily Seizure Probability

Using a Poisson rate $r$ seizures/day, the daily seizure probability is:

$$p = 1 - e^{-r}$$

**Examples:**
- 1 seizure/week: $r = 1/7$, $p \approx 0.134$
- 1 seizure/month: $r = 1/30$, $p \approx 0.033$
- 1 seizure/year: $r = 1/365$, $p \approx 0.0027$

**Note on Poisson Approximation:**
We use a Poisson approximation to convert seizure frequency into daily seizure probability for computational simplicity. Since our analysis depends only on the average daily probability and not on temporal clustering patterns, alternative stochastic models for seizure occurrence would yield equivalent results for individuals with the same average seizure frequency. Whether seizures are truly Poisson-distributed, clustered, or overdispersed does not affect the crash risk calculations, which depend only on the forecasting algorithm's performance (AUC) and the baseline rate.

---

### 5.4 Posterior Probability of Seizure on Safe Days

By Bayes' rule, the probability of a seizure on a day labeled "safe" is:

$$P(\text{seizure} | \text{safe}) = \frac{\Phi(t-m) \cdot p}{\Phi(t-m) \cdot p + \Phi(t)(1-p)}$$

This combines:
- The false negative rate: $\Phi(t-m)$
- The true negative rate: $\Phi(t)$
- The baseline daily seizure probability: $p$

---

### 5.5 Crash Risk on Safe Days

Let $p_0$ be baseline crash risk and $p_{sz}$ be the crash probability given a seizure while driving:

$$\text{CrashRisk} = P(\text{seizure} | \text{safe}) \cdot p_{sz} + [1 - P(\text{seizure} | \text{safe})] \cdot p_0$$

The crash risk multiplier (relative to baseline) is:

$$\text{CrashMultiplier} = \frac{\text{CrashRisk}}{p_0}$$

**Parameters:**
- $p_0 = 1.5 \times 10^{-5}$ (baseline crash risk per trip)
- $p_{sz} = 0.5$ (crash probability given seizure while driving)

---

### 5.6 Time in Warning

The probability that a randomly selected day is labeled "warning" is:

$$P(\text{warning}) = p \cdot \text{Sensitivity} + (1-p) \cdot \text{FPR}$$

Expected warning days per year:

$$D_{\text{warning}} = 365 \times P(\text{warning})$$

Expected driving days per year:

$$D_{\text{drive}} = 365 - D_{\text{warning}}$$

---

### 5.7 Minimum Warning Days for Legal-Limit Safety

We identify thresholds $t$ where:

$$\text{CrashMultiplier} \leq 16$$

(where 16× corresponds to the crash risk at the legal BAC limit of 0.08%)

The minimum $D_{\text{warning}}$ among these thresholds gives the operating point shown as black points in Figure 1.

---

### 5.8 Minimum Warning Days vs AUC (Figure S3)

For each AUC value and seizure frequency, we compute:

$$\text{AUC} \rightarrow \min_t D_{\text{warning}}$$

subject to the constraint that $\text{CrashMultiplier} \leq 16$.

This yields the curves shown in Figure S3.

---

### 5.9 Reproducibility

All computations use:
- Closed-form normal distribution formulas
- Deterministic threshold grids: $t \in [-10, 10]$ with 1000 points
- No randomization or simulation

The complete Python code is provided in [`crashes_vs_TiW.ipynb`](crashes_vs_TiW.ipynb) and will reproduce all figures exactly.

---

### 5.10 Why ROC Shape Matters (and Why It Doesn't)

The binormal ROC model assumes equal variance in the score distributions for seizure and non-seizure days. While this is a simplification, it is:

1. **Standard**: Most widely used parametric ROC representation in biomedical research
2. **Tractable**: Allows closed-form computation of all operating characteristics
3. **Optimistic**: Typically provides near-best-case sensitivity-specificity trade-offs for a given AUC
4. **Appropriate**: Ideal for conceptual analysis asking "what can *any* algorithm with AUC = X achieve?"

However, real-world ROC curves can deviate due to:
- Unequal variances between classes (S-shaped ROCs)
- Mixture distributions (hooked ROCs)
- Finite-sample effects (stepwise ROCs)

**Our sensitivity analysis tests robustness to these deviations.**

---

### 5.11 Alternative ROC Models Tested

We compare three score-generating models, all calibrated to AUC ≈ 0.90:

**1. Equal-variance binormal** (baseline):
- Negatives: $N(0, 1)$
- Positives: $N(m, 1)$ where $m = \sqrt{2} \cdot \Phi^{-1}(0.90) \approx 1.81$

**2. Unequal-variance binormal** (S-shaped):
- Negatives: $N(0, 1)$
- Positives: $N(2.4, 1.4)$
- Larger variance in positives creates S-shaped ROC

**3. Mixture model** (hooked):
- Negatives: $N(0, 1)$
- Positives: $0.7 \cdot N(2.5, 1) + 0.3 \cdot N(0.8, 1)$
- Mixture creates "hooked" ROC that rises quickly then flattens

---

### 5.12 Mathematical Formulations of Alternative ROC Shapes

#### Unequal-Variance Binormal Model

For threshold $t$:

$$\text{Sensitivity} = 1 - \Phi\left(\frac{t - \mu_1}{\sigma_1}\right)$$

$$\text{FPR} = 1 - \Phi(t)$$

Where $\mu_1 = 2.4$ and $\sigma_1 = 1.4$ are chosen to achieve AUC ≈ 0.90.

Posterior probability of seizure on a "safe" day:

$$P(\text{seizure} | \text{safe}) = \frac{\Phi\left(\frac{t - \mu_1}{\sigma_1}\right) \cdot p}{\Phi\left(\frac{t - \mu_1}{\sigma_1}\right) \cdot p + \Phi(t)(1-p)}$$

#### Mixture Model

For a mixture of two Gaussians in the positive class, with mixing weight $w$:

$$\text{Sensitivity} = w \cdot \left[1 - \Phi(t - \mu_{\text{easy}})\right] + (1-w) \cdot \left[1 - \Phi(t - \mu_{\text{hard}})\right]$$

Where $w = 0.7$, $\mu_{\text{easy}} = 2.5$, and $\mu_{\text{hard}} = 0.8$.

Probability of being below threshold for the positive class:

$$P(S < t | \text{seizure}) = w \cdot \Phi(t - \mu_{\text{easy}}) + (1-w) \cdot \Phi(t - \mu_{\text{hard}})$$

---

### 5.13 Impact on Driving Safety Conclusions

The ROC shape sensitivity analysis reveals nuanced but important findings:

**At high seizure frequencies (weekly or monthly):**
- All ROC shapes struggle to achieve safe driving
- Mixture model is most conservative (fewest allowed driving days)
- S-shaped ROC often cannot reach the safety threshold at all
- **Conclusion:** Limited discriminative ability, not ROC shape, is the barrier

**At low seizure frequency (yearly):**
- ROC shape has more substantial impact
- S-shaped ROC can outperform equal-variance binormal (288 vs 268 days/year)
- Mixture model is more conservative (223 days/year)
- **Conclusion:** At low frequencies and high AUC, shape affects *how many* driving days, but all models permit substantial driving

**Overall interpretation:**
- Using the equal-variance binormal model is reasonable and standard
- It tends to give the forecasting algorithm the "benefit of the doubt"
- Main conclusions about difficulty of safe forecasting-based driving policies are **robust to ROC shape assumptions**
- For safety-critical applications, **overall discriminative ability (AUC) matters far more than fine-grained ROC geometry**

---

## 6. Discussion: Validity of the Binormal ROC Assumption

### Is the binormal model a reasonable simplification?

**Yes, for several reasons:**

1. **Standard statistical approximation**: Widely used in biomedical research, diagnostic testing, and signal detection theory

2. **Mathematically tractable**: Closed-form expressions enable transparent, reproducible analysis without simulation

3. **Generally optimistic**: For a given AUC, equal-variance binormal ROC tends to offer near-best-case sensitivity-specificity trade-offs

4. **Appropriate for conceptual analysis**: Our paper addresses "what level of performance (AUC) is needed for safe driving decisions?"—not "how does this specific empirical ROC curve perform?"

### What about real-world ROC curves that aren't binormal?

Empirical ROC curves can indeed deviate from binormal shape due to:
- Unequal variances between seizure and non-seizure score distributions
- Mixture distributions (subpopulations of easy vs. hard-to-predict seizures)
- Nonlinearities in underlying physiological signals
- Finite-sample effects

**However, our sensitivity analysis shows these deviations do not undermine the main conclusions:**

- At **high seizure frequencies** (weekly/monthly), all ROC shapes—including those more optimistic than binormal—fail to support frequent safe driving even at AUC = 0.90
- At **low seizure frequency** (yearly), all ROC shapes with AUC = 0.90 permit substantial driving, though exact days vary by shape
- The fundamental barrier is **limited discriminative ability (AUC)**, not detailed ROC geometry

### Recommendations for algorithm developers

If you are developing a seizure forecasting algorithm:

1. **Aim for AUC ≥ 0.90** as a minimum for driving applications
2. **Characterize your empirical ROC shape**—if it's S-shaped or hooked, this may affect optimal operating points
3. **For patients with frequent seizures**, even AUC = 0.90 may be insufficient for safe, practical driving policies
4. **For patients with rare seizures**, AUC ≥ 0.90 can support meaningful driving opportunities, and ROC shape becomes more important for optimization

---

## 7. Running the Code

### Requirements

```bash
pip install numpy matplotlib scipy
```

### Execution

Open and run the Jupyter notebook:

```bash
jupyter notebook crashes_vs_TiW.ipynb
```

Or run all cells programmatically:

```bash
jupyter nbconvert --to notebook --execute crashes_vs_TiW.ipynb
```

### Outputs

The notebook generates:
- **Five PDF figures** (high-resolution for publication)
- **Five PNG figures** (for display on GitHub)
- **Comprehensive table** (tab-delimited, ready for Word)
- **Detailed statistics** for all AUC values and seizure frequencies

**Figure files:**
- `Figure_1.pdf/png` - Main text figure (driving days vs. AUC)
- `Figure_S1.pdf/png` - Supplementary figure (crash risk vs. warning days)
- `Figure_S2.pdf/png` - Supplementary figure (binormal model schematic)
- `Figure_S3.pdf/png` - Supplementary figure (minimum warning days vs. AUC)
- `Figure_S4.pdf/png` - Supplementary figure (ROC shape sensitivity)
- `Figure_S5.pdf/png` - Supplementary figure (ROC curve geometries)

---

## 8. Citation and Contact

### Citation

[Citation information will be added upon publication]

### License

See [LICENSE](LICENSE) file for details.

---

*Last updated: November 2024*
