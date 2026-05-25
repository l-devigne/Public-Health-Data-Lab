import os
import requests
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODÈLE ---
class CountryCovidStats(Base):
    __tablename__ = "country_covid_stats"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False, index=True)
    continent = Column(String(50), nullable=True)
    total_cases = Column(Integer, nullable=False)
    total_deaths = Column(Integer, nullable=False)
    total_recovered = Column(Integer, nullable=False)
    population = Column(Integer, nullable=False)
    # JSONB : stats détaillées (tests, actifs, critiques...)
    details = Column(JSONB, nullable=False)

Base.metadata.create_all(bind=engine)

# --- INGESTION ---
def fetch_and_store_covid_data(country_name: str):
    """
    Appelle disease.sh — API publique, sans clé, 100% stable.
    Ex: https://disease.sh/v3/covid-19/countries/France
    """
    print(f"📥 Récupération des données pour : {country_name}...")

    url = f"https://disease.sh/v3/covid-19/countries/{country_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        details = {
            "active":           data.get("active", 0),
            "critical":         data.get("critical", 0),
            "cases_per_million": data.get("casesPerOneMillion", 0),
            "deaths_per_million": data.get("deathsPerOneMillion", 0),
            "tests":            data.get("tests", 0),
            "tests_per_million": data.get("testsPerOneMillion", 0),
            "today_cases":      data.get("todayCases", 0),
            "today_deaths":     data.get("todayDeaths", 0),
        }

        session = SessionLocal()
        record = CountryCovidStats(
            country=data.get("country"),
            continent=data.get("continent"),
            total_cases=data.get("cases", 0),
            total_deaths=data.get("deaths", 0),
            total_recovered=data.get("recovered", 0),
            population=data.get("population", 0),
            details=details
        )
        session.add(record)
        session.commit()
        session.close()
        print(f"✅ {country_name} enregistré — {data.get('cases', 0):,} cas au total.")

    except Exception as e:
        print(f"❌ Erreur pour {country_name} : {e}")

# --- ANALYSE JSONB ---
def analyze_mortality_rate():
    """
    Requête analytique : taux de mortalité et données critiques via JSONB.
    """
    session = SessionLocal()
    try:
        query = text("""
            SELECT
                country,
                continent,
                total_cases,
                total_deaths,
                ROUND(total_deaths::NUMERIC / NULLIF(total_cases, 0) * 100, 2) AS mortality_rate_pct,
                CAST(details->>'critical' AS INTEGER) AS critical_patients,
                CAST(details->>'tests' AS BIGINT) AS total_tests
            FROM country_covid_stats
            ORDER BY mortality_rate_pct DESC;
        """)
        result = session.execute(query)
        print("\n📊 --- ANALYSE COVID : TAUX DE MORTALITÉ PAR PAYS ---")
        for row in result:
            print(
                f"🌍 {row[0]:20s} | {row[1]:15s} | "
                f"Cas: {row[2]:>12,} | Décès: {row[3]:>8,} | "
                f"Mortalité: {row[4]}% | Critiques: {row[5]:>6,}"
            )
    except Exception as e:
        print(f"❌ Erreur analyse : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("Démarrage du système d'analyse COVID...\n")

    countries = ["France", "Germany", "Italy", "USA", "Japan", "Brazil", "India"]
    for country in countries:
        fetch_and_store_covid_data(country)

    analyze_mortality_rate()