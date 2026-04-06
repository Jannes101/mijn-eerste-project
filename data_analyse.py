"""
data_analyse.py — Geeft een snel overzicht van een CSV-bestand.

Gebruik:
    python data_analyse.py                        # gebruikt sample_data.csv
    python data_analyse.py mijn_bestand.csv
"""

import csv
import sys
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def detecteer_type(waarden):
    """Bepaal het meest waarschijnlijke datatype op basis van niet-lege waarden."""
    niet_leeg = [w for w in waarden if w.strip() != ""]
    if not niet_leeg:
        return "onbekend (alles leeg)"

    # Probeer integer
    try:
        for w in niet_leeg:
            int(w)
        return "integer"
    except ValueError:
        pass

    # Probeer float (accepteer ook komma als decimaalteken)
    try:
        for w in niet_leeg:
            float(w.replace(",", "."))
        return "float"
    except ValueError:
        pass

    # Simpele datumcheck: bevat minstens twee koppeltekens of slashes
    if all(
        (w.count("-") >= 2 or w.count("/") >= 2) and len(w) >= 8
        for w in niet_leeg
    ):
        return "datum"

    return "tekst"


def maak_grafiek(kolommen, lege_aantallen, aantal_rijen, uitvoerpad="rapport.png"):
    """Sla een staafdiagram op van het aantal lege waarden per kolom."""
    percentages = [
        100 * n // aantal_rijen if aantal_rijen else 0 for n in lege_aantallen
    ]

    fig, ax = plt.subplots(figsize=(max(6, len(kolommen) * 1.2), 5))
    bars = ax.bar(kolommen, percentages, color="steelblue", edgecolor="white")

    ax.set_xlabel("Kolom")
    ax.set_ylabel("Lege waarden (%)")
    ax.set_title("Lege waarden per kolom")
    ax.set_ylim(0, 110)
    ax.tick_params(axis="x", rotation=45)

    for bar, pct, n in zip(bars, percentages, lege_aantallen):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{pct}%\n({n})",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(uitvoerpad, dpi=150)
    plt.close(fig)
    print(f"  Grafiek opgeslagen als '{uitvoerpad}'")


def analyseer_csv(bestandspad):
    if not os.path.isfile(bestandspad):
        print(f"Fout: bestand '{bestandspad}' niet gevonden.")
        sys.exit(1)

    with open(bestandspad, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        kolommen = reader.fieldnames

        if not kolommen:
            print("Fout: het bestand heeft geen kolomkoppen.")
            sys.exit(1)

        # Verzamel alle waarden per kolom
        kolomdata = defaultdict(list)
        aantal_rijen = 0
        for rij in reader:
            aantal_rijen += 1
            for kolom in kolommen:
                kolomdata[kolom].append(rij.get(kolom, ""))

    # Bepaal breedte voor uitlijning
    max_kolom = max(len(k) for k in kolommen)
    breedte_type = 30
    breedte_leeg = 12

    scheidslijn = "-" * (max_kolom + breedte_type + breedte_leeg + 8)

    print()
    print(f"  Bestand  : {bestandspad}")
    print(f"  Rijen    : {aantal_rijen}")
    print(f"  Kolommen : {len(kolommen)}")
    print()
    print(scheidslijn)
    print(
        f"  {'Kolom':<{max_kolom}}  {'Datatype':<{breedte_type}}  {'Lege waarden':>{breedte_leeg}}"
    )
    print(scheidslijn)

    lege_aantallen = []
    for kolom in kolommen:
        waarden = kolomdata[kolom]
        datatype = detecteer_type(waarden)
        aantal_leeg = sum(1 for w in waarden if w.strip() == "")
        lege_aantallen.append(aantal_leeg)
        leeg_label = f"{aantal_leeg} ({100 * aantal_leeg // aantal_rijen}%)" if aantal_rijen else "0"
        print(
            f"  {kolom:<{max_kolom}}  {datatype:<{breedte_type}}  {leeg_label:>{breedte_leeg}}"
        )

    print(scheidslijn)
    print()

    maak_grafiek(kolommen, lege_aantallen, aantal_rijen)


if __name__ == "__main__":
    bestand = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
    analyseer_csv(bestand)
