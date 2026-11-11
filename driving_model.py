"""Seizure forecasting and fatal-crash risk model.

Every number in the technical appendix is computed from the functions in this
module (called by crashes_vs_TiW.ipynb). Equation numbers refer to the appendix.

Model summary
-------------
* Forecast scores (Eq. 2.1): non-seizure days S ~ N(0, 1); seizure days follow
  one of three score models, each calibrated to the target AUC exactly:
    - equal-variance binormal  N(d', 1),        d' = sqrt(2) * Phi^-1(AUC)
    - unequal-variance         N(mu1, sigma1^2), sigma1 = 1.4
    - mixture                  w N(mu_e, 1) + (1-w) N(mu_h, 1), w = 0.7,
                               mu_e / mu_h fixed at 2.5 / 0.8
  A day is forecast safe when S <= t, so FNR(t) = P(S <= t | seizure) and
  TNR(t) = Phi(t).
* Daily seizure probability (Eq. 2.4): p_d = 1 - exp(-R).
* Residual seizure probability on forecast-safe days (Eq. 2.5):
  p_res(t) = FNR p_d / (FNR p_d + TNR (1 - p_d)).
* Relative fatal-crash risk on a forecast-safe day (Eq. 2.13):
  RR = 1 + p_res * (A - D/24), with A = q_f / (24 lambda_f).
* Safety threshold (Eq. 2.15): T = 2^(0.05/0.02) (BAC 0.05% under the Zador
  doubling rule). The operating threshold t* is the largest t with
  p_res(t) <= p_res_max = (T - 1) / (A - D/24) (Eq. 2.16), found by root-finding.
* Permitted driving days per year = 365 * P(forecast safe at t*) (Eqs. 2.6, 2.17).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Parameters (appendix Table 1)
# ---------------------------------------------------------------------------

# Baseline fatal-crash rate per hour of driving (Eq. 2.8):
#   ~44,000 passenger vehicles in fatal crashes (NHTSA Passenger Vehicles 2023)
#   / ~2.88e12 light-duty vehicle-miles (FHWA Highway Statistics 2023, VM-1)
#   = ~1.53e-8 per mile; x ~29 mph (AAA American Driving Survey 2023)
#   = ~4.4e-7 per hour.
LAMBDA_F = 4.4e-7

# P(fatal crash | seizure while driving): central value and sensitivity range.
Q_F = 0.02
Q_F_RANGE = (0.005, 0.02, 0.05)

# Relative-risk safety threshold: BAC 0.05% under the doubling-per-0.02% rule.
BAC_DOUBLING = 0.02          # BAC percentage points per doubling of risk
BAC_THRESHOLD = 0.05         # BAC (%) defining the safety threshold
T_SAFETY = 2 ** (BAC_THRESHOLD / BAC_DOUBLING)   # 5.656854...

DRIVING_HOURS = 1.0          # reference driving exposure (hours/day)
DAYS_PER_YEAR = 365

SEIZURE_RATES = {            # seizures per day
    "1 seizure / week": 1 / 7,
    "1 seizure / month": 1 / 30,
    "1 seizure / year": 1 / 365,
}
AUC_GRID = (0.60, 0.70, 0.80, 0.90, 0.95, 0.99)

# ROC-shape models (appendix Table 5)
UNEQUAL_SIGMA = 1.4
MIXTURE_W = 0.7
MIXTURE_RATIO = 2.5 / 0.8    # mu_easy / mu_hard, held fixed during calibration

# Threshold search interval. Phi() underflows to 0 below about -38, so the
# interval is kept where every probability is representable in float64.
T_LO, T_HI = -35.0, 35.0


def bac_to_rr(bac: float) -> float:
    """Relative risk at a given BAC (%) under the doubling rule (Section 2.5)."""
    return 2 ** (bac / BAC_DOUBLING)


def amplification(q_f: float = Q_F, lambda_f: float = LAMBDA_F) -> float:
    """A = q_f / (24 lambda_f) (Eq. 2.14)."""
    return q_f / (24 * lambda_f)


def p_res_max(D: float = DRIVING_HOURS, q_f: float = Q_F,
              lambda_f: float = LAMBDA_F, T: float = T_SAFETY) -> float:
    """Ceiling on the residual seizure probability (Eq. 2.16)."""
    return (T - 1) / (amplification(q_f, lambda_f) - D / 24)


def daily_seizure_prob(rate: float) -> float:
    """Poisson daily seizure probability (Eq. 2.4)."""
    return -np.expm1(-rate)


# ---------------------------------------------------------------------------
# Score models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScoreModel:
    """Seizure-day score distribution; non-seizure scores are always N(0, 1)."""
    name: str
    kind: str            # 'equal', 'unequal', or 'mixture'
    params: tuple

    # log FNR(t) = log P(S <= t | seizure); logs avoid underflow in far tails
    def log_fnr(self, t):
        t = np.asarray(t, dtype=float)
        if self.kind == "equal":
            (d,) = self.params
            return norm.logcdf(t - d)
        if self.kind == "unequal":
            mu, sigma = self.params
            return norm.logcdf((t - mu) / sigma)
        if self.kind == "mixture":
            w, mu_e, mu_h = self.params
            return np.logaddexp(np.log(w) + norm.logcdf(t - mu_e),
                                np.log1p(-w) + norm.logcdf(t - mu_h))
        raise ValueError(self.kind)

    def fnr(self, t):
        return np.exp(self.log_fnr(t))

    def sensitivity(self, t):
        return -np.expm1(self.log_fnr(t))

    def auc(self) -> float:
        """Closed-form AUC = P(S1 > S0)."""
        if self.kind == "equal":
            (d,) = self.params
            return norm.cdf(d / np.sqrt(2))
        if self.kind == "unequal":
            mu, sigma = self.params
            return norm.cdf(mu / np.sqrt(1 + sigma ** 2))
        w, mu_e, mu_h = self.params
        return w * norm.cdf(mu_e / np.sqrt(2)) + (1 - w) * norm.cdf(mu_h / np.sqrt(2))


def equal_variance(auc: float) -> ScoreModel:
    """Equal-variance binormal, d' = sqrt(2) Phi^-1(AUC) (Eq. 2.2)."""
    return ScoreModel("Equal-variance binormal", "equal",
                      (np.sqrt(2) * norm.ppf(auc),))


