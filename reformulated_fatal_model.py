"""
Reformulated seizure-forecasting crash risk model using per-hour FATAL crash
baseline, for comparison with the existing per-trip (any-crash-calibrated) model.

Generates:
  - Figure_1_compare.{pdf,png} : driving days vs AUC for 1hr/day, old vs new
  - Figure_S2_compare.{pdf,png}: driving days vs AUC for 30min and 2hr, old vs new
  - Console table: threshold AUC values under both models for a grid of q_f.

Parameters (new model):
  lambda_f  : baseline fatal crash rate per hour of sober driving (~4.5e-7/hr)
              (NHTSA 2023 DOT HS 813 723 + FHWA VM-1: ~1.4 fatal involvements /
               100M VMT x ~32 mph avg speed)
  q_f       : P(fatal crash | driver has seizure during driving)
              Central estimate 0.02 (from Gastaut & Zifkin 1987 P(crash|seizure
              while driving) ~0.55 x case-fatality ~0.04 from Sheth 2004 +
              Drazkowski 2003). Defensible range 0.005-0.05.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
})

# -----------------------------------------------------------------------------
# Shared parameters
# -----------------------------------------------------------------------------
R = [1/7, 1/30, 1/365]
R_labels = ['1 seizure / week', '1 seizure / month', '1 seizure / year']
auc_grid = np.linspace(0.60, 0.99, 80)
auc_markers = np.array([0.60, 0.70, 0.80, 0.90, 0.95, 0.99])
# Safety threshold: BAC-derived, ~5.66x baseline (manuscript text rounds to "6x")
RR_THRESHOLD = 2**(0.05/0.02)


# -----------------------------------------------------------------------------
# OLD model (current paper): per-trip baseline + 0.5 crash given seizure
# -----------------------------------------------------------------------------
P0_OLD = 1.5e-5                   # "per trip" baseline (actually any-crash)
Q_OLD  = 0.5                      # P(crash | seizure while driving)

def rr_old(p_seiz_given_safe, D):
    """Relative risk under current model (D = driving hours/day)."""
    p_drive = D / 24
    p_crash_seiz_day = p_drive * Q_OLD + (1 - p_drive) * P0_OLD
    pc = p_seiz_given_safe * p_crash_seiz_day + (1 - p_seiz_given_safe) * P0_OLD
    return pc / P0_OLD


# -----------------------------------------------------------------------------
# NEW model: per-hour fatal baseline + fatal-consistent q_f
# -----------------------------------------------------------------------------
LAMBDA_F = 4.5e-7                 # fatal crashes per hour sober driving

def rr_new(p_seiz_given_safe, D, q_f):
    """Relative risk under reformulated fatal model."""
    B = D * LAMBDA_F                        # baseline per day
    p_drive = D / 24
    F_seiz = p_drive * q_f + (1 - p_drive) * B
    F_safe = p_seiz_given_safe * F_seiz + (1 - p_seiz_given_safe) * B
    return F_safe / B


# -----------------------------------------------------------------------------
# Shared: posterior P(seizure | safe) from binormal ROC, sweep threshold
# -----------------------------------------------------------------------------
def sweep_threshold(auc, p_seizure):
    m = np.sqrt(2) * norm.ppf(auc)
    th = np.linspace(-10, 10, 2000)
    sens = norm.cdf(m - th)
    fpr  = 1 - norm.cdf(th)
    num = norm.cdf(th - m) * p_seizure
    den = num + norm.cdf(th) * (1 - p_seizure)
    p_seiz_safe = num / den
    p_warning = sens * p_seizure + fpr * (1 - p_seizure)
    days_warning = p_warning * 365
    return th, sens, fpr, p_seiz_safe, days_warning


def driving_days_for_auc(auc, p_seizure, D, rr_func):
    """Minimum warning days -> max driving days, given a RR function."""
    th, sens, fpr, p_seiz_safe, days_warning = sweep_threshold(auc, p_seizure)
    RR = rr_func(p_seiz_safe, D)

    idx = np.argsort(days_warning)
    dw = days_warning[idx]; rr = RR[idx]; s = sens[idx]; f = fpr[idx]
    below = np.where(rr < RR_THRESHOLD)[0]
    if len(below) == 0:
        return 0.0, np.nan
    k = below[0]
    p_warn = s[k] * p_seizure + f[k] * (1 - p_seizure)
    days_drive = (1 - p_warn) * 365
    return days_drive, dw[k]


# -----------------------------------------------------------------------------
# Compute driving-days curves for both models and a grid of q_f choices
# -----------------------------------------------------------------------------
Q_F_SCENARIOS = {
    "q_f = 0.005 (lower bound; conservative)": 0.005,
    "q_f = 0.02  (central; Gastaut+Sheth)":    0.02,
    "q_f = 0.05  (upper bound; near-misses)":  0.05,
}
Q_F_RECOMMENDED = 0.02

def curves_old(D):
    out = {lab: [] for lab in R_labels}
    for r, lab in zip(R, R_labels):
        p = 1 - np.exp(-r)
        for a in auc_grid:
            d, _ = driving_days_for_auc(a, p, D, rr_old)
            out[lab].append(d)
    return {k: np.array(v) for k, v in out.items()}

def curves_new(D, q_f):
    out = {lab: [] for lab in R_labels}
    for r, lab in zip(R, R_labels):
        p = 1 - np.exp(-r)
        for a in auc_grid:
            d, _ = driving_days_for_auc(a, p, D, lambda ps, DD: rr_new(ps, DD, q_f))
            out[lab].append(d)
    return {k: np.array(v) for k, v in out.items()}


# -----------------------------------------------------------------------------
# Plot: Figure 1 equivalent (D=1hr) -- OLD vs NEW (3 q_f scenarios)
# -----------------------------------------------------------------------------
colors = {
    '1 seizure / week':  '#F4A460',
    '1 seizure / month': '#4682B4',
    '1 seizure / year':  '#2E8B57',
}

def plot_compare_single_D(D, title_suffix, fname):
    fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharey=True)

    # Panel 0: OLD model
    ax = axes[0]
    old = curves_old(D)
    for lab in R_labels:
        ax.plot(auc_grid, old[lab], lw=2.3, color=colors[lab], label=lab)
    ax.set_title(f'Current paper model\n(per-trip, q=0.5)', fontsize=11)

    # Panels 1-3: NEW model for each q_f
    for i, (qlab, qf) in enumerate(Q_F_SCENARIOS.items(), start=1):
        ax = axes[i]
        new = curves_new(D, qf)
        for lab in R_labels:
            ax.plot(auc_grid, new[lab], lw=2.3, color=colors[lab])
        ax.set_title(f'Reformulated fatal\n({qlab})', fontsize=11)

    for ax in axes:
        ax.set_xlim(0.60, 0.99)
        ax.set_ylim(-10, 380)
        ax.set_xlabel('AUC')
        ax.grid(axis='y', ls='--', lw=0.4, alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    axes[0].set_ylabel('Driving days per year')
    axes[0].legend(loc='upper left', fontsize=9, framealpha=0.9)

    fig.suptitle(f'Driving days vs AUC — {title_suffix}', fontsize=13, y=1.02)
    plt.tight_layout()
    fig.savefig(f'{fname}.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig(f'{fname}.png', bbox_inches='tight', facecolor='white', dpi=200)
    plt.close(fig)


# -----------------------------------------------------------------------------
# Numerical comparison table
# -----------------------------------------------------------------------------
def print_comparison_table():
    print()
    print('=' * 92)
    print('  DRIVING DAYS PER YEAR — OLD vs NEW MODEL')
    print('  (Values at RR <= 6x baseline safety threshold)')
    print('=' * 92)
    for D, Dlab in [(0.5, '30 min/day'), (1.0, '1 hr/day'), (2.0, '2 hr/day')]:
        print()
        print(f'  Driving duration: {Dlab}')
        print(f'  {"":26} {"AUC=0.70":>9} {"AUC=0.80":>9} {"AUC=0.90":>9} {"AUC=0.95":>9}')
        for r, rlab in zip(R, R_labels):
            p = 1 - np.exp(-r)
            row_old = [driving_days_for_auc(a, p, D, rr_old)[0] for a in [0.70, 0.80, 0.90, 0.95]]
            print(f'  {rlab:26} OLD (q=0.5,per-trip):')
            print(f'  {"":26} {row_old[0]:>9.0f} {row_old[1]:>9.0f} {row_old[2]:>9.0f} {row_old[3]:>9.0f}')
            for qlab, qf in Q_F_SCENARIOS.items():
                fn = lambda ps, DD: rr_new(ps, DD, qf)
                row = [driving_days_for_auc(a, p, D, fn)[0] for a in [0.70, 0.80, 0.90, 0.95]]
                print(f'  {"":26} NEW ({qlab}):')
                print(f'  {"":26} {row[0]:>9.0f} {row[1]:>9.0f} {row[2]:>9.0f} {row[3]:>9.0f}')
            print()


# -----------------------------------------------------------------------------
# Amplification factor summary
# -----------------------------------------------------------------------------
def print_amp_summary():
    print()
    print('=' * 92)
    print('  AMPLIFICATION FACTOR A = q_f / (24 * lambda_f)')
    print('  RR ~= 1 + P(seizure|safe) * A      (for small D correction)')
    print('=' * 92)
    print(f'  NEW model lambda_f = {LAMBDA_F:.2e} / hour')
    print()
    for qlab, qf in Q_F_SCENARIOS.items():
        A = qf / (24 * LAMBDA_F)
        p_max = (RR_THRESHOLD - 1) / A
        print(f'  {qlab:40s}: A = {A:7.0f}, max P(seiz|safe) for RR<=6 = {p_max*100:.3f}%')
    print()
    print('  OLD model (for reference; amp depends on D because p0 is not scaled):')
    for D in [0.5, 1.0, 2.0]:
        p_drive = D / 24
        A_old = (p_drive * Q_OLD) / P0_OLD    # dominant numerator / denom
        p_max = (RR_THRESHOLD - 1) / A_old
        print(f'  D = {D:>4} hr/day                             : A_eff ~{A_old:6.0f}, '
              f'max P(seiz|safe) for RR<=6 = {p_max*100:.3f}%')


# -----------------------------------------------------------------------------
# Extended AUC table (matches paper's Table 1)
# -----------------------------------------------------------------------------
def print_extended_auc_table(q_f=Q_F_RECOMMENDED):
    auc_ext = [0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
    print()
    print('=' * 92)
    print(f'  EXTENDED AUC TABLE -- NEW MODEL, q_f = {q_f}')
    print('  Columns: warning_days / driving_days / avg_interval_between_drives')
    print('=' * 92)
    for D, Dlab in [(0.5, '30 min/day'), (1.0, '1 hr/day'), (2.0, '2 hr/day')]:
        print()
        print(f'  Driving duration: {Dlab}')
        print(f'  {"Seizure freq":22} {"AUC":>5} {"Warn":>6} {"Drive":>7} {"Interval (d)":>13}')
        for r, rlab in zip(R, R_labels):
            p = 1 - np.exp(-r)
            for a in auc_ext:
                fn = lambda ps, DD: rr_new(ps, DD, q_f)
                days_drive, dw = driving_days_for_auc(a, p, D, fn)
                if np.isnan(dw):
                    print(f'  {rlab:22} {a:>5.2f} {"--":>6} {"--":>7} {"unsafe":>13}')
                    continue
                warn = 365 - days_drive
                interval = 365 / days_drive if days_drive > 0 else np.inf
                print(f'  {rlab:22} {a:>5.2f} {warn:>6.0f} {days_drive:>7.0f} {interval:>13.2f}')
            print()


# -----------------------------------------------------------------------------
# Minimum warning days vs AUC (Figure S3 equivalent)
# -----------------------------------------------------------------------------
def plot_min_warning_vs_auc():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    styles = {
        '1 seizure / week':  ('-',  2.0),
        '1 seizure / month': ('--', 2.0),
        '1 seizure / year':  (':',  2.2),
    }
    for col, (D, Dlab) in enumerate([(0.5, '30 min/day'),
                                     (1.0, '1 hr/day'),
                                     (2.0, '2 hr/day')]):
        ax = axes[col]
        for r, lab in zip(R, R_labels):
            p = 1 - np.exp(-r)
            min_warn = []
            for a in auc_grid:
                fn = lambda ps, DD: rr_new(ps, DD, Q_F_RECOMMENDED)
                dd, dw = driving_days_for_auc(a, p, D, fn)
                min_warn.append(dw if not np.isnan(dw) else np.nan)
            ls, lw = styles[lab]
            ax.plot(auc_grid, min_warn, linestyle=ls, linewidth=lw,
                    color='k', label=lab)
        ax.set_xlim(0.60, 0.99)
        ax.set_ylim(0, 365)
        ax.set_xlabel('AUC')
        ax.set_title(Dlab, fontsize=11)
        ax.grid(axis='y', ls=':', lw=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax2 = ax.twinx()
        ax2.set_ylim(0, 365)
        ticks = np.arange(0, 401, 50)
        ax2.set_yticks(ticks)
        ax2.set_yticklabels([f'{int(365-v)}' for v in ticks])
        if col == 2:
            ax2.set_ylabel('Max driving days/year', fontsize=10)
        if col == 0:
            ax.legend(loc='center right', fontsize=9)
    axes[0].set_ylabel('Min warning days/year', fontsize=10)
    fig.suptitle(f'Minimum warning days vs AUC — reformulated model (q_f = {Q_F_RECOMMENDED})',
                 fontsize=13, y=1.02)
    plt.tight_layout()
    fig.savefig('Figure_S3_compare.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig('Figure_S3_compare.png', bbox_inches='tight', facecolor='white', dpi=200)
    plt.close(fig)


# -----------------------------------------------------------------------------
# q_f sensitivity: driving days at AUC=0.90 as a function of q_f
# -----------------------------------------------------------------------------
def plot_qf_sensitivity():
    qf_grid = np.logspace(np.log10(0.002), np.log10(0.10), 40)
    fig, ax = plt.subplots(figsize=(8, 5))
    for r, lab in zip(R, R_labels):
        p = 1 - np.exp(-r)
        days = []
        for qf in qf_grid:
            fn = lambda ps, DD: rr_new(ps, DD, qf)
            dd, _ = driving_days_for_auc(0.90, p, 1.0, fn)
            days.append(dd)
        ax.plot(qf_grid, days, lw=2.3, color=colors[lab], label=lab)
    ax.axvline(0.005, ls=':', color='gray', alpha=0.7)
    ax.axvline(0.02,  ls='-', color='gray', alpha=0.7)
    ax.axvline(0.05,  ls=':', color='gray', alpha=0.7)
    ax.text(0.005, 370, ' lower', fontsize=9, color='gray', rotation=90, va='top')
    ax.text(0.02,  370, ' central', fontsize=9, color='gray', rotation=90, va='top')
    ax.text(0.05,  370, ' upper', fontsize=9, color='gray', rotation=90, va='top')
    ax.set_xscale('log')
    ax.set_xlabel(r'$q_f = $ P(fatal crash | seizure while driving)')
    ax.set_ylabel('Driving days per year at AUC = 0.90')
    ax.set_title('Sensitivity to $q_f$ (1 hr driving/day, AUC 0.90, RR<=6x)')
    ax.grid(ls='--', lw=0.4, alpha=0.6)
    ax.legend(fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig('Figure_qf_sensitivity.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig('Figure_qf_sensitivity.png', bbox_inches='tight', facecolor='white', dpi=200)
    plt.close(fig)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print_amp_summary()
    print_comparison_table()
    print_extended_auc_table()
    plot_compare_single_D(1.0, '1 hour driving/day',   'Figure_1_compare')
    plot_compare_single_D(0.5, '30 min driving/day',   'Figure_S2_compare_30min')
    plot_compare_single_D(2.0, '2 hours driving/day',  'Figure_S2_compare_2hr')
    plot_min_warning_vs_auc()
    plot_qf_sensitivity()
    print()
    print('Saved: Figure_1_compare.{pdf,png}')
    print('       Figure_S2_compare_30min.{pdf,png}')
    print('       Figure_S2_compare_2hr.{pdf,png}')
    print('       Figure_S3_compare.{pdf,png}')
    print('       Figure_qf_sensitivity.{pdf,png}')
