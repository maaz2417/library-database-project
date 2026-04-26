CREATE DATABASE IF NOT EXISTS library_db2;
USE library_db2;

CREATE TABLE IF NOT EXISTS books (
    book_id    INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(255) NOT NULL,
    author     VARCHAR(255) NOT NULL,
    category   VARCHAR(100) NOT NULL,
    isbn       VARCHAR(30)  NOT NULL UNIQUE,
    publisher  VARCHAR(255),
    year       INT,
    quantity   INT NOT NULL DEFAULT 0,
    available  INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO books (title, author, category, isbn, publisher, year, quantity, available) VALUES
('Introduction to Algorithms',  'Thomas Cormen',        'Computer Science',     '978-0262033848', 'MIT Press',     2009, 5, 3),
('Clean Code',                  'Robert C. Martin',     'Software Engineering', '978-0132350884', 'Prentice Hall', 2008, 4, 4),
('Database System Concepts',    'Abraham Silberschatz', 'Databases',            '978-0073523323', 'McGraw-Hill',   2019, 6, 2),
('Operating System Concepts',   'Abraham Silberschatz', 'Operating Systems',    '978-1118063330', 'Wiley',         2018, 3, 0),
('The C Programming Language',  'Brian Kernighan',      'Programming',          '978-0131103627', 'Prentice Hall', 1988, 4, 3)
ON DUPLICATE KEY UPDATE title=title;

CREATE TABLE IF NOT EXISTS members (
    member_id  INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    phone      VARCHAR(50),
    address    VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issued_books (
    issue_id   INT AUTO_INCREMENT PRIMARY KEY,
    member_id  INT NOT NULL,
    book_id    INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date   DATE NOT NULL,
    issued_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id)   REFERENCES books(book_id)     ON DELETE CASCADE
);
