from utils.mysql import get_conn
from utils.mongodb import publications_col, favorites_col, faculty_col
from utils.neo4j import get_driver


def setup_mysql():
    conn = get_conn()
    cur = conn.cursor()
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_keyword_name ON keyword(name)",
        "CREATE INDEX IF NOT EXISTS idx_publication_year ON publication(year)",
        "CREATE INDEX IF NOT EXISTS idx_faculty_name ON faculty(name)",
        """CREATE OR REPLACE VIEW university_keyword_stats AS
           SELECT u.name AS university_name, k.name AS keyword_name,
                  COUNT(DISTINCT p.ID) AS pub_count, SUM(p.num_citations) AS total_citations
           FROM university u
           JOIN faculty f ON f.university_id = u.id
           JOIN faculty_publication fp ON fp.faculty_id = f.id
           JOIN publication p ON p.ID = fp.publication_id
           JOIN Publication_Keyword pk ON pk.publication_id = p.ID
           JOIN keyword k ON k.id = pk.keyword_id
           GROUP BY u.id, u.name, k.id, k.name""",
        """CREATE TABLE IF NOT EXISTS favorite_professors (
               id INT AUTO_INCREMENT PRIMARY KEY,
               faculty_id INT NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               CONSTRAINT uq_fav_faculty UNIQUE (faculty_id),
               CONSTRAINT fk_fav_faculty FOREIGN KEY (faculty_id)
                   REFERENCES faculty(id) ON DELETE CASCADE)""",
        """CREATE TABLE IF NOT EXISTS favorite_log (
               id INT AUTO_INCREMENT PRIMARY KEY,
               faculty_id INT NOT NULL,
               action ENUM('ADD','REMOVE') NOT NULL,
               ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    ]
    for sql in statements:
        try:
            cur.execute(sql)
        except Exception:
            pass

    for trigger_name, event, value, log_action in [
        ("trg_fav_add",    "INSERT", "NEW", "ADD"),
        ("trg_fav_remove", "DELETE", "OLD", "REMOVE"),
    ]:
        try:
            cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
            cur.execute(f"""
                CREATE TRIGGER {trigger_name}
                AFTER {event} ON favorite_professors FOR EACH ROW
                INSERT INTO favorite_log(faculty_id, action) VALUES ({value}.faculty_id, '{log_action}')
            """)
        except Exception:
            pass

    try:
        cur.execute("DROP PROCEDURE IF EXISTS get_top_faculty_for_keyword")
        cur.execute("""
            CREATE PROCEDURE get_top_faculty_for_keyword(IN kw VARCHAR(255), IN lim INT)
            BEGIN
                SELECT f.name AS faculty_name, u.name AS university,
                       SUM(p.num_citations) AS total_citations, COUNT(p.ID) AS pub_count
                FROM faculty f
                JOIN university u ON f.university_id = u.id
                JOIN faculty_publication fp ON f.id = fp.faculty_id
                JOIN publication p ON fp.publication_id = p.ID
                JOIN Publication_Keyword pk ON p.ID = pk.publication_id
                JOIN keyword k ON pk.keyword_id = k.id
                WHERE k.name LIKE CONCAT('%', kw, '%')
                GROUP BY f.id ORDER BY total_citations DESC LIMIT lim;
            END
        """)
    except Exception:
        pass

    conn.commit()
    cur.close()
    conn.close()


def setup_mongodb():
    indexes = [
        (publications_col, [("keywords.name", 1)], "idx_pub_keywords_name"),
        (publications_col, [("year", 1)],           "idx_pub_year"),
        (publications_col, [("keywords.name", 1), ("year", 1)], "idx_pub_keywords_name_year"),
        (faculty_col,      [("keywords.name", 1)], "idx_faculty_keywords_name"),
    ]
    for col, keys, name in indexes:
        try:
            col.create_index(keys, name=name)
        except Exception:
            pass
    try:
        favorites_col.create_index([("publication_id", 1)],
                                   name="favorite_publication_unique", unique=True)
    except Exception:
        pass


def setup_neo4j():
    statements = [
        "CREATE CONSTRAINT faculty_id_unique IF NOT EXISTS FOR (f:FACULTY) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT keyword_name_unique IF NOT EXISTS FOR (k:KEYWORD) REQUIRE k.name IS UNIQUE",
        "CREATE INDEX faculty_name_idx IF NOT EXISTS FOR (f:FACULTY) ON (f.name)",
        "CREATE INDEX publication_id_idx IF NOT EXISTS FOR (p:PUBLICATION) ON (p.id)",
    ]
    with get_driver().session() as session:
        for s in statements:
            try:
                session.run(s)
            except Exception:
                pass


def run_all_setup():
    setup_mysql()
    setup_mongodb()
    setup_neo4j()
