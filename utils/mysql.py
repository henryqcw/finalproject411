import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "academicworld"),
}


def get_conn():
    return mysql.connector.connect(**_CONFIG)


def w01_search_publications(keyword, limit=20):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.title, p.year, p.num_citations, p.venue,
               GROUP_CONCAT(DISTINCT f.name SEPARATOR ', ') AS authors
        FROM publication p
        JOIN Publication_Keyword pk ON p.ID = pk.publication_id
        JOIN keyword k ON pk.keyword_id = k.id
        LEFT JOIN faculty_publication fp ON p.ID = fp.publication_id
        LEFT JOIN faculty f ON fp.faculty_id = f.id
        WHERE k.name LIKE %s
        GROUP BY p.ID
        ORDER BY p.num_citations DESC
        LIMIT %s
    """, (f"%{keyword}%", limit))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def w02_get_university_profile(university_name):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT COUNT(DISTINCT f.id) AS faculty_count,
               COUNT(DISTINCT fp.publication_id) AS pub_count,
               SUM(p.num_citations) AS total_citations
        FROM university u
        JOIN faculty f ON f.university_id = u.id
        JOIN faculty_publication fp ON fp.faculty_id = f.id
        JOIN publication p ON p.ID = fp.publication_id
        WHERE u.name = %s
    """, (university_name,))
    stats = cur.fetchone()
    cur.execute("""
        SELECT k.name AS keyword_name, COUNT(*) AS cnt
        FROM university u
        JOIN faculty f ON f.university_id = u.id
        JOIN faculty_publication fp ON fp.faculty_id = f.id
        JOIN Publication_Keyword pk ON pk.publication_id = fp.publication_id
        JOIN keyword k ON k.id = pk.keyword_id
        WHERE u.name = %s
        GROUP BY k.id ORDER BY cnt DESC LIMIT 10
    """, (university_name,))
    keywords = cur.fetchall()
    cur.close()
    conn.close()
    return stats, keywords


def w02_get_university_list():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM university ORDER BY name")
    result = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return result


def w03_compare_universities(names):
    if not names:
        return []
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(names))
    cur.execute(f"""
        SELECT u.name AS university,
               COUNT(DISTINCT f.id) AS faculty_count,
               COUNT(DISTINCT fp.publication_id) AS pub_count,
               SUM(p.num_citations) AS total_citations,
               COUNT(DISTINCT CASE WHEN p.year >= 2020 THEN p.ID END) AS recent_pubs
        FROM university u
        JOIN faculty f ON f.university_id = u.id
        JOIN faculty_publication fp ON fp.faculty_id = f.id
        JOIN publication p ON p.ID = fp.publication_id
        WHERE u.name IN ({placeholders})
        GROUP BY u.id
        ORDER BY total_citations DESC
    """, names)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def w04_get_faculty_profile(faculty_name):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT f.id, f.name, f.position, f.research_interest, f.photo_url,
               u.name AS university
        FROM faculty f JOIN university u ON f.university_id = u.id
        WHERE f.name = %s LIMIT 1
    """, (faculty_name,))
    profile = cur.fetchone()
    if not profile:
        cur.close()
        conn.close()
        return None
    fid = profile["id"]
    cur.execute("""
        SELECT SUM(p.num_citations) AS total_citations, COUNT(p.ID) AS pub_count
        FROM faculty_publication fp JOIN publication p ON fp.publication_id = p.ID
        WHERE fp.faculty_id = %s
    """, (fid,))
    stats = cur.fetchone()
    cur.execute("""
        SELECT k.name, COUNT(*) AS cnt
        FROM faculty_publication fp
        JOIN Publication_Keyword pk ON fp.publication_id = pk.publication_id
        JOIN keyword k ON pk.keyword_id = k.id
        WHERE fp.faculty_id = %s GROUP BY k.id ORDER BY cnt DESC LIMIT 8
    """, (fid,))
    keywords = cur.fetchall()
    cur.execute("""
        SELECT p.title, p.year, p.num_citations
        FROM faculty_publication fp JOIN publication p ON fp.publication_id = p.ID
        WHERE fp.faculty_id = %s ORDER BY p.num_citations DESC LIMIT 5
    """, (fid,))
    papers = cur.fetchall()
    cur.close()
    conn.close()
    profile.update(stats or {})
    profile["keywords"] = keywords
    profile["papers"] = papers
    return profile


def w04_get_faculty_list():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM faculty ORDER BY name")
    result = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return result


def w05_top_faculty_for_keyword(keyword, limit=10):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.callproc("get_top_faculty_for_keyword", [keyword, limit])
    result = []
    for rs in cur.stored_results():
        result = rs.fetchall()
    cur.close()
    conn.close()
    return result


def w05_publication_trend(keyword):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.year, COUNT(*) AS count
        FROM publication p
        JOIN Publication_Keyword pk ON p.ID = pk.publication_id
        JOIN keyword k ON pk.keyword_id = k.id
        WHERE k.name LIKE %s AND p.year IS NOT NULL AND p.year != ''
        GROUP BY p.year ORDER BY p.year
    """, (f"%{keyword}%",))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def w07_add_favorite(faculty_name):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM faculty WHERE name = %s LIMIT 1", (faculty_name,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False, "Faculty not found."
    fid = row["id"]
    try:
        cur.execute("INSERT INTO favorite_professors (faculty_id) VALUES (%s)", (fid,))
        conn.commit()
        ok, msg = True, f"Added {faculty_name} to favorites."
    except Exception as e:
        conn.rollback()
        ok, msg = False, "Already in favorites." if "Duplicate" in str(e) else str(e)
    cur.close()
    conn.close()
    return ok, msg


def w07_remove_favorite(faculty_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM favorite_professors WHERE faculty_id = %s", (faculty_id,))
    conn.commit()
    cur.close()
    conn.close()


def w07_get_favorites():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT fp.id AS fav_id, f.id AS faculty_id, f.name, u.name AS university
        FROM favorite_professors fp
        JOIN faculty f ON fp.faculty_id = f.id
        JOIN university u ON f.university_id = u.id
        ORDER BY fp.created_at DESC
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
