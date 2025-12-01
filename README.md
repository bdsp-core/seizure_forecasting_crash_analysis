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
  - `Figure_ROC_shapes.pdf` - ROC shape sensitivity analysis (main)
  - `Figure_ROC_shapes_curves.pdf` - Comparison of ROC curve geometries

## Key Figures

### Figure 1: Crash Risk vs. Days in Warning per Year

![Figure 1](Figure_1.pdf)

This figure shows how crash risk (relative to baseline) varies with the number of days per year a patient spends in "warning" (not allowed to drive) for three seizure frequencies and three AUC values (0.6, 0.8, 0.9).

**Key features:**
- Light green shaded region: "Safe" zone (below 1-drink equivalent)
- Light yellow shaded region: "Caution" zone (1-4 drinks equivalent)
- Light pink shaded region: "Unsafe" zone (above legal limit)
- Black dashed vertical lines: Minimum warning days needed to reach legal-limit safety
- Horizontal reference lines: Crash risk equivalents for alcohol consumption (1, 3, 4, 6 drinks)

**Black curves** represent different AUC values (thicker lines = higher AUC), showing the fundamental trade-off between crash risk and driving restrictions.

### Figure S0: Binormal Forecast Model Schematic

![Figure S0](Figure_S0.pdf)

Illustrates the statistical model underlying the primary analysis:
- Forecast scores on non-seizure days: N(0,1)
- Forecast scores on seizure days: N(m,1)
- Threshold *t* defines the operating point

The Bayes' theorem box shows how forecast performance combines with baseline seizure probability to compute posterior seizure risk on "safe" days.

### Figure S1: Minimum Warning Days Required for Legal-Limit Safety

![Figure S1](Figure_S1.pdf)

Shows the minimum number of warning days per year needed to achieve legal-limit driving safety as a function of AUC, for three seizure frequencies:
- Solid line: 1 seizure/week
- Dashed line: 1 seizure/month
- Dotted line: 1 seizure/year

The right y-axis converts warning days to maximum allowed driving days (365 − warning days). This figure demonstrates that achieving safety with high seizure frequencies requires extremely high AUC values.

### Figure ROC_shapes: Sensitivity to ROC Curve Shape

![Figure ROC_shapes](Figure_ROC_shapes.pdf)

This figure addresses the question: **"Do our conclusions depend on assuming a binormal (symmetric) ROC curve?"**

We compare three different ROC curve shapes, all calibrated to AUC ≈ 0.90:

1. **Equal-variance binormal** (black): The standard symmetric ROC curve used in the main analysis
2. **Unequal-variance binormal** (blue): An S-shaped ROC curve arising when positive and negative classes have different variances
3. **Mixture model** (red): A "hooked" ROC curve arising when the positive class is a mixture of easy-to-detect and hard-to-detect cases

**Key finding:** While ROC shape affects the *specific number* of allowable driving days, it does not change the qualitative conclusion that high seizure frequencies require severe driving restrictions even with excellent forecasting (AUC = 0.90).

### Figure ROC_shapes_curves: Comparison of ROC Geometries

![Figure ROC_shapes_curves](Figure_ROC_shapes_curves.pdf)

Shows the actual ROC curves for the three different models, all with AUC ≈ 0.90. Despite similar overall discriminative ability (AUC), the curves have visibly different shapes:
- Equal-variance: Smooth, symmetric curve
- S-shaped: Convex near (0,0), concave near (1,1)
- Hooked: Rises quickly at low FPR, then flattens

These shape differences lead to different optimal operating points, particularly for low-frequency seizures.

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

The minimum $D_{\text{warning}}$ among these thresholds gives the operating point shown as black points in Figure 1.

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

### S10. Why ROC Shape Matters (and Why It Doesn't)

The binormal ROC model assumes equal variance in the score distributions for seizure and non-seizure days. While this is a simplification, it is:

1. **Standard**: The binormal model is the most widely used parametric ROC representation in biomedical research
2. **Tractable**: It allows closed-form computation of all operating characteristics
3. **Optimistic**: For a given AUC, the equal-variance binormal ROC typically provides near-best-case sensitivity-specificity trade-offs
4. **Appropriate for conceptual analysis**: Our question is "what can *any* forecasting algorithm with AUC = X achieve?", not "what does this specific empirical ROC curve imply?"

However, real-world ROC curves can deviate from the idealized binormal shape due to:
- Unequal variances between classes (producing S-shaped ROCs)
- Mixture distributions (producing "hooked" ROCs)
- Finite-sample effects (producing stepwise ROCs)

To test robustness, we analyze alternative ROC shapes with the same AUC.

