import sqlite3
import hashlib



DB_NAME = "gestion_scolaire.db"


def load_stylesheet():
    return """
        QMainWindow, QDialog {
            background-color: #f8f9fa; 
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QCheckBox, QRadioButton {
            color: #495057; /* Gris foncé */
        }

 
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
            selection-background-color: #fff3cd; 
            color: #0B1D51; /* Bleu foncé pour le texte */
        }
        QComboBox {
            color: white;
            background-color: #0B1D51;
            selection-background-color: #DC2525; 

        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #86b7fe; 
        }

        /* Style des boutons */
        QPushButton {
            color: white;
            padding: 10px 18px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: bold;
            background-color: #0B1D51; 
        }
        QPushButton#primary {
            background-color: #0d6efd; 
        }
        QPushButton#primary:hover {
            background-color: #0b5ed7;
        }
        QPushButton#danger {
            background-color: #dc3545;
        }
        QPushButton#danger:hover {
            background-color: #bb2d3b;
        }
        QPushButton#success {
            background-color: #198754; 
        }
        QPushButton#success:hover {
            background-color: #157347;
        }
        QPushButton#secondary {
            background-color: #6c757d; 
        }
        QPushButton#secondary:hover {
            background-color: #5c636a;
        }

        /* Style des onglets */
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            border-top: 3px solid #0d6efd;
            background: #FFE3A9;
            margin-top: -1px;
        }
        QTabBar::tab {
            background: #e9ecef;
            border: 1px solid #dee2e6;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 10px 20px;
            margin-right: 2px;
            font-size: 14px;
            font-weight: bold;
            color: #495057;
        }
        QTabBar::tab:selected {
            background: white;
            color: #0d6efd;
            border-bottom: 1px solid white;
        }
        QTabBar::tab:!selected:hover {
            background: #dde2e6;
        }

        /* Style des tableaux */
        QTableWidget {
            background: white;
            border: 0px solid #dee2e6;
            border-radius: 8px;
            gridline-color: #e9ecef;
            font-size: 13px;
            alternate-background-color: #f8f9fa; /* Lignes alternées */
            selection-background-color: #cfe2ff;
            selection-color: #000;
            color: #212529; 
        }
        QTableWidget::item {
            padding: 0px;
        }
        QHeaderView::section {
            background-color: #e9ecef;
            color: #212529;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #dee2e6;
            font-weight: bold;
            font-size: 13px;
        }

        /* Style des labels */
        QLabel {
            color: #343a40;
            font-size: 14px;
        }
        QLabel#title {
            color: #0B1D51;
            font-size: 28px;
            font-weight: bold;
        }
        QLabel#h2 {
            font-size: 18px;
            font-weight: bold;
            color: #495057;
            color: #0B1D51;

            padding-bottom: 5px;
            border-bottom: 2px solid #e9ecef;
            margin-bottom: 5px;
        }
        QLabel#error {
             color: #dc3545;
             font-weight: bold;
        }

        QFrame#login_frame {
            background-color: white;
            border-radius: 15px;
            border: 1px solid #dee2e6;
        }
        QMessageBox {
        background-color: #075B5E; /* Fond blanc */
        color: white;
        padding: 20px;
        }
    """

def init_db():
    """Initialise la base de données et crée/met à jour les tables."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS academic_years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            name TEXT UNIQUE NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            validation_grade REAL NOT NULL DEFAULT 12.0
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            duration_years INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            matricule TEXT PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            program_id INTEGER,
            academic_year_id INTEGER,
            year_of_study INTEGER,
            FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE SET NULL,
            FOREIGN KEY (academic_year_id) REFERENCES academic_years (id) ON DELETE SET NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('administrateur', 'responsable', 'secretaire')),
            student_id TEXT UNIQUE,
            FOREIGN KEY (student_id) REFERENCES students (matricule) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            program_id INTEGER NOT NULL,
            year_of_study INTEGER NOT NULL,
            has_two_grades BOOLEAN NOT NULL DEFAULT 1,
            UNIQUE(name, program_id, year_of_study, semester),
            FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_matricule TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            academic_year_id INTEGER NOT NULL,
            grade1 REAL,
            grade2 REAL,
            resit_grade REAL,
            UNIQUE(student_matricule, course_id, academic_year_id),
            FOREIGN KEY (student_matricule) REFERENCES students (matricule) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (academic_year_id) REFERENCES academic_years (id) ON DELETE CASCADE
        )
        ''')

        cursor.execute("SELECT COUNT(*) FROM academic_years")
        if cursor.fetchone()[0] == 0:
            current_year = 2023
            for i in range(3):
                start = current_year - i
                cursor.execute("INSERT INTO academic_years (start_year, end_year, name) VALUES (?, ?, ?)",
                              (start, start+1, f"{start}-{start+1}"))

        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_users = [
                ('admin', hash_password('adminpass'), 'administrateur', None),
                ('responsable1', hash_password('resppass'), 'responsable', None),
                ('secretaire1', hash_password('secpass'), 'secretaire', None)
            ]
            cursor.executemany("INSERT INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)", default_users)
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur de base de données: {e}")
    finally:
        if conn:
            conn.close()

def hash_password(password):
    """Hache un mot de passe pour le stockage."""
    return hashlib.sha256(password.encode()).hexdigest()
