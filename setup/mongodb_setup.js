db = db.getSiblingDB("academicworld");

db.publications.createIndex({ "keywords.name": 1 }, { name: "idx_pub_keywords_name" });
db.publications.createIndex({ year: 1 }, { name: "idx_pub_year" });
db.publications.createIndex({ "keywords.name": 1, year: 1 }, { name: "idx_pub_keywords_name_year" });
db.faculty.createIndex({ "keywords.name": 1 }, { name: "idx_faculty_keywords_name" });
db.favorite_publications.createIndex({ publication_id: 1 }, { name: "favorite_publication_unique", unique: true });
