"""
app.py — Flask webserver met CSV-uploadformulier.

Gebruik:
    python app.py
    Open http://127.0.0.1:5000 in je browser.
"""

import os
import csv
from collections import defaultdict

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from data_analyse import detecteer_type, maak_grafiek

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_MAP = "uploads"
RAPPORT_PAD = os.path.join("static", "rapport.png")
os.makedirs(UPLOAD_MAP, exist_ok=True)
os.makedirs("static", exist_ok=True)


def _csv_extensie(bestandsnaam):
    return "." in bestandsnaam and bestandsnaam.rsplit(".", 1)[1].lower() == "csv"


def _analyseer(bestandspad):
    with open(bestandspad, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        kolommen = list(reader.fieldnames or [])
        if not kolommen:
            return None
        kolomdata = defaultdict(list)
        aantal_rijen = 0
        for rij in reader:
            aantal_rijen += 1
            for kolom in kolommen:
                kolomdata[kolom].append(rij.get(kolom, ""))

    rijen = []
    lege_aantallen = []
    for kolom in kolommen:
        waarden = kolomdata[kolom]
        datatype = detecteer_type(waarden)
        aantal_leeg = sum(1 for w in waarden if w.strip() == "")
        lege_aantallen.append(aantal_leeg)
        pct = 100 * aantal_leeg // aantal_rijen if aantal_rijen else 0
        rijen.append({
            "kolom": kolom,
            "datatype": datatype,
            "aantal_leeg": aantal_leeg,
            "pct_leeg": pct,
        })

    maak_grafiek(kolommen, lege_aantallen, aantal_rijen, uitvoerpad=RAPPORT_PAD)

    return {
        "bestandsnaam": os.path.basename(bestandspad),
        "aantal_rijen": aantal_rijen,
        "aantal_kolommen": len(kolommen),
        "rijen": rijen,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    bestand = request.files.get("bestand")

    if not bestand or bestand.filename == "":
        return render_template("index.html", fout="Geen bestand geselecteerd.")

    if not _csv_extensie(bestand.filename):
        return render_template("index.html", fout="Alleen .csv bestanden zijn toegestaan.")

    bestandsnaam = secure_filename(bestand.filename)
    pad = os.path.join(UPLOAD_MAP, bestandsnaam)
    bestand.save(pad)

    resultaat = _analyseer(pad)
    if resultaat is None:
        return render_template("index.html", fout="Het CSV-bestand heeft geen kolomkoppen.")

    session["resultaat"] = resultaat
    return redirect(url_for("resultaat"))


@app.route("/resultaat")
def resultaat():
    data = session.get("resultaat")
    if not data:
        return redirect(url_for("index"))
    return render_template("resultaat.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
