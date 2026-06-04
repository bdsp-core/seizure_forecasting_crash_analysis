# Seizure Forecasting and Crash Risk Analysis

**Supplementary materials for the JAMA Neurology paper.**

This repository contains the analysis code, the figures, and the full technical
appendix supporting the main paper.

---

## Appendix (PDF)

The full technical appendix lives in **[`appendix.pdf`](appendix.pdf)** (LaTeX
source: [`appendix.tex`](appendix.tex)). It contains:

1. **Overview**
2. **Model and Methods** — binormal ROC framework, daily seizure probability, Bayesian posterior on forecast-safe days, fatal-crash-risk model, the relative-risk derivation, safety threshold, time in warning, driving days
3. **Main Result** — table + figures
4. **Sensitivity Analyses** — $q_f$, driving duration, ROC curve shape
5. **Assumptions, Limitations, and Recommendations**
6. **Reproducibility**

---

## Reproducibility

Every figure and every number in the appendix is reproduced by the single Jupyter
notebook [`crashes_vs_TiW.ipynb`](crashes_vs_TiW.ipynb).

```bash
pip install numpy matplotlib scipy
jupyter notebook crashes_vs_TiW.ipynb        # interactive
# or run all cells programmatically:
jupyter nbconvert --to notebook --execute crashes_vs_TiW.ipynb
```

| Cell | Produces |
|---|---|
| 0 | Figure S2 — crash risk vs. days in warning (3 frequencies, 1 hr/day) |
| 1 | Figure 1 — driving days vs. AUC (main result) |
| 2 | Figure S1 — binormal model schematic |
| 3 | Figures S4 & S5 — ROC shape geometries and sensitivity |
| 4–5 | Extended AUC table (tab-delimited) |
| 6 | Figure S3 — $q_f$ sensitivity |

**Figure files** (PDF and PNG): `Figure_1`, `Figure_S1`–`Figure_S5`.

To rebuild the appendix PDF from the LaTeX source after editing:

```bash
pdflatex appendix.tex && pdflatex appendix.tex   # second pass resolves cross-references
```

---

## Citation

Citation information will be added upon publication.

## License

See [LICENSE](LICENSE).
