import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = None


def get_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")),
            database=os.getenv("NEO4J_DATABASE", "academicworld")
        )
    return driver


def run_query(query, **params):
    with get_driver().session() as session:
        return [dict(r) for r in session.run(query, **params)]


def w05_top_faculty_citations(keyword, limit=10):
    return run_query("""
        MATCH (f:FACULTY)-[:INTERESTED_IN]->(k:KEYWORD)<-[:LABEL_BY]-(p:PUBLICATION)<-[:PUBLISH]-(f)
        WHERE toLower(k.name) CONTAINS toLower($keyword)
        RETURN f.name AS faculty, SUM(p.numCitations) AS total_citations,
               COUNT(p) AS pub_count
        ORDER BY total_citations DESC LIMIT $limit
    """, keyword=keyword, limit=limit)


def w06_institute_ranking(keyword, limit=10):
    return run_query("""
        MATCH (f:FACULTY)-[:AFFILIATION_WITH]->(i:INSTITUTE),
              (f)-[:INTERESTED_IN]->(k:KEYWORD)
        WHERE toLower(k.name) CONTAINS toLower($keyword)
        RETURN i.name AS institute, COUNT(DISTINCT f) AS faculty_count,
               SUM(k.score) AS total_score
        ORDER BY faculty_count DESC LIMIT $limit
    """, keyword=keyword, limit=limit)


def w06_related_keywords(keyword, limit=10):
    return run_query("""
        MATCH (f:FACULTY)-[:INTERESTED_IN]->(k1:KEYWORD)
        WHERE toLower(k1.name) CONTAINS toLower($keyword)
        MATCH (f)-[:INTERESTED_IN]->(k2:KEYWORD)
        WHERE k2 <> k1
        RETURN k2.name AS related_keyword, COUNT(DISTINCT f) AS faculty_count
        ORDER BY faculty_count DESC LIMIT $limit
    """, keyword=keyword, limit=limit)


def w07_collaboration_network(faculty_name):
    return run_query("""
        MATCH (f1:FACULTY)-[:PUBLISH]->(p:PUBLICATION)<-[:PUBLISH]-(f2:FACULTY)
        WHERE f1.name = $name AND f1 <> f2
        RETURN f2.name AS collaborator, COUNT(p) AS shared_pubs
        ORDER BY shared_pubs DESC LIMIT 20
    """, name=faculty_name)
