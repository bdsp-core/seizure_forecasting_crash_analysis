# Seizure Forecasting and Crash Risk Analysis

This repository contains the analysis code and supplementary materials for a JAMA Neurology paper examining the relationship between seizure forecasting algorithm performance and driving safety.

## Overview

This analysis quantifies the trade-offs between seizure forecasting accuracy (measured by AUC) and driving restrictions required to maintain crash risk at or below legal intoxication levels (approximately 16× baseline risk). The key finding: even high-performance forecasting algorithms require substantial driving restrictions for patients with frequent seizures.

## Repository Contents

- [`crashes_vs_TiW.ipynb`](crashes_vs_TiW.ipynb) - Jupyter notebook containing all analysis code
- Figure PDFs:
  - `Figure_1.pdf` - Main figure showing crash risk vs. warning days
  - `Figure_S0.pdf` - Schematic of binormal forecast model
  - `Figure_S1.pdf` - Minimum warning days vs. AUC

## Key Figures

### Figure 1: Crash Risk vs. Days in Warning per Year

This figure shows how crash risk (relative to baseline) varies with the number of days per year a patient spends in "warning" (not allowed to drive) for three seizure frequencies and three AUC values.

**Key features:**
- Light blue shaded region: "Safe" zone (below legal limit crash risk)
- Light pink shaded region: "Unsafe" zone (above legal limit)
- Red dashed vertical lines: Minimum warning days needed to reach legal-limit safety
- Horizontal reference lines: Crash risk equivalents for alcohol consumption (1, 3, 4, 6 drinks)

### Figure S0: Binormal Forecast Model Schematic

Illustrates the statistical model underlying the analysis:
- Forecast scores on non-seizure days: N(0,1)
- Forecast scores on seizure days: N(m,1)
- Threshold *t* defines the operating point

The Bayes' theorem box shows how forecast performance combines with baseline seizure probability to compute posterior seizure risk on "safe" days.

### Figure S1: Minimum Warning Days Required for Legal-Limit Safety

Shows the minimum number of warning days per year needed to achieve legal-limit driving safety as a function of AUC, for three seizure frequencies:
- Solid line: 1 seizure/week
- Dashed line: 1 seizure/month
- Dotted line: 1 seizure/year

The right y-axis converts warning days to maximum allowed driving days (365 − warning days).

## Mathematical Methods

### S1. Binormal ROC Model

We model the forecast score $S$ as:

$$S | \text{no seizure} \sim N(0,1)$$

$$S | \text{seizure} \sim N(m,1)$$

The separation parameter $m$ determines discrimination. The AUC is:

$$\text{AUC} = \Phi\left(\frac{m}{\sqrt{2}}\right)$$

Therefore:

$$m = \sqrt{2} \, \Phi^{-1}(\text{AUC})$$

### S2. Sensitivity and FPR for Any Threshold

A day is labeled "warning" if $S \geq t$ and "safe" if $S < t$:

$$\text{Sensitivity} = 1 - \Phi(t - m)$$

$$\text{FPR} = 1 - \Phi(t)$$

### S3. Daily Seizure Probability

Using a Poisson rate $r$ seizures/day, the daily seizure probability is:

$$p = 1 - e^{-r}$$

For example:
- 1 seizure/week: $r = 1/7$, $p \approx 0.134$
- 1 seizure/month: $r = 1/30$, $p \approx 0.033$
- 1 seizure/year: $r = 1/365$, $p \approx 0.0027$

### S4. Posterior Probability of Seizure on "Safe" Days

By Bayes' rule, the probability of a seizure on a day labeled "safe" is:

$$P(\text{seizure} | \text{safe}) = \frac{\Phi(t-m) \, p}{\Phi(t-m) \, p + \Phi(t)(1-p)}$$

This combines:
- The false negative rate: $\Phi(t-m)$
- The true negative rate: $\Phi(t)$
- The baseline daily seizure probability: $p$

### S5. Crash Risk on Safe Days

Let $p_0$ be baseline crash risk (per mile driven) and $p_{sz}$ be the crash probability given a seizure while driving. The crash risk on days labeled "safe" is:

$$\text{CrashRisk} = P(\text{seizure} | \text{safe}) \cdot p_{sz} + [1 - P(\text{seizure} | \text{safe})] \cdot p_0$$

The crash risk multiplier (relative to baseline) is:

$$\text{CrashMultiplier} = \frac{\text{CrashRisk}}{p_0}$$

**Parameters used:**
- $p_0 = 1.5 \times 10^{-5}$ (baseline crash risk per trip)
- $p_{sz} = 0.5$ (crash probability given seizure while driving)

### S6. Time in Warning

The probability that a randomly selected day is labeled "warning" is:

$$P(\text{warning}) = p \cdot \text{Sensitivity} + (1-p) \cdot \text{FPR}$$

Expected warning days per year:

$$D_{\text{warning}} = 365 \times P(\text{warning})$$

Expected driving days per year:

$$D_{\text{drive}} = 365 - D_{\text{warning}}$$

### S7. Minimum Warning Days for Legal-Limit Safety

We identify thresholds $t$ where:

$$\text{CrashMultiplier} \leq 16$$

(where 16× corresponds to the crash risk at the legal BAC limit of 0.08%)

The minimum $D_{\text{warning}}$ among these thresholds gives the operating point shown as red points in Figure 1.

### S8. Minimum Warning Days vs AUC (Figure S1)

For each AUC value and seizure frequency, we compute:

$$\text{AUC} \rightarrow \min_t D_{\text{warning}}$$

subject to the constraint that $\text{CrashMultiplier} \leq 16$.

This yields the curves shown in Figure S1.

### S9. Reproducibility

All computations use:
- Closed-form normal distribution formulas
- Deterministic threshold grids: $t \in [-10, 10]$ with 1000 points
- No randomization or simulation

The complete Python code is provided in [`crashes_vs_TiW.ipynb`](crashes_vs_TiW.ipynb) and will reproduce all figures exactly.

## Running the Code

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

The notebook generates three PDF figures:
- `Figure_1.pdf`
- `Figure_S0.pdf`
- `Figure_S1.pdf`

## Key Results

At the legal-limit safety threshold (16× baseline crash risk):

| Seizure Frequency | AUC | Warning Days/Year | Driving Days/Year | Avg Days Between Drives |
|------------------|-----|-------------------|-------------------|------------------------|
| **1/week** | 0.60 | 365 | 0 | ∞ |
| | 0.90 | 331 | 34 | 10.7 |
| | 0.95 | 279 | 86 | 4.2 |
| **1/month** | 0.60 | 365 | 0 | ∞ |
| | 0.90 | 149 | 216 | 1.7 |
| | 0.95 | 93 | 272 | 1.3 |
| **1/year** | 0.60 | 184 | 181 | 2.0 |
| | 0.90 | 12 | 353 | 1.0 |
| | 0.95 | 7 | 358 | 1.0 |

**Interpretation:** Even with excellent forecasting performance (AUC = 0.95), patients with weekly seizures can only drive ~86 days per year (average of one every 4 days) to maintain crash risk at legal intoxication levels. Only patients with rare seizures (1/year) achieve near-daily driving with high-AUC algorithms.

## Citation

[Citation information will be added upon publication]

## License

See [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open a GitHub issue or contact the authors.
