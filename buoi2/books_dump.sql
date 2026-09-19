BEGIN TRANSACTION;
CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        title TEXT NOT NULL
    );
INSERT INTO "books" VALUES(1,'Nguyen Van A','Python Co Ban');
INSERT INTO "books" VALUES(2,'Nguyen Van B','Flask REST API');
INSERT INTO "books" VALUES(3,'Robert','RESTful Web Services');
INSERT INTO "books" VALUES(4,'Nguyen Van A','Python Co Ban');
INSERT INTO "books" VALUES(5,'Nguyen Van B','Flask REST API');
INSERT INTO "books" VALUES(6,'Robert','RESTful Web Services');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('books',6);
COMMIT;
##1