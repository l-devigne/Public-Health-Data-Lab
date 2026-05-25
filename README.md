# Public-Health-Data-Lab : Global COVID-19 Analytics & Mortality Intelligence

A data engineering laboratory designed to analyze COVID-19 statistics across countries and continents. This project leverages the **disease.sh** public API to ingest real-world pandemic data into an isolated **PostgreSQL** database via **SQLAlchemy 2.0**, demonstrating the power of relational schemas combined with **JSONB** semi-structured data.

## 🌟 Core Concept & Public Health Value
In health-tech, understanding the spread and lethality of infectious diseases is crucial for epidemiological research and public policy. This tool pulls data directly from the **disease.sh Open Disease API** to:
1. Track total cases, deaths, and recoveries across countries and continents.
2. Store volatile data structures (dynamic per-country metrics) without breaking the schema.
3. Query and compute mortality rates and identify countries with critical patient loads via advanced JSONB queries.

---

## 🛠️ Technical Stack & Architecture

- **Language:** Python 3.11+
- **Database:** PostgreSQL 16 (Isolated and containerized via Docker on port `5433`)
- **ORM / Database Client:** SQLAlchemy 2.0 (Modern, type-safe Pythonic ORM) with `psycopg3` as the native PostgreSQL driver.
- **Data Source:** [disease.sh](https://disease.sh) — free, keyless, open-source disease data API.
- **Data Ingestion:** `requests` for robust HTTP interaction with Open Data REST APIs.
- **Security:** `python-dotenv` for local environment variable encapsulation.

---

## 🚀 Quick Start

### 1. Clone the repository and install dependencies
```bash
git clone https://github.com/l-devigne/Public-Health-Data-Lab
cd Public-Health-Data-Lab
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your environment
Create a `.env` file at the root of the project:
```env
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5433
DB_NAME=your_database
```

### 3. Start the PostgreSQL container
```bash
docker-compose up -d
```

### 4. Run the pipeline
```bash
python app.py
```

---

## 📊 Data Model

### Table: `country_covid_stats`

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Primary key |
| `country` | VARCHAR(100) | Country name |
| `continent` | VARCHAR(50) | Continent |
| `total_cases` | INTEGER | Cumulative confirmed cases |
| `total_deaths` | INTEGER | Cumulative deaths |
| `total_recovered` | INTEGER | Cumulative recoveries |
| `population` | INTEGER | Country population |
| `details` | **JSONB** | Semi-structured metrics (see below) |

### JSONB `details` field structure
```json
{
  "active": 12000,
  "critical": 340,
  "cases_per_million": 58210,
  "deaths_per_million": 1242,
  "tests": 271000000,
  "tests_per_million": 4012400,
  "today_cases": 0,
  "today_deaths": 0
}
```

---

## 🔍 Key Analytics Query

Mortality rate ranking with JSONB extraction:
```sql
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
```

---

## 🌐 Data Source

All data is fetched from the **[disease.sh](https://disease.sh) Open Disease Data API**:
- Endpoint: `GET https://disease.sh/v3/covid-19/countries/{country}`
- No API key required
- JSON response, updated automatically from official sources
- 100% free and open-source

---

## 💡 Learning Objectives

This lab is designed to practice:
- **SQLAlchemy 2.0** ORM patterns (declarative models, sessions, `create_all`)
- **JSONB** in PostgreSQL — storing and querying semi-structured data with `->>` operators
- **REST API ingestion** with `requests` and error handling
- **Environment isolation** with `.venv` and `python-dotenv`
- **Docker** for reproducible database environments