def unequal_variance(auc: float, sigma: float = UNEQUAL_SIGMA) -> ScoreModel:
    """Unequal-variance binormal; mu1 = Phi^-1(AUC) sqrt(1 + sigma^2)."""
    mu = norm.ppf(auc) * np.sqrt(1 + sigma ** 2)
    return ScoreModel("Unequal-variance", "unequal", (mu, sigma))


def mixture(auc: float, w: float = MIXTURE_W,
            ratio: float = MIXTURE_RATIO) -> ScoreModel:
    """Two-component mixture; scale (mu_e, mu_h) with fixed ratio to hit AUC."""
    def f(mu_h):
        return (w * norm.cdf(ratio * mu_h / np.sqrt(2))
                + (1 - w) * norm.cdf(mu_h / np.sqrt(2)) - auc)
    mu_h = brentq(f, 1e-9, 10, xtol=1e-14)
    return ScoreModel("Mixture", "mixture", (w, ratio * mu_h, mu_h))


ROC_MODELS = {"Equal-variance binormal": equal_variance,
              "Unequal-variance": unequal_variance,
              "Mixture": mixture}


# ---------------------------------------------------------------------------
# Risk calculations
# ---------------------------------------------------------------------------

def p_res(model: ScoreModel, t, p_d: float):
    """Residual seizure probability on forecast-safe days (Eq. 2.5)."""
    # p_res = 1 / (1 + TNR (1 - p_d) / (FNR p_d)), evaluated in log space
    log_ratio = (norm.logcdf(t) + np.log1p(-p_d)) - (model.log_fnr(t) + np.log(p_d))
    return 1.0 / (1.0 + np.exp(log_ratio))