### S11. Alternative ROC Models Tested

We compare three score-generating models, all calibrated to AUC ≈ 0.90:

1. **Equal-variance binormal** (baseline model):
   - Negatives: $N(0, 1)$
   - Positives: $N(m, 1)$ where $m = \sqrt{2} \, \Phi^{-1}(0.90) \approx 1.81$

2. **Unequal-variance binormal** (S-shaped ROC):
   - Negatives: $N(0, 1)$
   - Positives: $N(2.4, 1.4)$
   - The larger variance in positives creates an S-shaped ROC

3. **Mixture model** (hooked ROC):
   - Negatives: $N(0, 1)$
   - Positives: $0.7 \cdot N(2.5, 1) + 0.3 \cdot N(0.8, 1)$
   - The mixture creates a "hooked" ROC that rises quickly then flattens

### S12. Mathematical Formulations of Alternative ROC Shapes

#### Unequal-Variance Binormal Model

For threshold $t$:

$$\text{Sensitivity} = 1 - \Phi\left(\frac{t - \mu_1}{\sigma_1}\right)$$

$$\text{FPR} = 1 - \Phi(t)$$

Where $\mu_1 = 2.4$ and $\sigma_1 = 1.4$ are chosen to achieve AUC ≈ 0.90.

The posterior probability of seizure on a "safe" day:

$$P(\text{seizure} | \text{safe}) = \frac{\Phi\left(\frac{t - \mu_1}{\sigma_1}\right) \, p}{\Phi\left(\frac{t - \mu_1}{\sigma_1}\right) \, p + \Phi(t)(1-p)}$$

#### Mixture Model

For a mixture of two Gaussians in the positive class, with mixing weight $w$:

$$\text{Sensitivity} = w \cdot \left[1 - \Phi(t - \mu_{\text{easy}})\right] + (1-w) \cdot \left[1 - \Phi(t - \mu_{\text{hard}})\right]$$

Where $w = 0.7$, $\mu_{\text{easy}} = 2.5$, and $\mu_{\text{hard}} = 0.8$.

The probability of being below threshold for the positive class:

$$P(S < t | \text{seizure}) = w \cdot \Phi(t - \mu_{\text{easy}}) + (1-w) \cdot \Phi(t - \mu_{\text{hard}})$$

This is used in Bayes' rule to compute crash risk on safe days.

### S13. Impact on Driving Safety Conclusions

The ROC shape sensitivity analysis reveals nuanced but important findings:

**At high seizure frequencies (weekly or monthly):**
- All ROC shapes struggle to achieve safe driving
- The mixture model is most conservative (fewest allowed driving days)
- The S-shaped ROC often cannot reach the safety threshold at all
- **Conclusion**: Limited discriminative ability, not ROC shape, is the barrier

**At low seizure frequency (yearly):**
- ROC shape has a more substantial impact
- S-shaped ROC can outperform equal-variance binormal (288 vs 268 days/year)
- Mixture model is more conservative (223 days/year)
- **Conclusion**: At low frequencies and high AUC, shape affects *how many* driving days, but all models permit substantial driving

**Overall interpretation:**
- Using the equal-variance binormal model is a reasonable, standard approach
- It tends to give the forecasting algorithm the "benefit of the doubt"
- Our main conclusions about the difficulty of safe forecasting-based driving policies are robust to ROC shape assumptions
- For safety-critical applications, the overall discriminative ability (AUC) matters far more than the fine-grained ROC geometry

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

The notebook generates five PDF figures:
- `Figure_1.pdf`
- `Figure_S0.pdf`
- `Figure_S1.pdf`
- `Figure_ROC_shapes.pdf`
- `Figure_ROC_shapes_curves.pdf`

## Key Results

### Main Analysis: Equal-Variance Binormal ROC

At the legal-limit safety threshold (16× baseline crash risk):

| Seizure Frequency | AUC | Warning Days/Year | Driving Days/Year | Avg Days Between Drives |
|------------------|-----|-------------------|-------------------|------------------------|
| **1/week** | 0.60 | — | — | Cannot reach safety threshold |
| | 0.80 | 365 | 0 | 59,333 |
| | 0.90 | 358 | 7 | 55 |
| **1/month** | 0.60 | — | — | Cannot reach safety threshold |
| | 0.80 | 364 | 1 | 396 |
| | 0.90 | 318 | 47 | 8 |
| **1/year** | 0.60 | 365 | 0 | 680,859 |
| | 0.80 | 238 | 127 | 3 |
| | 0.90 | 97 | 268 | 1.4 |

