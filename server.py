# server.py
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for

def loadClubs():
    with open("clubs.json", "r", encoding="utf-8") as c:
        return json.load(c)["clubs"]

def loadCompetitions():
    with open("competitions.json", "r", encoding="utf-8") as comps:
        return json.load(comps)["competitions"]

app = Flask(__name__)
app.secret_key = "something_secret_for_flash"  # en prod: variable d'env

clubs = loadClubs()
competitions = loadCompetitions()

# suivi cumulatif des réservations par (club, competition)
# clé: (club_name, comp_name) -> int
club_bookings = {}

def find_club_by_name(name):
    return next((c for c in clubs if c["name"] == name), None)

def find_comp_by_name(name):
    return next((c for c in competitions if c["name"] == name), None)

def competition_in_past(competition) -> bool:
    """Retourne True si la compétition est passée (tolérant aux dates mal formées)."""
    try:
        comp_dt = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        return comp_dt < datetime.now()
    except Exception:
        return False

def validate_purchase(club, competition, places_required, current_booked=0):
    """
    Règles:
      - compétition non passée
      - places_required entier > 0
      - places_required <= places restantes de la compétition
      - points du club >= places_required (1 point = 1 place)
      - plafond 12 par club et par compétition (cumulé)
    """
    # 1) compétition non passée
    if competition_in_past(competition):
        return False, "Competition already finished"

    # 2) quantité valide
    try:
        n = int(places_required)
    except (TypeError, ValueError):
        return False, "Invalid quantity"
    if n <= 0:
        return False, "Invalid quantity (>=1)"

    # 3) places restantes
    comp_left = int(competition["numberOfPlaces"])
    if n > comp_left:
        return False, "Pas assez de places disponibles"

    # 4) points du club
    club_pts = int(club["points"])
    if n > club_pts:
        return False, "Pas assez de points"

    # 5) plafond 12 (cumul par club/compétition)
    if current_booked + n > 12:
        return False, "Maximum 12 places par club sur une compétition"

    return True, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/showSummary", methods=["POST"])
def showSummary():
    # éviter toute ambiguïté avec le nom 'email'
    email_input = request.form.get("email", "")
    club = next((c for c in clubs if c["email"] == email_input), None)
    if not club:
        flash("Email inconnu")
        return redirect(url_for("index"))
    return render_template("welcome.html", club=club, competitions=competitions)

@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = find_club_by_name(club)
    foundCompetition = find_comp_by_name(competition)
    if not foundClub or not foundCompetition:
        flash("Club ou compétition introuvable")
        return redirect(url_for("index"))
    return render_template("booking.html", club=foundClub, competition=foundCompetition)

@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    comp_name = request.form.get("competition")
    club_name = request.form.get("club")
    places_str = request.form.get("places", "0")

    competition = find_comp_by_name(comp_name)
    club = find_club_by_name(club_name)

    if not competition or not club:
        flash("Données invalides (club/compétition)")
        return redirect(url_for("index"))

    booked = club_bookings.get((club["name"], competition["name"]), 0)

    ok, msg = validate_purchase(club, competition, places_str, current_booked=booked)
    if not ok:
        flash(msg)
        return render_template("welcome.html", club=club, competitions=competitions)

    n = int(places_str)

    # appliquer la réservation (cohérence points/places)
    new_places = int(competition["numberOfPlaces"]) - n
    new_points = int(club["points"]) - n
    if new_places < 0 or new_points < 0:
        flash("Erreur de calcul des points/places")
        return render_template("welcome.html", club=club, competitions=competitions)

    competition["numberOfPlaces"] = str(new_places)
    club["points"] = str(new_points)
    club_bookings[(club["name"], competition["name"])] = booked + n

    flash("Great-booking complete!")  # texte attendu par les tests
    return render_template("welcome.html", club=club, competitions=competitions)

# affichage public des points (HTML)
@app.route("/points")
def points():
    return render_template("points.html", clubs=clubs)

@app.route("/logout")
def logout():
    return redirect(url_for("index"))
