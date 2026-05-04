# Academic World Explorer

## Title
Academic World Explorer

## Purpose
A dashboard for exploring the Academic World dataset. Target users are students looking to find research directions, compare universities, or discover faculty. The app lets users search publications, view faculty profiles, track research trends, rank institutes by keyword, and save favorites — backed by MySQL, MongoDB, and Neo4j.

## Demo
https://mediaspace.illinois.edu/media/t/1_951riaq6

## Installation

Requires Python 3.9+, MySQL 8.0, MongoDB, and Neo4j running locally with the Academic World dataset already loaded.

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your database credentials:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=academicworld

MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=academicworld

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=academicworld
```

Run the app:
```bash
python app.py
```

Open http://127.0.0.1:8050. Database setup (indexes, view, triggers, stored procedure) runs automatically on startup.

## Usage

| Widget | Description |
|--------|-------------|
| Keyword Publication Search | Search publications by keyword, ranked by citations (MySQL) |
| University Research Profile | Faculty, publication, and citation summary for a university (MySQL) |
| University Comparison | Compare multiple universities side by side (MySQL View) |
| Faculty Profile | Stats, keywords, and top papers for a faculty member (MySQL) |
| Research Trends | Publication trend over time + top faculty by citations (MySQL + MongoDB) |
| Institute & Keyword Ranking | Top institutes and related keywords by graph traversal (Neo4j) |
| Favorite Professors | Add/remove favorite faculty with trigger logging (MySQL) |
| Favorite Publications | Save and manage favorite papers (MongoDB) |

## Design

```
app.py              entry point, runs DB setup on startup
components/         one file per widget + layout.py
utils/
    mysql.py        MySQL queries and updates
    mongodb.py      MongoDB queries and updates
    neo4j.py        Neo4j Cypher queries
    common.py       shared helpers
    setup.py        DB initialization
assets/style.css    stylesheet
setup/              reference SQL/JS/Cypher scripts
```

## Implementation
- Dash + Dash Bootstrap Components (DARKLY theme)
- Plotly Express for charts
- Pandas for data manipulation
- mysql-connector-python, pymongo, neo4j as drivers
- python-dotenv for credentials

## Database Techniques

| Technique | Details |
|-----------|---------|
| Indexing | MySQL: keyword.name, publication.year, faculty.name; MongoDB: keywords.name, year; Neo4j: FACULTY.name, PUBLICATION.id |
| View | `university_keyword_stats` in MySQL — used in Widget 3 |
| Stored Procedure | `get_top_faculty_for_keyword` in MySQL — used in Widget 5 |
| Trigger | `trg_fav_add` / `trg_fav_remove` on `favorite_professors` — used in Widget 7 |
| Constraint | UNIQUE + FOREIGN KEY on `favorite_professors` — used in Widget 7 |

## Contributions

| Member | Tasks | Time |
|--------|-------|------|
| Henry (Qice) Wang | All widgets, DB setup, styling, README | ~20 hours |