**Interpretation:** Even with high forecasting performance (AUC = 0.90), patients with weekly seizures can only drive ~7 days per year (average of one every 55 days) to maintain crash risk at legal intoxication levels. Patients with monthly seizures achieve ~47 driving days per year (one every 8 days) at AUC = 0.90. Only patients with rare seizures (1/year) achieve frequent driving opportunities with high-AUC algorithms, with 268 driving days per year at AUC = 0.90.

### ROC Shape Sensitivity Analysis: AUC ≈ 0.90

Comparison of driving days allowed per year across different ROC shapes:

| Seizure Frequency | Equal-variance binormal | S-shaped (unequal variance) | Hooked (mixture) |
|------------------|------------------------|----------------------------|------------------|
| **1/week** | 7 days | Cannot reach safety | 0 days |
| **1/month** | 47 days | Cannot reach safety | 0 days |
| **1/year** | 268 days | **288 days** | 223 days |

**Key observations at AUC = 0.90:**

1. **For weekly seizures**: Only the equal-variance binormal allows *any* driving (7 days/year). The S-shaped ROC cannot reach the safety threshold, and the mixture model allows essentially no driving. This demonstrates that high seizure frequencies are problematic regardless of ROC shape.

2. **For monthly seizures**: Similar pattern—only the equal-variance binormal permits reasonable driving (47 days/year). Other ROC shapes are too conservative or cannot achieve safety.

3. **For yearly seizures**: All three ROC shapes allow substantial driving, but with important differences:
   - The **S-shaped ROC performs best** (288 days/year = 79% of days)
   - The **equal-variance binormal** is in the middle (268 days/year = 73% of days)
   - The **mixture model is most conservative** (223 days/year = 61% of days)

**Why does the S-shaped ROC perform better for low-frequency seizures?**

At low base rates (yearly seizures), the optimal strategy is to achieve high specificity without requiring extreme sensitivity. The S-shaped ROC, due to its unequal variance structure, can achieve excellent specificity at moderate sensitivity levels—exactly what's needed when seizures are rare.

**Bottom line:**
- **Shape matters more at higher seizure frequencies**, where all models struggle
- At **low frequencies with high AUC**, shape affects the *magnitude* of benefit, but all models support driving
- The **equal-variance binormal is a reasonable middle ground** and is often optimistic
- Our conclusions about the fundamental challenges of forecasting-based driving policies are **robust to ROC shape assumptions**

## Discussion: Validity of the Binormal ROC Assumption

### Is the binormal model a reasonable simplification?

**Yes, for several reasons:**

1. **It's a standard statistical approximation**: The binormal ROC model is widely used in biomedical research, diagnostic testing, and signal detection theory. It provides a clean, parametric representation of classifier performance.

2. **It's mathematically tractable**: Closed-form expressions for sensitivity, specificity, and posterior probabilities enable transparent, reproducible analysis without simulation.

3. **It's generally optimistic**: For a given AUC, the equal-variance binormal ROC tends to offer near-best-case sensitivity-specificity trade-offs. Using this model gives the forecasting algorithm the benefit of the doubt.

4. **It's appropriate for conceptual analysis**: Our paper addresses the question "what level of performance (AUC) is needed for safe driving decisions?"—not "how does this specific empirical ROC curve perform?" The binormal model is ideal for this conceptual analysis.

### What about real-world ROC curves that aren't binormal?

Empirical ROC curves can indeed deviate from the binormal shape due to:
- Unequal variances between seizure and non-seizure score distributions
- Mixture distributions (subpopulations of easy vs. hard-to-predict seizures)
- Nonlinearities in the underlying physiological signals
- Finite-sample effects

**However, our sensitivity analysis shows that these deviations do not undermine the main conclusions:**

- At **high seizure frequencies** (weekly/monthly), all ROC shapes—including those that are more optimistic than binormal—fail to support frequent safe driving even at AUC = 0.90
- At **low seizure frequency** (yearly), all ROC shapes with AUC = 0.90 permit substantial driving, though the exact number of days varies by shape
- The fundamental barrier is **limited discriminative ability (AUC)**, not the detailed ROC geometry

### Recommendation for forecasting algorithm developers

If you are developing a seizure forecasting algorithm:

1. **Aim for AUC ≥ 0.90** as a minimum for driving applications
2. **Characterize your empirical ROC shape**—if it's S-shaped or hooked, this may affect optimal operating points
3. **For patients with frequent seizures**, even AUC = 0.90 may be insufficient for safe, practical driving policies
4. **For patients with rare seizures**, AUC ≥ 0.90 can support meaningful driving opportunities, and ROC shape becomes more important for optimization

## Citation

[Citation information will be added upon publication]

## License

See [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open a GitHub issue or contact the authors.
