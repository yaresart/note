Tento projekt je jednoduchá webová aplikace pro správu poznámek s možností přihlášení uživatele a přidávání obrázků k poznámkám.

--Požadavky

 Python 3.10 nebo vyšší
 Flask
 SQLite3
 pip

--Instalace

1. Naklonujte repozitář
2. Vytvořte a aktivujte virtuální prostředí:
"python -m venv venv"
pro windows "venv\Scripts\activate"
pro linux nebo macOs "source venv/bin/activate"
3. Nainstalujte požadované balíčky:
pip install -r requirements.txt

--Inicializace databáze

1. Spusťte Python skript pro vytvoření databáze a tabulek:
python init_db.py
python init_notes.py

--Spuštění aplikace

Aplikaci můžete spustit na libovolném portu podle potřeby. 
Například: python app.py 1111 nebo prostě app.py (na port 5000)
