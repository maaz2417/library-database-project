Library Management System
A robust web-based application built to manage library operations, including book tracking, user management, and transaction logging. This project was developed as part of a Database Systems course.

🚀 Features
Book Management: Add, update, and delete book records.

User Authentication: Secure login system for administrators/staff.

Search Functionality: Filter books by title, author, or ISBN.

Database Integration: Persistent storage using MySQL.

Responsive UI: Clean interface built with Flask and Jinja2 templates.

🛠️ Tech Stack
Backend: Python (Flask)

Database: MySQL

Frontend: HTML5, CSS3, Bootstrap

Environment: Compatible with Linux (WSL/Native) and Windows

📋 Prerequisites
Before running the project, ensure you have the following installed:

Python 3.x

MySQL Server

pip (Python package manager)

⚙️ Installation & Setup
Clone the repository:

Bash
git clone https://github.com/maaz2417/library-management-system.git
cd library-management-system
Install dependencies:

Bash
pip install flask flask-mysql
Database Configuration:

Import the provided .sql file into your MySQL instance:

SQL
SOURCE database_schema.sql;
Update the connection settings in app.py:

Python
app.config['MYSQL_DATABASE_USER'] = 'your_username'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_password'
app.config['MYSQL_DATABASE_DB'] = 'library_db'
Run the application:

Bash
python app.py
The app will be available at http://127.0.0.1:5000/.

📂 Project Structure
Plaintext
├── app.py              # Main Flask application
├── static/             # CSS and Image files
├── templates/          # HTML files (Jinja2)
├── database_schema.sql # Database export file
└── README.md           # Project documentation
📝 License
This project is open-source and available under the MIT License.
