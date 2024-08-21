from flask import Flask, redirect, url_for
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return f"<h1>LOGIN</h1>"

@app.route("/lista_ksiazek")
def lista_ksiazek():
    return f"<h1>lista ksiazek</h1>"

@app.route("/lista_ksiazek/<ksiazka>")
def widok_ksiazki(ksiazka):
    return f"<h1>{ksiazka}</h1>"