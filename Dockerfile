# Używamy obrazu bazowego z Pythonem
FROM python:3.9

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy pliki aplikacji do kontenera
COPY . /app

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Ustawiamy zmienną środowiskową
ENV FLASK_APP=app.py

# Komenda uruchamiająca aplikację
CMD ["flask", "run", "--host=0.0.0.0"]
