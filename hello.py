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

@app.route("/<czytelnik>/lista_ksiazek/<ksiazka>", methods=['POST','GET'])
def widok_ksiazki(czytelnik, ksiazka):
    if request.method == 'POST':
        id_ksiazki = request.form.get("ksiazka_id")
        uzytkownik_id = Uzytkownik.query.filter_by(login=czytelnik).first().id
        
        print(id_ksiazki)
        print(uzytkownik_id)
        
        nowe_wypozyczenie = Wypozyczenie(id=Wypozyczenie.query.count()+1, uzytkownik_id=uzytkownik_id, ksiazka_id=id_ksiazki, status="Z", data_wypozyczenia=datetime.date.today(), data_zwrotu=datetime.date.today()+datetime.timedelta(days=3))
        
        print(nowe_wypozyczenie)
        
        db.session.add(nowe_wypozyczenie)
        db.session.commit()

    ksiazka = Ksiazka.query.filter_by(id=ksiazka).first()
    
    print("size:" ,len(ksiazka.wypozyczenia))
    return render_template("ksiazka.html", ksiazka=ksiazka, czytelnik=czytelnik)

@app.route("/<czytelnik>")
def czytelnik(czytelnik):
    return render_template("czytelnik.html", czytelnik=czytelnik)

@app.route("/<czytelnik>/wypozyczenia", methods=["POST", 'GET'])
def czytelnik_wypozyczenia(czytelnik):
    
    if request.method == 'POST':
        rezerwacja_id = request.form.get("rezerwacja_id")    
        #print(f"Rezerwacja o ID {rezerwacja_id} została anulowana.")
        #print(request.form.get("rezerwacja_id"))
        anulowane_wpozyczenie = Wypozyczenie.query.get(rezerwacja_id)
        anulowane_wpozyczenie.status = 'A'
        db.session.commit()
        
    
    
    zalogowany_czytelnik = Uzytkownik.query.filter_by(login=czytelnik).first()
    #print(zalogowany_czytelnik.wypozyczenia[0])
    #print(Uzytkownik.query.filter_by(login=czytelnik).first())
    '''for instance in Uzytkownik.query.filter_by(login=czytelnik).all():
        print(instance.login, instance.haslo, instance.ksiazki)
        for b in instance.ksiazki:
            print(b.autor)
    print(Uzytkownik.query.filter_by(login=czytelnik).first().ksiazki[0].autor)'''
    
   
    #ksiazki_zarezerwowane = [wypozyczenie.ksiazka for wypozyczenie in zalogowany_czytelnik.wypozyczenia if wypozyczenie.status == "Z"]
    #ksiazki_wypozyczone= [wypozyczenie.ksiazka for wypozyczenie in zalogowany_czytelnik.wypozyczenia if wypozyczenie.status == "W"]
    
    rezerwacje = Wypozyczenie.query.filter_by(uzytkownik_id=zalogowany_czytelnik.id, status="Z").all()
    wypozyczenia = Wypozyczenie.query.filter_by(uzytkownik_id=zalogowany_czytelnik.id, status="W").all()
    
    return render_template("czytelnik_wypozyczenia.html", czytelnik=czytelnik, rezerwacje=rezerwacje, wypozyczenia=wypozyczenia)

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

@app.route("/bibliotekarz/wyszukaj_czytelnika", methods=['POST','GET'])
def wyszukaj_czytelnika():
    
    if request.method == 'POST':
        akcja = request.form.get('przycisk') 
        if akcja == 'czytelnik':
            login_czytelnika = request.form.get('czytelnik') 
            czytelnik = Uzytkownik.query.filter_by(login=login_czytelnika).first()
            czytelnik_wypozyczenia = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="Z").all()
            czytelnik_zwroty = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="W").all()
           
            return redirect(url_for('obsluz', login_czytelnika=login_czytelnika))


    return render_template("wyszukaj_czytelnika.html")

@app.route("/bibliotekarz/wyszukaj_czytelnika/<login_czytelnika>/obsluz", methods=['POST','GET'])
def obsluz(login_czytelnika):
   
    czytelnik = Uzytkownik.query.filter_by(login=login_czytelnika).first()
    czytelnik_wypozyczenia = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="Z").all()
    czytelnik_zwroty = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="W").all()
    
    if request.method == 'POST':
     
        id_wypozyczenia = request.form.get('wypozyczenie_id')
        print("id: ", id_wypozyczenia)
        obslugiwane_wypozyczenie = Wypozyczenie.query.filter_by(id=id_wypozyczenia).first()
        print(czytelnik_wypozyczenia)
        print("ow: ", obslugiwane_wypozyczenie)
        if(obslugiwane_wypozyczenie.status == "W"):
            obslugiwane_wypozyczenie.status = "H"
        elif(obslugiwane_wypozyczenie.status == "Z"):
            obslugiwane_wypozyczenie.status = "W"
        czytelnik_wypozyczenia = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="Z").all()
        czytelnik_zwroty = Wypozyczenie.query.filter_by(uzytkownik_id=czytelnik.id, status="W").all()
          
        db.session.commit()      
    
    return render_template("obsluz.html", login_czytelnika=login_czytelnika, zwroty=czytelnik_zwroty, wypozyczenia=czytelnik_wypozyczenia)
       
       
@app.route("/bibliotekarz/ksiazki_biblioteki")
def ksiazki_biblioteki():
    ksiegozbior = Ksiazka.query.all()
    return render_template("ksiazki_biblioteki.html", ksiazki=ksiegozbior)

@app.route("/bibliotekarz/ksiazki_biblioteki/<autor>/<tytul>/<ksiazka_id>")
def historia_ksiazki(autor, tytul, ksiazka_id):
    print(autor)
    print(tytul)
    print(ksiazka_id)
    wypozyczenia = Wypozyczenie.query.filter_by(ksiazka_id=ksiazka_id).all()
    print(wypozyczenia)

    return render_template("ksiazka_historia.html", wypozyczenia=wypozyczenia, autor=autor, tytul=tytul)