def p_forecast_safe(model: ScoreModel, t, p_d: float):
    """P(forecast safe) = FNR p_d + TNR (1 - p_d) (Eq. 2.6)."""
    return model.fnr(t) * p_d + norm.cdf(t) * (1 - p_d)


def relative_risk(model: ScoreModel, t, p_d: float, D: float = DRIVING_HOURS,
                  q_f: float = Q_F, lambda_f: float = LAMBDA_F):
    """Exact relative fatal-crash risk on forecast-safe days (Eq. 2.13)."""
    return 1 + p_res(model, t, p_d) * (amplification(q_f, lambda_f) - D / 24)


@dataclass
class OperatingPoint:
    feasible: bool       # False if no threshold meets the risk limit
    unrestricted: bool   # True if driving every day already meets the limit
    t_star: float        # operating threshold (inf if unrestricted, nan if infeasible)
    p_res: float         # residual seizure probability at t*
    driving_days: float  # expected permitted driving days per year
    warning_days: float  # expected warning days per year
    sensitivity: float
    fpr: float
    p_res_floor: float   # min over t of p_res (relevant when infeasible)
    t_floor: float       # threshold at which the floor occurs

    @property
    def interval(self) -> float:
        """Average days between drives = 365 / driving days."""
        return DAYS_PER_YEAR / self.driving_days if self.driving_days > 0 else np.inf


def operating_point(model: ScoreModel, p_d: float, D: float = DRIVING_HOURS,
                    q_f: float = Q_F, lambda_f: float = LAMBDA_F,
                    T: float = T_SAFETY) -> OperatingPoint:
    """Largest threshold t* with p_res(t*) <= p_res_max (Section 2.5).

    P(forecast safe) increases with t for every model, so the largest admissible
    threshold maximizes permitted driving days. For the equal-variance and
    mixture models p_res(t) increases monotonically in t. For the unequal-
    variance model (sigma1 > 1) p_res(t) is U-shaped, so the admissible set is
    an interval whose upper end is found by root-finding to the right of the
    minimum.
    """
    limit = p_res_max(D, q_f, lambda_f, T)
    g = lambda t: p_res(model, t, p_d) - limit

    # Minimum of p_res(t) over t (the floor); for monotone models this is the
    # left end of the search interval.
    res = minimize_scalar(lambda t: np.log(p_res(model, t, p_d)),
                          bounds=(T_LO, T_HI), method="bounded",
                          options={"xatol": 1e-12})
    t_floor = float(res.x)
    floor = float(p_res(model, t_floor, p_d))

    def summarize(t, feasible=True, unrestricted=False):
        if not feasible:
            return OperatingPoint(False, False, np.nan, np.nan, 0.0,
                                  float(DAYS_PER_YEAR), np.nan, np.nan,
                                  floor, t_floor)
        safe = 1.0 if unrestricted else float(p_forecast_safe(model, t, p_d))
        sens = 0.0 if unrestricted else float(model.sensitivity(t))
        fpr = 0.0 if unrestricted else float(norm.sf(t))
        pr = p_d if unrestricted else float(p_res(model, t, p_d))
        return OperatingPoint(True, unrestricted, t, pr, DAYS_PER_YEAR * safe,
                              DAYS_PER_YEAR * (1 - safe), sens, fpr, floor, t_floor)

    if floor > limit:
        return summarize(None, feasible=False)
    # As t -> +inf every day is forecast safe and p_res -> p_d.
    if p_d <= limit:
        return summarize(np.inf, unrestricted=True)
    t_star = brentq(g, t_floor, T_HI, xtol=1e-13, rtol=4 * np.finfo(float).eps)
    return summarize(t_star)


def risk_curve(model: ScoreModel, p_d: float, D: float = DRIVING_HOURS,
               q_f: float = Q_F, lambda_f: float = LAMBDA_F, n: int = 4000):
    """(warning days/year, relative risk) traced over thresholds, for plotting."""
    t = np.linspace(-12, 10, n)
    warn = DAYS_PER_YEAR * (1 - p_forecast_safe(model, t, p_d))
    rr = relative_risk(model, t, p_d, D, q_f, lambda_f)
    return warn, rr
