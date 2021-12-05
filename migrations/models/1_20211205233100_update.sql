-- upgrade --
CREATE TABLE IF NOT EXISTS "search" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "movie_name" VARCHAR(255) NOT NULL,
    "user_id" INT REFERENCES "user" ("id") ON DELETE SET NULL
);
-- downgrade --
DROP TABLE IF EXISTS "search";
