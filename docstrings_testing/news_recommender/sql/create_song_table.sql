DROP TABLE IF EXISTS articles;
CREATE TABLE articles (
    name TEXT NOT NULL,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    publishedAt TEXT NOT NULL,
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(author, title, url)
);