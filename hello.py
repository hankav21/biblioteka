import datetime
from typing import List

from flask import Flask, redirect, url_for, render_template
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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/lista_ksiazek")
def lista_ksiazek():
    ksiazki=[["tytul","autor","stan"], ["tytul2","autor2","stan2"]]
    ksiazka = Ksiazka.query.get(1)
    return render_template("lista_ksiazek.html", ksiazki=ksiazki, k=ksiazka.wypozyczenia)

@app.route("/lista_ksiazek/<ksiazka>")
def widok_ksiazki(ksiazka):
    return render_template("ksiazka.html", ksiazka=ksiazka)

@app.route("/<czytelnik>")
def czytelnik(czytelnik):
    return render_template("czytelnik.html",czytelnik=czytelnik)

@app.route("/<czytelnik>/wypozyczenia")
def czytelnik_wypozyczenia(czytelnik):
    ksiazki_zarezerwowane=[["tytul","autor","data zamowienia"], ["tytul2","autor2"," xx-xx-xxxx"]]
    ksiazki_wypozyczone=[["tytul","autor","data do zwrotu"], ["tytul2","autor2","xx-xx-xxxx"]]
    return render_template("czytelnik_wypozyczenia.html", czytelnik=czytelnik, zarezerwowane=ksiazki_zarezerwowane, wypozyczone=ksiazki_wypozyczone)

@app.route("/<czytelnik>/historia")
def czytelnik_historia(czytelnik):
    ksiazki=[["tytul","autor","data zwrotu"], ["tytul2","autor2","xx-xx-xxxx"]]
    return render_template("czytelnik_historia.html", czytelnik=czytelnik, ksiazki=ksiazki)

@app.route("/bibliotekarz")
def bibliotekarz():
    return render_template("bibliotekarz.html")

@app.route("/bibliotekarz/dodaj_ksiazke")
def dodaj_ksiazke():
    return render_template("dodaj_ksiazke.html")

@app.route("/bibliotekarz/dodaj_uzytkownika")
def dodaj_uzytkownika():
    return render_template("dodaj_uzytkownika.html")

@app.route("/bibliotekarz/wypozycz")
def wypozycz():
    ksiazka = "ksiazka x"
    czytelnik = "czytelnik y"
    return render_template("wypozycz.html", ksiazka=ksiazka, czytelnik=czytelnik)
