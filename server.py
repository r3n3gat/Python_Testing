import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_secret_for_flash"  # en prod: variable d'env

clubs = loadClubs()
competitions = loadCompetitions()

# suivi cumulatif des réservations par (club, competition)
club_bookings = {}  # clé: (club_name, comp_name) -> int

def find_club_by_name(name):
    return next((c for c in clubs if c["name"] == name), None)

def find_comp_by_name(name):
    return next((c for c in competitions if c["name"] == name), None)

def validate_purchase(club, competition, places_required, current_booked=0):
    """
    Règles:
      - places_required entier > 0
      - cumul par club par compétition <= 12
      - places_required <= places restantes de la compétition
      - points du club >= places_required (1 point = 1 place)
    """
    try:
        n = int(places_required)
    except (TypeError, ValueError):
            return False, "Invalid quantity"
    if n <= 0:
        return False, "Invalid quantity (>=1)"

    # disponibilité compétition
    comp_left = int(competition["numberOfPlaces"])
    if n > comp_left:
        return False, "Pas assez de places disponibles"

    # points du club
    club_pts = int(club["points"])
    if n > club_pts:
        return False, "Pas assez de points"

    # plafond 12 par club et par compétition (cumulé)
    if current_booked + n > 12:
        return False, "Maximum 12 places par club sur une compétition"

    return True, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/showSummary", methods=["POST"])
def showSummary():
    email = request.form.get("email", "")
    club = next((c for c in clubs if c["email"] == email), None)
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
        # on reste sur la page de synthèse du club
        return render_template("welcome.html", club=club, competitions=competitions)

    n = int(places_str)

    # appliquer la réservation
    competition["numberOfPlaces"] = str(int(competition["numberOfPlaces"]) - n)
    club["points"] = str(int(club["points"]) - n)
    club_bookings[(club["name"], competition["name"])] = booked + n

    flash("Great-booking complete!")  # garde le texte d'origine pour que les tests passent
    return render_template("welcome.html", club=club, competitions=competitions)

# (Phase 2) affichage public des points — simple, sans login
@app.route("/points")
def points():
    # rendu minimaliste sans template dédié (tu pourras faire un template plus tard)
    rows = [f"<li>{c['name']}: {c['points']} points</li>" for c in clubs]
    return "<h2>Points par club</h2><ul>" + "\n".join(rows) + "</ul>"

@app.route("/logout")
def logout():
    return redirect(url_for("index"))