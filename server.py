import json
from datetime import datetime
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
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    matching_clubs = [club for club in clubs if club['email'] == email]

    if len(matching_clubs) == 0:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    club = matching_clubs[0]
    return render_template('welcome.html', club=club, competitions=competitions)



@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    if placesRequired > 12:
        flash("you can not book more than 12 places")
        return render_template('welcome.html', club=club, competitions=competitions)
    if datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S") < datetime.now():
        flash("You cannot book place in past competition")
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired > int(club["points"]):
        flash("you can not book more than available points")
        return render_template('welcome.html', club=club, competitions=competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    flash('Great-booking complete!')
    club["points"] = int(club["points"]) - placesRequired
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/clubsPoints',methods=['GET'])
def display_clubs_points():
    return render_template('clubs_points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))