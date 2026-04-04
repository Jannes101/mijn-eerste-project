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

    for kolom in kolommen:
        waarden = kolomdata[kolom]
        datatype = detecteer_type(waarden)
        aantal_leeg = sum(1 for w in waarden if w.strip() == "")
        leeg_label = f"{aantal_leeg} ({100 * aantal_leeg // aantal_rijen}%)" if aantal_rijen else "0"
        print(
            f"  {kolom:<{max_kolom}}  {datatype:<{breedte_type}}  {leeg_label:>{breedte_leeg}}"
        )

    print(scheidslijn)
    print()


if __name__ == "__main__":
    bestand = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
    analyseer_csv(bestand)
