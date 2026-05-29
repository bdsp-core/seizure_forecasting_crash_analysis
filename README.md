# Seizure Forecasting and Crash Risk Analysis

**Supplementary Materials for JAMA Neurology Paper**

This repository contains the complete analysis code, mathematical methods, and supplementary materials examining the relationship between seizure forecasting algorithm performance and driving safety.

---

## Table of Contents

### 1. [Overview](#1-overview)
### 2. [Model and Methods](#2-model-and-methods)
   - 2.1 [Binormal ROC Framework](#21-binormal-roc-framework)
   - 2.2 [Daily Seizure Probability](#22-daily-seizure-probability)
   - 2.3 [Posterior Seizure Probability on "Safe" Days](#23-posterior-seizure-probability-on-safe-days)
   - 2.4 [Fatal Crash Risk and the Relative-Risk Derivation](#24-fatal-crash-risk-and-the-relative-risk-derivation)
   - 2.5 [Safety Threshold](#25-safety-threshold)
   - 2.6 [Time in Warning and Driving Days](#26-time-in-warning-and-driving-days)
### 3. [Main Result](#3-main-result)
### 4. [Sensitivity Analyses](#4-sensitivity-analyses)
   - 4.1 [Conditional Fatal-Crash Probability (q_f)](#41-conditional-fatal-crash-probability-q_f)
   - 4.2 [Driving Duration (Exposure Invariance)](#42-driving-duration-exposure-invariance)
   - 4.3 [ROC Curve Shape](#43-roc-curve-shape)
### 5. [Assumptions, Limitations, and Recommendations](#5-assumptions-limitations-and-recommendations)
### 6. [Reproducibility and Running the Code](#6-reproducibility-and-running-the-code)
### 7. [Citation, References, and License](#7-citation-references-and-license)

---

## 1. Overview

This analysis quantifies the trade-offs between seizure forecasting accuracy (measured by AUC), driving exposure, and the driving restrictions required to maintain fatal crash risk at or below a safety threshold of 6× baseline, corresponding to BAC ≈0.06–0.07% for adult drivers. This benchmark is aligned with the 0.05% BAC standard used in Utah and most European countries, and is more conservative than the 0.08% BAC legal limit used in 49 U.S. states. It refers specifically to relative risk of fatal single-vehicle crashes (not legal permissibility) and reflects the principle that AI-assisted medical decisions should meet substantially higher safety standards than merely matching known dangerous activities.

**Key modeling feature.** We model relative fatal crash risk on forecasted "safe" days using a per-hour fatal-crash baseline ($\lambda_f \approx 4.5 \times 10^{-7}$/hr) and a conditional probability $q_f = P(\text{fatal crash} \mid \text{seizure while driving}) = 0.02$ (central estimate; range 0.005–0.05 examined as sensitivity). The probability that a seizure coincides with driving scales as $D/24$ for daily driving duration $D$, but because both the seizure-related risk and the baseline risk scale with exposure, the relative-risk benchmark is approximately invariant to $D$ — only absolute risk scales (Section 2.4).

**Key findings.** With the 6× safety threshold and central $q_f = 0.02$: patients with infrequent seizures (≤1/year) approach unrestricted driving even at low AUC; patients with frequent seizures require high-performance forecasting (AUC ≥ 0.90) to enable meaningful driving. At AUC 0.90, weekly seizures permit ~53 days/year, monthly seizures ~182, and yearly seizures ~365. These results are largely insensitive to driving duration but moderately sensitive to $q_f$ (Section 4).

---

## 2. Model and Methods

The analysis is fully analytical (closed-form); no Monte Carlo simulation is required. This section builds the model in the order it is computed: the forecasting model, the seizure prior, the Bayesian posterior on "safe" days, the crash-risk model, the safety threshold, and the conversion to driving days.

### 2.1 Binormal ROC Framework

![Figure S4: binormal model schematic](Figure_S4.png)

We model the forecasting algorithm's output as a normally distributed score $S$. For a patient day:

- Non-seizure days: $S \sim N(0, 1)$
- Seizure days: $S \sim N(m, 1)$

The separation parameter $m$ is related to AUC by:

$$m = \sqrt{2} \cdot \Phi^{-1}(\text{AUC})$$

For a decision threshold $t$ (the algorithm warns "unsafe to drive" when $S > t$, "safe" when $S \leq t$):

$$\text{Sensitivity} = P(S > t \mid \text{seizure}) = 1 - \Phi(t - m) = \Phi(m - t)$$

$$\text{FPR} = P(S > t \mid \text{no seizure}) = 1 - \Phi(t)$$

The schematic above shows the two score distributions, the threshold, and how sensitivity and FPR are read off. This equal-variance binormal form is the standard simplification; Section 4.3 tests robustness to alternative ROC shapes.

### 2.2 Daily Seizure Probability

For a patient with average seizure rate $R$ (seizures per day), the daily seizure probability under a Poisson process is:

$$p = 1 - e^{-R}$$

| Frequency | $R$ | $p$ |
|---|---|---|
| 1 seizure/week | 1/7 | ≈0.133 |
| 1 seizure/month | 1/30 | ≈0.033 |
| 1 seizure/year | 1/365 | ≈0.0027 |

The Poisson mapping is used only to translate an average rate into a daily probability; the analysis is otherwise agnostic to the temporal structure of seizure risk.

### 2.3 Posterior Seizure Probability on "Safe" Days

When a patient drives on a forecasted "safe" day, the residual crash risk is driven by the posterior probability of a seizure given a negative forecast. By Bayes' theorem:

$$P(\text{seizure} \mid \text{safe}) = \frac{P(\text{safe} \mid \text{seizure}) \cdot p}{P(\text{safe} \mid \text{seizure}) \cdot p + P(\text{safe} \mid \text{no seizure}) \cdot (1-p)}$$

$$= \frac{(1 - \text{Sensitivity}) \cdot p}{(1 - \text{Sensitivity}) \cdot p + (1 - \text{FPR}) \cdot (1-p)} = \frac{\Phi(t - m) \cdot p}{\Phi(t - m) \cdot p + \Phi(t) \cdot (1-p)}$$

### 2.4 Fatal Crash Risk and the Relative-Risk Derivation

Let $D$ be hours of driving per day and $\lambda_f$ the baseline sober fatal-crash rate per driving hour. The baseline (per-day) fatal crash risk for a sober driver is:

$$B(D) = D \cdot \lambda_f$$

On a day when a seizure occurs, the per-day fatal crash risk depends on whether the seizure happens to fall within the driving window:

$$P(\text{fatal crash} \mid \text{seizure day}) = \frac{D}{24} \cdot q_f + \left(1 - \frac{D}{24}\right) \cdot B(D)$$

On a forecasted "safe" day, the residual fatal crash risk is:

$$P(\text{fatal crash} \mid \text{safe day}) = P(\text{seizure} \mid \text{safe}) \cdot P(\text{fatal crash} \mid \text{seizure day}) + (1 - P(\text{seizure} \mid \text{safe})) \cdot B(D)$$

**Parameters:**

| Symbol | Meaning | Value | Source |
|---|---|---|---|
| $\lambda_f$ | Baseline fatal crash rate per hour of sober driving | $4.5 \times 10^{-7}$/hr | NHTSA *Passenger Vehicles 2023* + FHWA *Highway Statistics 2023* + AAA *American Driving Survey 2023* (derivation below) |
| $q_f$ | $P(\text{fatal crash} \mid \text{seizure while driving})$ | $0.02$ (central; range $0.005$–$0.05$) | Inferred severity parameter; see Section 4.1 |
| $D$ | Driving hours per day | 0.5, 1, 2 | — |

**Derivation of the baseline rate $\lambda_f$.** NHTSA *Passenger Vehicles 2023* reports ~44,000 passenger vehicles involved in fatal crashes; FHWA *Highway Statistics 2023* Table VM-1 reports ~2.88 trillion light-duty vehicle-miles traveled. The ratio is ≈1.5 passenger-vehicle fatal-crash involvements per 100 million miles, i.e. $1.5\times 10^{-8}$ per mile. Converting from per-mile to per-hour requires a driving speed: the AAA *American Driving Survey 2023* reports ≈29.1 miles over ≈60.7 minutes per driver per day, i.e. ≈29 mph. Then

$$\lambda_f \approx 1.5\times 10^{-8}\ \text{per mile} \times 29\ \text{mph} \approx 4.4\times 10^{-7}\ \text{per hour} \approx 4.5\times 10^{-7}\,/\text{hr}.$$

(FHWA Table VM-1 supplies the VMT denominator only; the driving speed used for the per-mile→per-hour conversion comes from the AAA survey.) Because this baseline incorporates all non-seizure causes of fatal crashes (distraction, weather, other drivers), the model conservatively attributes this background risk to every driving day regardless of seizure status.

**Relative fatal crash risk.** Let $\pi = P(\text{seizure} \mid \text{safe})$. Substitute the seizure-day expression into the safe-day expression and divide by the baseline $B(D)$:

$$\text{RR}(D) = \frac{P(\text{fatal crash} \mid \text{safe day})}{B(D)} = \frac{\pi \cdot \left[\dfrac{D}{24} q_f + \left(1 - \dfrac{D}{24}\right) B(D)\right] + (1 - \pi) \cdot B(D)}{B(D)}$$

Distribute the numerator and divide each term by $B(D) = D \lambda_f$:

$$\text{RR}(D) = \pi \cdot \frac{(D/24) \, q_f}{D \lambda_f} + \pi \cdot \left(1 - \frac{D}{24}\right) + (1 - \pi)$$

The $D$ in the first term cancels:

$$\text{RR}(D) = \pi \cdot \frac{q_f}{24 \lambda_f} + \pi - \pi \cdot \frac{D}{24} + 1 - \pi$$

The $\pi$ and $-\pi$ cancel, leaving:

$$\text{RR}(D) = 1 + \pi \cdot \left[\frac{q_f}{24 \lambda_f} - \frac{D}{24}\right]$$

This is the *exact* expression. Under our parameters, $q_f / (24 \lambda_f) = 0.02 / (24 \cdot 4.5\times 10^{-7}) \approx 1852$, while $D/24 \leq 2/24 \approx 0.083$ for $D \leq 2$ hours. Since $1852 \gg 0.083$, the $D/24$ term is negligible and we approximate:

$$\boxed{\text{RR}(D) \approx 1 + \pi \cdot \frac{q_f}{24 \lambda_f} = 1 + \pi \cdot A}$$

where $A = q_f / (24 \lambda_f)$ is the **amplification factor**.

**Exposure invariance.** The approximation makes the $D$-dependence vanish: the relative-risk benchmark is exposure-invariant to ~5 parts in $10^5$ at $D = 1$ hr (the residual $D/24$ correction is at most $0.083\,\pi$ versus the dominant $\sim 1852\,\pi$). Absolute fatal crash risk does scale with driving exposure through $B(D)$, but the *relative* risk against the BAC-anchored threshold does not. Section 4.2 confirms this numerically.

### 2.5 Safety Threshold

We use a safety threshold derived from the BAC 0.05% standard. Under the doubling-per-0.02-BAC parametric model of Zador et al. and Compton & Berning, the relative fatal-crash risk at BAC 0.05% is

$$T = 2^{0.05/0.02} \approx 5.66,$$

which is approximately 6× baseline. The prose throughout describes this as a "6× threshold" for readability; the code uses the precise value $T = 2^{0.05/0.02}$. We find the operating threshold $t$ such that

$$\frac{P(\text{fatal crash} \mid \text{safe day})}{B(D)} \leq T,$$

and report the corresponding minimum days in warning (the minimum restriction required to meet the threshold).

### 2.6 Time in Warning and Driving Days

The proportion of days the algorithm flags as high-risk ("time in warning"):

$$P(\text{warning}) = \text{Sensitivity} \cdot p + \text{FPR} \cdot (1-p), \qquad \text{Days in warning/year} = P(\text{warning}) \times 365.$$

The complementary quantity, $(1 - P(\text{warning})) \times 365$, is the number of days per year the patient is permitted to drive. An algorithm that warns every day achieves perfect sensitivity but permits zero driving days; the analysis finds, for each AUC, the operating point that just meets the safety threshold and reports the resulting driving days.

---

## 3. Main Result

**Driving restrictions required to achieve the safety threshold, by seizure frequency and forecasting performance** (1 hr/day driving, $q_f = 0.02$, $\lambda_f = 4.5\times 10^{-7}$/hr):

| Seizure Frequency | AUC | Warning Days/Year | Driving Days/Year | Avg Days Between Drives |
|------------------|-----|-------------------|-------------------|------------------------|
| **1/week** | 0.60 | 365 | 0 | Cannot reach safety threshold |
| | 0.70 | 365 | 0 | Cannot reach safety threshold |
| | 0.80 | 363 | 2 | ~237 |
| | 0.90 | 312 | 53 | 6.9 |
| | 0.95 | 221 | 144 | 2.5 |
| | 0.99 | 91 | 274 | 1.3 |
| **1/month** | 0.60 | 365 | 0 | Cannot reach safety threshold |
| | 0.70 | 364 | 1 | ~497 |
| | 0.80 | 323 | 42 | 8.8 |
| | 0.90 | 183 | 182 | 2.0 |
| | 0.95 | 92 | 273 | 1.3 |
| | 0.99 | 23 | 342 | 1.1 |
| **1/year** | 0.60 | 34 | 331 | 1.1 |
| | 0.70 | 8 | 357 | 1.0 |
| | 0.80 | 2 | 363 | 1.0 |
| | 0.90 | 0 | 365 | 1.0 (already safe) |
| | 0.95 | 0 | 365 | 1.0 (already safe) |
| | 0.99 | 0 | 365 | 1.0 (already safe) |

![Figure 1: driving days vs AUC](Figure_1.png)

**Figure 1.** Annual driving days permitted to keep fatal crash risk below the safety threshold, for three seizure frequencies (green = 1/year, blue = 1/month, orange = 1/week), 1 hr/day driving, $q_f = 0.02$. Filled circles mark AUC 0.60, 0.70, 0.80, 0.90, 0.95, 0.99. Curves are analytic (equal-variance binormal ROC + Bayes' theorem).

The figure below shows the underlying mechanism — how crash risk on "safe" days falls as the algorithm spends more days in warning, and where each AUC curve crosses the safety threshold:

![Figure S1: crash risk vs warning days](Figure_S1.png)

**Figure S1.** Crash risk (× baseline) versus days in warning, by seizure frequency (rows), at 1 hr/day driving. Black curves are AUC 0.60, 0.80, 0.90 (thicker = higher AUC). Shaded bands and dashed lines mark BAC-equivalent risk levels (0.02%, the 0.05% safety threshold, 0.12%). Black circles mark the minimum warning days needed to reach the threshold.

**Key insights.**
- **High AUC is the binding constraint.** Algorithms need AUC ≥ 0.90 to provide meaningful driving days for patients with weekly or monthly seizures.
- **Patients with rare seizures (≤1/year)** are at or near unrestricted driving even at low AUC (≈331 days/year at AUC 0.60), though not literally always-safe.
- **Monthly seizure patients benefit greatly:** AUC 0.90 permits ~182 driving days/year; AUC 0.95 permits ~273.
- **Weekly seizure patients face significant restrictions:** even AUC 0.90 permits only ~53 days/year; AUC 0.80 is essentially insufficient (≤2 days/year).

---

## 4. Sensitivity Analyses

Three analyses test the robustness of the main result: to the most uncertain parameter ($q_f$, Section 4.1), to driving duration (Section 4.2), and to the shape of the ROC curve (Section 4.3).

### 4.1 Conditional Fatal-Crash Probability (q_f)

$q_f = P(\text{fatal crash} \mid \text{seizure while driving})$ is the most uncertain parameter in the model and is not directly reported by any single study; it is an inferred severity parameter. We examined the defensible range $q_f \in [0.005, 0.05]$:

- **Lower bound (0.005):** moderate crash rate (~0.30) given a seizure while driving × moderate case-fatality (~0.02) — closer to baseline fatal-crash severity.
- **Central (0.02):** Gastaut & Zifkin 1987 observed crash rate (~0.55) × case-fatality of seizure-related crashes (~3–5%, inferred from Sheth et al. 2004 and Drazkowski et al. 2003).
- **Upper bound (0.05):** counts near-misses as effective crashes (Gastaut: ~38% additional near-miss rate) with upper-bound severity.

**Driving days/year at AUC = 0.90, 1 hr/day:**

| Seizure Frequency | $q_f$ = 0.005 | $q_f$ = 0.02 (central) | $q_f$ = 0.05 |
|---|---|---|---|
| 1/week | 154 | 53 | 20 |
| 1/month | 314 | 182 | 99 |
| 1/year | 365 | 365 | 334 |

The amplification factor $A = q_f / (24 \lambda_f)$ ranges from ~463 (lower) through ~1852 (central) to ~4630 (upper); the corresponding maximum tolerable $P(\text{seizure} \mid \text{safe})$ for $\text{RR} \leq 5.66$ ranges from ~1.0% down to ~0.10%.

![Figure: q_f sensitivity](Figure_qf_sensitivity.png)

**Interpretation.** Across the full range, the qualitative finding is preserved: weekly-seizure patients cannot achieve unrestricted driving even at AUC 0.90, and yearly-seizure patients remain at or near unrestricted driving. The quantitative allowance for monthly seizures spans roughly a factor of three. Stakeholders may prefer the conservative-end $q_f = 0.05$ until the parameter is better empirically anchored.

### 4.2 Driving Duration (Exposure Invariance)

Section 2.4 shows analytically that relative risk is approximately invariant to driving duration $D$, because both the seizure-related and baseline fatal risks scale with exposure. Numerically, the driving-day allowances are identical to integer rounding across the examined durations:

| Seizure Frequency | AUC | 30 min/day | 1 hr/day | 2 hr/day |
|---|---|---|---|---|
| 1/week | 0.90 | 53 | 53 | 53 |
| 1/month | 0.90 | 182 | 182 | 182 |
| 1/year | 0.80 | 363 | 363 | 363 |

Absolute fatal crash risk still scales with driving duration; an alternative *absolute*-risk benchmark would depend directly on exposure. Under the relative-risk benchmark used here, driving duration is not a material determinant of the allowable driving days.

### 4.3 ROC Curve Shape

The equal-variance binormal assumption implies a specific sensitivity–specificity relationship. Real ROC curves can deviate due to unequal variances (S-shaped), mixture distributions (hooked; some seizures easier to predict than others), or finite-sample effects. We test three score-generating models, all calibrated to AUC ≈ 0.90:

**1. Equal-variance binormal** (baseline): negatives $N(0,1)$, positives $N(m,1)$, $m = \sqrt{2}\,\Phi^{-1}(0.90) \approx 1.81$.

**2. Unequal-variance binormal** (S-shaped): negatives $N(0,1)$, positives $N(2.4, 1.4)$. For threshold $t$,

$$\text{Sensitivity} = 1 - \Phi\!\left(\frac{t - \mu_1}{\sigma_1}\right), \quad \text{FPR} = 1 - \Phi(t), \quad \mu_1 = 2.4,\ \sigma_1 = 1.4,$$

and the posterior on "safe" days uses $\Phi((t-\mu_1)/\sigma_1)$ in place of $\Phi(t-m)$.

**3. Mixture model** (hooked): negatives $N(0,1)$, positives $0.7\,N(2.5,1) + 0.3\,N(0.8,1)$. With mixing weight $w = 0.7$, $\mu_{\text{easy}} = 2.5$, $\mu_{\text{hard}} = 0.8$,

$$\text{Sensitivity} = w\,[1 - \Phi(t - \mu_{\text{easy}})] + (1-w)\,[1 - \Phi(t - \mu_{\text{hard}})],$$

$$P(S < t \mid \text{seizure}) = w\,\Phi(t - \mu_{\text{easy}}) + (1-w)\,\Phi(t - \mu_{\text{hard}}).$$

![Figure S6: ROC geometries](Figure_S6.png)

**Figure S6.** The three ROC curve shapes, all at AUROC ≈ 0.90.

**Driving days/year at AUC ≈ 0.90, 1 hr/day:**

| Seizure Frequency | Equal-variance binormal | S-shaped (unequal variance) | Hooked (mixture) |
|------------------|------------------------|----------------------------|------------------|
| **1/week** | 53 | Cannot reach safety | 1 |
| **1/month** | 182 | 145 | 66 |
| **1/year** | 365 | 365 | 365 |

![Figure S5: ROC shape sensitivity](Figure_S5.png)

**Figure S5.** Crash risk versus warning days for the three ROC shapes, by seizure frequency (1 hr/day, AUC ≈ 0.90).

**Findings.**
- **At high seizure frequencies, ROC shape matters.** Equal-variance binormal is the most optimistic shape; the S-shaped form fails to reach the threshold at all for weekly seizures, and the hooked mixture permits only 1 day. For monthly seizures the spread is 182 → 145 → 66 days/year.
- **At low seizure frequency (yearly), shape is irrelevant** — all three permit essentially full-year driving because the prior seizure probability is already very low.
- **Net:** AUC remains the primary determinant, but ROC geometry is a meaningful secondary factor. Because equal-variance binormal is the most optimistic of the three, real-world (S-shaped or hooked) ROCs at the same AUC will generally permit *fewer* driving days than the main result suggests — so reporting AUC alone may overstate clinical utility for patients with frequent seizures. The qualitative conclusion (high AUC is necessary, and even AUC 0.90 is borderline for weekly seizures) is robust to shape.

---

## 5. Assumptions, Limitations, and Recommendations

**Why the binormal model is a reasonable base case.** It is a standard approximation in diagnostic testing and signal-detection theory, is mathematically tractable (closed-form, reproducible), and for a given AUC tends to offer near-best-case sensitivity–specificity trade-offs — giving the forecasting algorithm the benefit of the doubt. The paper's question is "what level of performance (AUC) is needed for safe driving decisions?", not "how does one specific empirical ROC curve perform?" Section 4.3 quantifies the effect of departures from this assumption.

**Driving-exposure assumptions.**
1. **Seizure timing is uniformly distributed** over the 24-hour day. Many patients have circadian patterns (nocturnal epilepsy, morning clustering); the model is conservative for seizures concentrated outside driving hours and optimistic for daytime clustering.
2. **Driving duration is constant across days.** Real driving varies; the 30 min/day–2 hr/day range brackets typical commuter and heavy-driver patterns (and, per Section 4.2, barely affects the relative-risk result).
3. **$q_f = 0.02$ is an inferred severity parameter** (range 0.005–0.05), decomposing as P(crash | seizure while driving) ≈ 0.55 (Gastaut & Zifkin 1987) × case-fatality ≈ 3–5% (inferred from Sheth et al. 2004 and Drazkowski et al. 2003). It depends on seizure type, aura, road conditions, and vehicle safety features; Section 4.1 reports the sensitivity analysis.

**Recommendations for algorithm developers.**
1. **Aim for AUC ≥ 0.90** as a minimum for driving applications.
2. **Characterize your empirical ROC shape** — an S-shaped or hooked curve at the same AUC permits fewer driving days and shifts optimal operating points.
3. **For patients with frequent seizures,** even AUC = 0.90 may be insufficient for practical driving policies.
4. **For patients with rare seizures,** forecasting may be unnecessary for safety; focus on other quality-of-life benefits.
5. **Consider patient-specific seizure frequency and driving patterns** when counseling about risk.

---

## 6. Reproducibility and Running the Code

All calculations use NumPy, SciPy (`scipy.stats.norm` for the Gaussian CDF/inverse CDF), and Matplotlib, with analytic closed-form expressions.

```bash
pip install numpy matplotlib scipy
jupyter notebook crashes_vs_TiW.ipynb        # interactive
# or run all cells programmatically:
jupyter nbconvert --to notebook --execute crashes_vs_TiW.ipynb
```

**Notebook cells → outputs:**

| Cell | Produces |
|---|---|
| 0 | Figure S1 — crash risk vs. warning days (3 seizure frequencies, 1 hr/day) |
| 1 | Figure 1 — driving days vs. AUC (main result) |
| 2 | Figure S4 — binormal model schematic |
| 3 | Figures S5 & S6 — ROC shape sensitivity and geometries |
| 4–5 | Extended AUC table (tab-delimited, all frequencies/durations) |
| 6 | Figure q_f sensitivity — driving days vs. $q_f$ at AUC 0.90 |

**Figure files:** `Figure_1`, `Figure_S1`, `Figure_S4`, `Figure_S5`, `Figure_S6`, `Figure_qf_sensitivity` (each as `.pdf` and `.png`).

---

## 7. Citation, References, and License

### Citation

[Citation information will be added upon publication]

### References

1. AAA Foundation for Traffic Safety. (2024). *American Driving Survey, 2023*. https://aaafoundation.org/american-driving-survey-2023/
2. National Highway Traffic Safety Administration. *Passenger Vehicles: 2023 Data* (DOT HS 813 723). U.S. Department of Transportation; May 2025.
3. Federal Highway Administration. *Highway Statistics 2023*, Table VM-1. U.S. Department of Transportation; 2024.
4. Gastaut H, Zifkin BG. The risk of automobile accidents with seizures occurring while driving: relation to seizure type. *Neurology*. 1987;37(10):1613–1616.
5. Sheth SG, Krauss G, Krumholz A, Li G. Mortality in epilepsy: driving fatalities vs other causes of death in patients with epilepsy. *Neurology*. 2004;63(6):1002–1007.
6. Drazkowski JF, Fisher RS, Sirven JI, et al. Seizure-related motor vehicle crashes in Arizona before and after reducing the driving restriction from 12 to 3 months. *Mayo Clin Proc*. 2003;78(7):819–825.
7. Zador PL, Krawchuk SA, Voas RB. Alcohol-related relative risk of driver fatalities and driver involvement in fatal crashes in relation to driver age and gender: an update using 1996 data. *J Stud Alcohol*. 2000;61(3):387–395.

(The manuscript reference list is the authoritative citation source; the above supports the supplement's parameter derivations.)

### License

See [LICENSE](LICENSE) file for details.

---

*Last updated: May 28, 2026*
