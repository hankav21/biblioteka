from flask import Flask, redirect, url_for, render_template
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/lista_ksiazek")
def lista_ksiazek():
    return render_template("lista_ksiazek.html")

@app.route("/lista_ksiazek/<ksiazka>")
def widok_ksiazki(ksiazka):
    return render_template("ksiazka.html", ksiazka=ksiazka)