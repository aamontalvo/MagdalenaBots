#!/usr/bin/env python3
"""
02_cartillas_caudales_resto.py
==============================

Regenera Fig1 (serie de tiempo), Fig4 (curvas de frecuencia de caudales
excedidos) y Fig5 (ajuste de distribucion de extremos) de las cartillas
de caudales, obedeciendo la convencion de niveles v2.1:

- Fuente: Datos_Imputados_Caudales.csv (serie imputada L1+L2, derivada de
  la base oficial sin outliers).
- Fig1: serie completa (originales + imputados), con anotacion de periodo,
  total de registros y porcentajes de originales e imputados (misma
  convencion de niveles).
- Fig4 y Fig5: solo datos originales (Nivel_Imputacion == 0), como en niveles.
- Titulo solo con el nombre de la estacion (sin codigo), eje "Caudal (m3/s)".
- Sobrescribe los archivos en cartillas_estaciones/Caudales/.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMPUTED_FILE = (
    PROJECT_ROOT / "backend" / "data" / "work" / "caudales_v1"
    / "output" / "Datos_Imputados_Caudales.csv"
)
CARTILLAS_DIR = PROJECT_ROOT / "cartillas_estaciones" / "Caudales"

GEO_ORDER = [
    "CALAMAR", "MAGANGUE", "BARBOSA", "ARMENIA", "RIO_NUEVO",
    "LAS_PALOMAS", "LAS_AGUADAS", "EL_BANCO", "PENONCITO",
    "EL_CONTENTO", "SITIO_NUEVO", "SAN_PABLO", "PUERTO_BERRIO", "PUERTO_SALGAR",
]

DISPLAY_NAMES = {
    "CALAMAR": "Calamar", "MAGANGUE": "Magangué", "BARBOSA": "Barbosa",
    "ARMENIA": "Armenia", "RIO_NUEVO": "Río Nuevo", "LAS_PALOMAS": "Las Palomas",
    "LAS_AGUADAS": "Las Aguadas", "EL_BANCO": "El Banco", "PENONCITO": "Peñoncito",
    "EL_CONTENTO": "El Contento", "SITIO_NUEVO": "Sitio Nuevo",
    "SAN_PABLO": "San Pablo", "PUERTO_BERRIO": "Puerto Berrío",
    "PUERTO_SALGAR": "Puerto Salgar",
}

MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
         "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_imputados():
    df = pd.read_csv(IMPUTED_FILE, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df


def plot_fig1_serie(st_all, station, output_path):
    """Serie completa (originales + imputados) con porcentajes, como niveles."""
    s = st_all.sort_values("Fecha")
    valid = s.dropna(subset=["Caudal"])
    if len(valid) < 30:
        return False

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(valid["Fecha"], valid["Caudal"], "k-", linewidth=0.8)

    total = len(s)
    originales = (s["Nivel_Imputacion"] == 0).sum()
    imputados = (s["Nivel_Imputacion"] > 0).sum()
    pct_o = originales / total * 100 if total else 0
    pct_i = imputados / total * 100 if total else 0
    y0 = int(s["Fecha"].dt.year.min())
    y1 = int(s["Fecha"].dt.year.max())

    annotation = (
        f"Periodo: {y0}-{y1} | Total: {total:,} registros\n"
        f"Originales: {pct_o:.1f}% | Imputados: {pct_i:.1f}%"
    )
    ax.text(
        0.02, 0.98, annotation, transform=ax.transAxes, fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
    )
    ax.set_title(
        f"Serie de Tiempo de Caudales - {DISPLAY_NAMES[station]}",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Fecha", fontsize=11)
    ax.set_ylabel("Caudal (m3/s)", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(plt.MaxNLocator(12))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def plot_fig4_excedidos(st_orig, station, output_path):
    """Curvas de frecuencia excedidos con percentiles diarios (solo originales)."""
    s = st_orig.sort_values("Fecha")
    if len(s) < 365:
        return False
    s = s.copy()
    s["mes_dia"] = s["Fecha"].dt.strftime("%m-%d")

    fecha_base = pd.date_range("2020-01-01", "2020-12-31", freq="D")
    fecha_base = fecha_base[fecha_base.strftime("%m-%d") != "02-29"]

    rows = []
    for f in fecha_base:
        md = f.strftime("%m-%d")
        vals = s.loc[s["mes_dia"] == md, "Caudal"].values
        if len(vals) > 0:
            rows.append({
                "doy": f.dayofyear,
                "max": np.max(vals),
                "p95": np.percentile(vals, 95),
                "p75": np.percentile(vals, 75),
                "p50": np.percentile(vals, 50),
                "p25": np.percentile(vals, 25),
                "p5": np.percentile(vals, 5),
                "min": np.min(vals),
            })
    pdf = pd.DataFrame(rows)
    if len(pdf) < 300:
        return False

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = {
        "max": "black", "p95": "#8B0000", "p75": "#6B8E23",
        "p50": "black", "p25": "#5DADE2", "p5": "#D35400", "min": "black",
    }
    linewidths = {
        "max": 1.2, "p95": 1.2, "p75": 1.2, "p50": 2.5,
        "p25": 1.2, "p5": 1.2, "min": 1.2,
    }
    for col in ["max", "p95", "p75", "p50", "p25", "p5", "min"]:
        ax.plot(pdf["doy"], pdf[col], color=colors[col], linewidth=linewidths[col])

    last = pdf.iloc[-1]
    labels_data = [
        ("max", last["max"], "MAX"), ("p95", last["p95"], "5%"),
        ("p75", last["p75"], "25%"), ("p50", last["p50"], "50%"),
        ("p25", last["p25"], "75%"), ("p5", last["p5"], "95%"),
        ("min", last["min"], "MIN"),
    ]
    x_label = pdf["doy"].max() + 3
    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight="bold",
                color=colors[col], va="center", ha="left")

    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(MESES, fontsize=11)
    ax.set_xlabel("Mes", fontsize=12, fontweight="bold")
    ax.set_ylabel("Caudal (m3/s)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Curvas de Frecuencia de Caudales Excedidos - {DISPLAY_NAMES[station]}",
        fontsize=14, fontweight="bold", pad=15,
    )
    ax.grid(True, alpha=0.3, which="both")
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which="minor", linestyle=":", linewidth=0.5)

    plt.tight_layout()
    plt.subplots_adjust(right=0.88)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def _anderson_a2(data, cdf_func):
    x = np.sort(data)
    n = len(x)
    F = np.clip(cdf_func(x), 1e-12, 1 - 1e-12)
    i = np.arange(1, n + 1)
    return -n - np.sum((2 * i - 1) * (np.log(F) + np.log(1 - F[::-1]))) / n


def _fit_extremos(vals, es_maximos):
    """Ajusta Gumbel, Log-Pearson III y GEV. Retorna dict con mejor ajuste."""
    candidatos = {}

    try:
        if es_maximos:
            loc, scale = stats.gumbel_r.fit(vals)
            cdf = lambda q, loc=loc, scale=scale: stats.gumbel_r.cdf(q, loc, scale)
            ppf = lambda p, loc=loc, scale=scale: stats.gumbel_r.ppf(p, loc, scale)
        else:
            loc, scale = stats.gumbel_l.fit(vals)
            cdf = lambda q, loc=loc, scale=scale: stats.gumbel_l.cdf(q, loc, scale)
            ppf = lambda p, loc=loc, scale=scale: stats.gumbel_l.ppf(p, loc, scale)
        candidatos["Gumbel"] = {"cdf": cdf, "ppf": ppf,
                                "A2": _anderson_a2(vals, cdf)}
    except Exception:
        pass

    try:
        logv = np.log10(vals)
        shape, loc, scale = stats.pearson3.fit(logv)
        cdf = lambda q, shape=shape, loc=loc, scale=scale: stats.pearson3.cdf(
            np.log10(q), shape, loc, scale)
        ppf = lambda p, shape=shape, loc=loc, scale=scale: 10 ** stats.pearson3.ppf(
            p, shape, loc, scale)
        candidatos["Log-Pearson III"] = {"cdf": cdf, "ppf": ppf,
                                         "A2": _anderson_a2(vals, cdf)}
    except Exception:
        pass

    try:
        c, loc, scale = stats.genextreme.fit(vals)
        cdf = lambda q, c=c, loc=loc, scale=scale: stats.genextreme.cdf(q, c, loc, scale)
        ppf = lambda p, c=c, loc=loc, scale=scale: stats.genextreme.ppf(p, c, loc, scale)
        candidatos["GEV"] = {"cdf": cdf, "ppf": ppf,
                             "A2": _anderson_a2(vals, cdf)}
    except Exception:
        pass

    if not candidatos:
        return None, candidatos
    mejor = min(candidatos, key=lambda k: candidatos[k]["A2"])
    return mejor, candidatos


def plot_fig5_extremos(st_orig, station, tipo, output_path):
    """Ajuste de extremos anuales (solo datos originales)."""
    s = st_orig.sort_values("Fecha").copy()
    if len(s) < 365 * 10:
        return False
    s["year"] = s["Fecha"].dt.year
    es_maximos = tipo == "maximos"
    anual = s.groupby("year")["Caudal"].max() if es_maximos else s.groupby("year")["Caudal"].min()
    vals = anual.values
    if len(vals) < 15:
        return False

    mejor, candidatos = _fit_extremos(vals, es_maximos)
    if mejor is None:
        return False
    best = candidatos[mejor]

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(vals, bins="fd", density=True, alpha=0.6,
             color="steelblue", edgecolor="gray")
    xs = np.linspace(vals.min(), vals.max(), 200)
    pdf_vals = np.gradient(best["cdf"](xs), xs)
    ax1.plot(xs, pdf_vals, "r-", linewidth=2, label=f"{mejor} (mejor ajuste)")
    ax1.set_title(f"Histograma y PDF ajustada - {tipo.upper()}",
                  fontsize=12, fontweight="bold")
    ax1.set_xlabel("Caudal (m3/s)")
    ax1.set_ylabel("Densidad")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    n = len(vals)
    probs = (np.arange(1, n + 1)) / (n + 1)
    teoricos = best["ppf"](probs)
    observados = np.sort(vals)
    ax2.scatter(teoricos, observados, facecolor="steelblue",
                edgecolor="black", alpha=0.7, s=30)
    lims = [min(teoricos.min(), observados.min()),
            max(teoricos.max(), observados.max())]
    ax2.plot(lims, lims, "r--", linewidth=1.5)
    ax2.set_title(f"Q-Q Plot - {mejor}", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Cuantiles teoricos (m3/s)")
    ax2.set_ylabel("Cuantiles observados (m3/s)")
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(gs[1, :])
    F_emp = np.arange(1, n + 1) / n
    ax3.plot(observados, F_emp, "ko-", markersize=4, linewidth=1.2,
             label="Empirico")
    ax3.plot(xs, best["cdf"](xs), "r-", linewidth=2,
             label=f"{mejor} teorico")

    T_list = [2, 5, 10, 25, 50, 100]
    if es_maximos:
        Q_T = {T: best["ppf"](1 - 1 / T) for T in T_list}
    else:
        Q_T = {T: best["ppf"](1 / T) for T in T_list}

    txt = "Periodo de retorno (anos) | Caudal (m3/s)\n"
    txt += "-" * 42 + "\n"
    for T in T_list:
        txt += f"   T={T:>3d}   |   {Q_T[T]:>10,.2f}\n"
    txt += "\nBondad de ajuste (Anderson-Darling A2):\n"
    for nombre in candidatos:
        txt += f"   {nombre}: {candidatos[nombre]['A2']:.4f}\n"

    ax3.text(
        0.98, 0.03, txt, transform=ax3.transAxes, fontsize=9,
        verticalalignment="bottom", horizontalalignment="right",
        family="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
    )
    ax3.set_title(
        f"Funcion de Distribucion Acumulada - {tipo.upper()} ({mejor})",
        fontsize=12, fontweight="bold",
    )
    ax3.set_xlabel("Caudal (m3/s)")
    ax3.set_ylabel("Probabilidad de no excedencia F(x)")
    ax3.legend(loc="upper left", fontsize=9)
    ax3.grid(True, alpha=0.3)

    fig.suptitle(
        f"Ajuste de Distribucion de Extremos - {DISPLAY_NAMES[station]} ({tipo.upper()})\n"
        f"Mejor ajuste: {mejor}",
        fontsize=14, fontweight="bold",
    )
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def main():
    print("=" * 70)
    print("CARTILLAS CAUDALES - Fig1, Fig4, Fig5 (serie imputada, formato v2.1)")
    print("=" * 70)

    print(f"\nCargando serie imputada: {IMPUTED_FILE.name}")
    df = load_imputados()
    print(f"Registros: {len(df):,}")

    for st in GEO_ORDER:
        st_dir = CARTILLAS_DIR / st
        st_dir.mkdir(parents=True, exist_ok=True)
        nombre = DISPLAY_NAMES[st]

        st_all = df[df["NombreEstacion"] == st]
        st_orig = st_all[
            (st_all["Nivel_Imputacion"] == 0) & st_all["Caudal"].notna()
        ][["Fecha", "Caudal"]]

        ok1 = plot_fig1_serie(st_all, st, st_dir / f"Fig1_Serie_Tiempo_{st}.png")
        ok4 = plot_fig4_excedidos(st_orig, st, st_dir / f"Fig4_Curvas_Excedidos_{st}_v2.png")
        ok5a = plot_fig5_extremos(st_orig, st, "maximos",
                                  st_dir / f"Fig5_Ajuste_Extremos_maximos_{st}.png")
        ok5b = plot_fig5_extremos(st_orig, st, "minimos",
                                  st_dir / f"Fig5_Ajuste_Extremos_minimos_{st}.png")
        print(f"  {nombre:15s} Fig1={'OK' if ok1 else 'NO'} "
              f"Fig4={'OK' if ok4 else 'NO'} "
              f"Fig5max={'OK' if ok5a else 'NO'} Fig5min={'OK' if ok5b else 'NO'}")

    print(f"\nDirectorio: {CARTILLAS_DIR}")


if __name__ == "__main__":
    main()
