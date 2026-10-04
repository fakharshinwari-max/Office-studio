"""Analysis ToolPak equivalents, executed server-side with numpy/scipy/statsmodels."""
from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd
from scipy import stats


def run(tool: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        if tool == "descriptive":     return descriptive(params)
        if tool == "histogram":       return histogram(params)
        if tool == "regression":      return regression(params)
        if tool == "correlation":     return correlation(params)
        if tool == "covariance":      return covariance(params)
        if tool == "ttest_paired":    return ttest_paired(params)
        if tool == "ttest_2sample":   return ttest_2sample(params)
        if tool == "ztest":           return ztest(params)
        if tool == "ftest":           return ftest(params)
        if tool == "moving_average":  return moving_average(params)
        if tool == "exp_smoothing":   return exp_smoothing(params)
        if tool == "rank_percentile": return rank_percentile(params)
        if tool == "sampling":        return sampling(params)
        if tool == "fourier":         return fourier(params)
        if tool == "anova_single":    return anova_single(params)
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"Unknown tool {tool}"}


def _arr(params, key="data"):
    v = params.get(key, [])
    out = []
    for x in v:
        try:
            f = float(x)
            if not np.isnan(f):
                out.append(f)
        except (TypeError, ValueError):
            pass
    return np.array(out)


def descriptive(params):
    data = _arr(params)
    if len(data) == 0:
        return {"error": "Empty data"}
    return {
        "count": int(len(data)),
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "mode": _mode(data),
        "std": float(np.std(data, ddof=1)) if len(data) > 1 else 0,
        "sample_variance": float(np.var(data, ddof=1)) if len(data) > 1 else 0,
        "kurtosis": float(stats.kurtosis(data)),
        "skewness": float(stats.skew(data)),
        "range": float(np.ptp(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "sum": float(np.sum(data)),
        "confidence_95": float(1.96 * np.std(data, ddof=1) / np.sqrt(len(data))) if len(data) > 1 else 0,
    }


def _mode(data):
    vals, counts = np.unique(data, return_counts=True)
    return float(vals[np.argmax(counts)])


def histogram(params):
    data = _arr(params)
    if len(data) == 0:
        return {"error": "Empty data"}
    bins = params.get("bins")
    if isinstance(bins, list):
        bins = np.array([float(b) for b in bins])
    else:
        bins = int(bins) if bins else 10
    counts, edges = np.histogram(data, bins=bins)
    return {"counts": counts.tolist(), "bin_edges": edges.tolist()}


def regression(params):
    y = _arr(params, "y")
    X = np.array(params.get("x", []), dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if len(y) == 0 or X.shape[0] == 0:
        return {"error": "Empty data"}
    n, k = X.shape
    X_design = np.hstack([np.ones((n, 1)), X])
    beta, residuals, rank, sv = np.linalg.lstsq(X_design, y, rcond=None)
    y_hat = X_design @ beta
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else 0
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1) if n > k + 1 else r2
    se = float(np.sqrt(ss_res / (n - k - 1))) if n > k + 1 else 0
    try:
        cov = se ** 2 * np.linalg.inv(X_design.T @ X_design)
        se_beta = np.sqrt(np.diag(cov))
        t_stats = beta / se_beta
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n - k - 1))
    except Exception:
        se_beta = np.zeros_like(beta)
        t_stats = np.zeros_like(beta)
        p_values = np.zeros_like(beta)
    return {
        "coefficients": [
            {"name": "Intercept" if i == 0 else f"X{i}", "value": float(b),
             "se": float(s), "t": float(t), "p": float(p)}
            for i, (b, s, t, p) in enumerate(zip(beta, se_beta, t_stats, p_values))
        ],
        "r_squared": r2,
        "adjusted_r_squared": adj_r2,
        "std_error": se,
        "observations": n,
        "f_statistic": float((ss_tot - ss_res) / k / (ss_res / (n - k - 1))) if n > k + 1 and k else 0,
    }


def correlation(params):
    columns = params.get("columns", [])
    if not columns:
        return {"error": "No columns"}
    df = pd.DataFrame(columns)
    return {"matrix": df.corr().to_dict(), "labels": list(df.columns)}


def covariance(params):
    columns = params.get("columns", [])
    if not columns:
        return {"error": "No columns"}
    df = pd.DataFrame(columns)
    return {"matrix": df.cov().to_dict(), "labels": list(df.columns)}


def ttest_paired(params):
    a = _arr(params, "a"); b = _arr(params, "b")
    t, p = stats.ttest_rel(a, b)
    return {"t": float(t), "p": float(p), "df": int(len(a) - 1)}


def ttest_2sample(params):
    a = _arr(params, "a"); b = _arr(params, "b")
    t, p = stats.ttest_ind(a, b, equal_var=params.get("equal_var", False))
    return {"t": float(t), "p": float(p), "df": float(len(a) + len(b) - 2)}


def ztest(params):
    data = _arr(params)
    mu = params.get("mu", 0)
    sigma = params.get("sigma", float(np.std(data, ddof=1)))
    z = (np.mean(data) - mu) / (sigma / np.sqrt(len(data)))
    p = 2 * (1 - stats.norm.cdf(np.abs(z)))
    return {"z": float(z), "p": float(p)}


def ftest(params):
    a = _arr(params, "a"); b = _arr(params, "b")
    f = float(np.var(a, ddof=1) / np.var(b, ddof=1))
    df1, df2 = len(a) - 1, len(b) - 1
    p = 2 * min(stats.f.cdf(f, df1, df2), 1 - stats.f.cdf(f, df1, df2))
    return {"f": f, "df1": df1, "df2": df2, "p": float(p)}


def moving_average(params):
    data = _arr(params)
    period = int(params.get("period", 3))
    out = []
    for i in range(len(data)):
        if i < period - 1:
            out.append(None)
        else:
            out.append(float(np.mean(data[i - period + 1:i + 1])))
    return {"values": out}


def exp_smoothing(params):
    data = _arr(params)
    alpha = float(params.get("alpha", 0.3))
    out = [float(data[0])] if len(data) else []
    for i in range(1, len(data)):
        out.append(alpha * float(data[i]) + (1 - alpha) * out[-1])
    return {"values": out}


def rank_percentile(params):
    data = _arr(params)
    order = np.argsort(data)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(data) + 1)
    percentiles = ranks / len(data) * 100
    return {"ranks": ranks.tolist(), "percentiles": percentiles.tolist()}


def sampling(params):
    data = _arr(params)
    size = int(params.get("size", min(10, len(data))))
    period = int(params.get("period", 1))
    if params.get("method") == "periodic":
        return {"values": data[::period][:size].tolist()}
    rng = np.random.default_rng(seed=params.get("seed", 42))
    return {"values": rng.choice(data, size=size, replace=False).tolist()}


def fourier(params):
    data = _arr(params)
    fft = np.fft.fft(data)
    return {"real": fft.real.tolist(), "imag": fft.imag.tolist()}


def anova_single(params):
    groups = [np.array(g, dtype=float) for g in params.get("groups", [])]
    f, p = stats.f_oneway(*groups)
    return {"f": float(f), "p": float(p)}