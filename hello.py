import datetime
from typing import List

from flask import Flask, flash, redirect, request, url_for, render_template
from markupsafe import escape

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy

# SQLAlchemy 

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Uzytkownik(db.Model):
    __tablename__ = "uzytkownicy"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(16), unique=True, nullable=False)
    haslo = db.Column(db.String(64), nullable=False)
    wypozyczenia = db.relationship("Wypozyczenie", back_populates="uzytkownik")
    ksiazki = association_proxy("wypozyczenia", "ksiazka")

class Ksiazka(db.Model):
    __tablename__ = "ksiazki"
    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(128), nullable=False)
    autor = db.Column(db.String(128), nullable=False)
    wypozyczenia = db.relationship("Wypozyczenie", back_populates="ksiazka")
    uzytkownicy = association_proxy("wypozyczenia", "uzytkownik")

class Wypozyczenie(db.Model):
    __tablename__ = "wypozyczenia"
    id = db.Column(db.Integer, primary_key=True)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey("uzytkownicy.id"), nullable=False)
    ksiazka_id = db.Column(db.Integer, db.ForeignKey("ksiazki.id"), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    data_wypozyczenia = db.Column(db.Date, nullable=False)
    data_zwrotu = db.Column(db.Date, nullable=False)

    uzytkownik = db.relationship("Uzytkownik", back_populates="wypozyczenia")
    ksiazka = db.relationship("Ksiazka", back_populates="wypozyczenia")
# FLASK

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///biblioteka.db"
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get("login")
        haslo = request.form.get("haslo")
        
        # Sprawdzenie, czy użytkownik istnieje w bazie danych
        uzytkownik = Uzytkownik.query.filter_by(login=login, haslo=haslo).first()
        
        if uzytkownik:
            return redirect(url_for("czytelnik", czytelnik=login))
        else:
            # Jeśli użytkownik nie istnieje, pokaż błąd
            #flash("Niepoprawny login lub hasło", "danger")
            print("nei ma takeigo uzytkownika")
    
    return render_template("login.html")

@app.route("/<czytelnik>/lista_ksiazek")
def lista_ksiazek(czytelnik):
    ksiazki=Ksiazka.query.all()
    #ksiazka = Ksiazka.query.get(1)
    return render_template("lista_ksiazek.html", ksiazki=ksiazki, czytelnik=czytelnik)

@app.route("/<czytelnik>/lista_ksiazek/<ksiazka>")
def widok_ksiazki(czytelnik, ksiazka):
    ksiazka = Ksiazka.query.filter_by(id=ksiazka).first()
    print(ksiazka.wypozyczenia[-1].status)
    print(ksiazka.wypozyczenia[-1])
    return render_template("ksiazka.html", ksiazka=ksiazka, czytelnik=czytelnik)

@app.route("/<czytelnik>")
def czytelnik(czytelnik):
    return render_template("czytelnik.html", czytelnik=czytelnik)

@app.route("/<czytelnik>/wypozyczenia")
def czytelnik_wypozyczenia(czytelnik):
    zalogowany_czytelnik = Uzytkownik.query.filter_by(login=czytelnik).first()
    #print(zalogowany_czytelnik.wypozyczenia[0])
    #print(Uzytkownik.query.filter_by(login=czytelnik).first())
    '''for instance in Uzytkownik.query.filter_by(login=czytelnik).all():
        print(instance.login, instance.haslo, instance.ksiazki)
        for b in instance.ksiazki:
            print(b.autor)
    print(Uzytkownik.query.filter_by(login=czytelnik).first().ksiazki[0].autor)'''
    
   
    ksiazki_zarezerwowane = [wypozyczenie.ksiazka for wypozyczenie in zalogowany_czytelnik.wypozyczenia if wypozyczenie.status == "Z"]
    ksiazki_wypozyczone= [wypozyczenie.ksiazka for wypozyczenie in zalogowany_czytelnik.wypozyczenia if wypozyczenie.status == "W"]
    
    return render_template("czytelnik_wypozyczenia.html", czytelnik=czytelnik, zarezerwowane=ksiazki_zarezerwowane, wypozyczone=ksiazki_wypozyczone)

@app.route("/<czytelnik>/historia")
def czytelnik_historia(czytelnik):
    zalogowany_czytelnik = Uzytkownik.query.filter_by(login=czytelnik).first()
    ksiazki= [wypozyczenie.ksiazka for wypozyczenie in zalogowany_czytelnik.wypozyczenia if wypozyczenie.status == "H"]
    w = Wypozyczenie.query.filter_by(uzytkownik_id=zalogowany_czytelnik.id, status="H").all()
    
    
    return render_template("czytelnik_historia.html", wypozyczenia=w, czytelnik=czytelnik)

@app.route("/bibliotekarz")
def bibliotekarz():
    return render_template("bibliotekarz.html")

@app.route("/bibliotekarz/dodaj_ksiazke", methods=['POST', 'GET'])
def dodaj_ksiazke():
    if request.method == 'POST':
        autor = request.form.get('autor')
        tytul = request.form.get('tytul')
        
        nowa_ksiazka = Ksiazka(id=Ksiazka.query.count()+1, autor=autor, tytul=tytul)
        db.session.add(nowa_ksiazka)
        db.session.commit()
    return render_template("dodaj_ksiazke.html")

@app.route("/bibliotekarz/dodaj_uzytkownika",  methods=['GET', 'POST'])
def dodaj_uzytkownika():
    if request.method == 'POST': 
        # Retrieve the text from the textarea 
        haslo = request.form.get('haslo') 
        login = request.form.get('login') 
        
        nowy_uzytkownik = Uzytkownik(id=Uzytkownik.query.count()+1 , login=login, haslo=haslo)
        db.session.add(nowy_uzytkownik)
        db.session.commit()
        
    return render_template("dodaj_uzytkownika.html")

@app.route("/bibliotekarz/wypozycz")
def wypozycz():
    ksiazka = "ksiazka x"
    czytelnik = "czytelnik y"
    return render_template("wypozycz.html", ksiazka=ksiazka, czytelnik=czytelnik)
