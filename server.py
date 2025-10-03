import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, session

# ---------- Data loading ----------
def loadClubs():
    with open("clubs.json", "r", encoding="utf-8") as c:
        return json.load(c)["clubs"]

def loadCompetitions():
    with open("competitions.json", "r", encoding="utf-8") as comps:
        return json.load(comps)["competitions"]

app = Flask(__name__)
app.secret_key = "something_secret_for_flash"  # NOTE: en prod, utiliser une variable d'env

# Données en mémoire (réinitialisées dans les tests via conftest)
clubs = loadClubs()
competitions = loadCompetitions()

# suivi cumulatif des réservations par (club, competition)
# clé: (club_name, comp_name) -> int
club_bookings = {}

# ---------- Helpers ----------
def find_club_by_name(name):
    return next((c for c in clubs if c.get("name") == name), None)

def find_club_by_email(email_value):
    if not email_value:
        return None
    return next((c for c in clubs if c.get("email", "").lower() == email_value.lower()), None)

def find_comp_by_name(name):
    return next((c for c in competitions if c.get("name") == name), None)

def competition_in_past(competition) -> bool:
    """True si la compétition est passée. Tolérant aux dates mal formées."""
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
      - places_required <= places restantes
      - points du club >= places_required
      - plafond 12 (cumul par club/compétition)
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

    # 5) plafond 12 cumulé
    if current_booked + n > 12:
        return False, "Maximum 12 places par club sur une compétition"

    return True, None

# ---------- Routes ----------
@app.route("/")
def index():
    # index doit afficher les messages flash ("Email inconnu", etc.)
    return render_template("index.html")

@app.route("/showSummary", methods=["POST"])
def showSummary():
    email_input = (request.form.get("email") or "").strip()
    club = next((c for c in clubs if c.get("email") == email_input), None)
    if not club:
        flash("Adresse mail inconnue")
        flash("Email inconnu")
        return redirect(url_for("index"))
    session["club_email"] = club["email"].lower()
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
    places_str = request.form.get("places", "0")

    # récupérer le club depuis la session (le formulaire peut ne pas l'envoyer)
    club_email = session.get("club_email")
    club = find_club_by_email(club_email)
    competition = find_comp_by_name(comp_name) if comp_name else None

    if not competition or not club:
        # Le test cherche le mot "invalides" dans le message d'erreur
        flash("Données invalides (club/compétition invalides)")
        return redirect(url_for("index"))

    booked = club_bookings.get((club["name"], competition["name"]), 0)
    ok, msg = validate_purchase(club, competition, places_str, current_booked=booked)
    if not ok:
        flash(msg)
        # On reste sur la page du club (welcome), status 200 attendu par les tests
        return render_template("welcome.html", club=club, competitions=competitions)

    n = int(places_str)

    # appliquer la réservation (cohérence points/places)
    new_places = int(competition["numberOfPlaces"]) - n
    new_points = int(club["points"]) - n
    if new_places < 0 or new_points < 0:
        # sauvegarde défensive (ne devrait pas arriver si la validation est OK)
        flash("Erreur de calcul des points/places")
        return render_template("welcome.html", club=club, competitions=competitions)

    competition["numberOfPlaces"] = str(new_places)
    club["points"] = str(new_points)
    club_bookings[(club["name"], competition["name"])] = booked + n

    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)

@app.route("/points")
def points():
    # tableau public (pas de login requis)
    return render_template("points.html", clubs=clubs)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
