import datetime
from typing import List

from flask import Flask, redirect, url_for, render_template
from markupsafe import escape

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey

# SQLAlchemy 

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Uzytkownik(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    haslo: Mapped[str] = mapped_column(String(64), nullable=False)
    ksiazki: Mapped[List["Ksiazka"]] = relationship("Wypozyczenie", back_populates="uzytkownik")
    
class Ksiazka(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    tytul: Mapped[str] = mapped_column(String(128), nullable=False)
    autor: Mapped[str] = mapped_column(String(128), nullable=False)
    uzytkownicy: Mapped[List["Uzytkownik"]] = relationship("Wypozyczenie", back_populates="ksiazka")
    
class Wypozyczenie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    ksiazka_id: Mapped[int] = mapped_column(ForeignKey("ksiazka.id"))
    uzytkownik_id: Mapped[int] = mapped_column(ForeignKey("uzytkownik.id"))
    status: Mapped[str] = mapped_column(nullable=False)
    data_wypozyczenia: Mapped[datetime.date] = mapped_column(nullable=False)
    data_zwrotu: Mapped[datetime.date] = mapped_column(nullable=False)
    ksiazka: Mapped["Ksiazka"] = relationship(back_populates="uzytkownicy")
    uzytkownik: Mapped["Uzytkownik"] = relationship(back_populates="ksiazki")
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
    #uzytkownik = Uzytkownik(id=1, login="admin", haslo="admin")
    #db.session.add(uzytkownik)
    #db.session.commit()
    return render_template("login.html")

@app.route("/lista_ksiazek")
def lista_ksiazek():
    ksiazki=[["tytul","autor","stan"], ["tytul2","autor2","stan2"]]
    ksiazka = db.get_or_404(Ksiazka, 1)
    print(ksiazka.uzytkownicy[0].data_wypozyczenia)
    return render_template("lista_ksiazek.html", ksiazki=ksiazki, k=ksiazka)

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
