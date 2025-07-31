import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    """
        Charge la liste des clubs depuis le fichier JSON 'clubs.json'.
        Retourne une liste de dictionnaires représentant chaque club.
    """
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    """
        Charge la liste des compétitions depuis le fichier JSON 'competitions.json'.
        Retourne une liste de dictionnaires représentant chaque compétition.
    """
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    """
       Route principale qui affiche la page d'accueil (formulaire de connexion via email).
    """
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    """
        Traite le formulaire POST pour récupérer l'email du club.
        Vérifie si le club existe, sinon affiche un message d'erreur.
        Affiche la page de bienvenue avec les informations du club et la liste des compétitions.
    """
    email = request.form['email']
    matching_clubs = [club for club in clubs if club['email'] == email]

    if len(matching_clubs) == 0:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    club = matching_clubs[0]
    return render_template('welcome.html', club=club, competitions=competitions)



@app.route('/book/<competition>/<club>')
def book(competition,club):
    """
       Route pour afficher la page de réservation pour un club et une compétition donnés.
       Vérifie que le club et la compétition existent, sinon affiche un message d'erreur.
    """
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    """
        Route pour traiter la réservation des places.
        Vérifie les règles suivantes avant d'accepter la réservation :
        - Pas plus de 12 places par réservation.
        - La compétition n'est pas passée.
        - Le club a assez de points pour réserver les places demandées.
        Met à jour les données en mémoire et affiche un message de succès ou d'erreur.
    """
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    if placesRequired > 12:
        flash("you can not book more than 12 places")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifie que la compétition n'est pas dans le passé
    if datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S") < datetime.now():
        flash("You cannot book place in past competition")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifie que le club a assez de points
    if placesRequired > int(club["points"]):
        flash("you can not book more than available points")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Mise à jour du nombre de places restantes et des points du club
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    flash('Great-booking complete!')
    club["points"] = int(club["points"]) - placesRequired
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/clubsPoints',methods=['GET'])
def display_clubs_points():
    """
        Route pour afficher la page listant les points de tous les clubs.
    """
    return render_template('clubs_points.html', clubs=clubs)

@app.route('/logout')
def logout():
    """
        Route pour se déconnecter (redirige simplement vers la page d'accueil).
    """
    return redirect(url_for('index'))