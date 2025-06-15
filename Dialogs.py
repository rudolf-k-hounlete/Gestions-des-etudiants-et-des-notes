import sqlite3
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem,
                             QMessageBox, QDialog, QFormLayout, QSpinBox, QHeaderView,
                             QCheckBox, QDoubleSpinBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

DB_NAME = "gestion_scolaire.db"


class DepartmentDialog(QDialog):
    def __init__(self, department_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Département")
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.validation_grade_input = QDoubleSpinBox()
        self.validation_grade_input.setRange(0, 20)
        self.validation_grade_input.setValue(12.0)
        
        if department_data:
            self.setWindowTitle("Modifier le Département")
            self.name_input.setText(department_data['name'])
            self.validation_grade_input.setValue(department_data['validation_grade'])

        layout.addRow("Nom du département:", self.name_input)
        layout.addRow("Note de validation:", self.validation_grade_input)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Valider")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")
        
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
    def get_data(self):
        return {
            "name": self.name_input.text(),
            "validation_grade": self.validation_grade_input.value()
        }

class ProgramDialog(QDialog):
    def __init__(self, program_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Formation")
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 10)
        self.department_combo = QComboBox()
        
        self.load_departments()
        
        if program_data:
            self.setWindowTitle("Modifier la Formation")
            self.name_input.setText(program_data['name'])
            self.duration_input.setValue(program_data['duration'])
            index = self.department_combo.findData(program_data['department_id'])
            if index != -1:
                self.department_combo.setCurrentIndex(index)
        
        layout.addRow("Nom de la formation:", self.name_input)
        layout.addRow("Durée (années):", self.duration_input)
        layout.addRow("Département:", self.department_combo)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Valider")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")

        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def load_departments(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM departments ORDER BY name")
                for dep_id, name in cursor.fetchall():
                    self.department_combo.addItem(name, dep_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les départements: {e}")

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "duration": self.duration_input.value(),
            "department_id": self.department_combo.currentData()
        }

class AcademicYearDialog(QDialog):
    def __init__(self, year_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Année Académique")
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.start_year_input = QSpinBox()
        self.start_year_input.setRange(2000, 2100)
        self.start_year_input.setValue(2023)
        
        if year_data:
            self.setWindowTitle("Modifier l'Année Académique")
            self.start_year_input.setValue(year_data['start_year'])

        self.end_year_input = QSpinBox()
        self.end_year_input.setRange(2000, 2100)
        self.end_year_input.setValue(2024)
        self.end_year_input.setEnabled(False)
        
        if year_data:
            self.end_year_input.setValue(year_data['end_year'])
        
        layout.addRow("Année de début:", self.start_year_input)
        layout.addRow("Année de fin:", self.end_year_input)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Valider")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")
        
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        self.start_year_input.valueChanged.connect(self.update_end_year)
        
    def update_end_year(self):
        self.end_year_input.setValue(self.start_year_input.value() + 1)
        
    def get_data(self):
        return {
            "start_year": self.start_year_input.value(),
            "end_year": self.start_year_input.value() + 1,
            "name": f"{self.start_year_input.value()}-{self.start_year_input.value() + 1}"
        }

class StudentDialog(QDialog):
    def __init__(self, student_data=None, parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.matricule_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.first_name_input = QLineEdit()
        
        buttons = QHBoxLayout()
        if student_data:
            self.setWindowTitle("Modifier l'Étudiant")
            self.matricule_input.setText(student_data['matricule'])
            self.matricule_input.setReadOnly(True)
            self.last_name_input.setText(student_data['last_name'])
            self.first_name_input.setText(student_data['first_name'])
            ok_button = QPushButton("Modifier")
        else:
            self.setWindowTitle("Nouvel Étudiant")
            ok_button = QPushButton("Créer")

        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")
        
        layout.addRow("N° Matricule:", self.matricule_input)
        layout.addRow("Nom:", self.last_name_input)
        layout.addRow("Prénom:", self.first_name_input)
        
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return {
            "matricule": self.matricule_input.text(),
            "last_name": self.last_name_input.text(),
            "first_name": self.first_name_input.text()
        }

class EnrollStudentDialog(QDialog):
    def __init__(self, student_matricule, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inscrire l'Étudiant")
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.program_combo = QComboBox()
        self.academic_year_combo = QComboBox()
        self.year_of_study_input = QSpinBox()
        self.year_of_study_input.setRange(1, 10)
        
        self.load_programs()
        self.load_academic_years()
        
        layout.addRow("Formation:", self.program_combo)
        layout.addRow("Année Académique:", self.academic_year_combo)
        layout.addRow("Année d'Étude:", self.year_of_study_input)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Inscrire")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")
        
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        self.student_matricule = student_matricule

    def load_programs(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM programs ORDER BY name")
                for prog_id, name in cursor.fetchall():
                    self.program_combo.addItem(name, prog_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Chargement des formations impossible: {e}")

    def load_academic_years(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM academic_years ORDER BY start_year DESC")
                for year_id, name in cursor.fetchall():
                    self.academic_year_combo.addItem(name, year_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Chargement des années académiques impossible: {e}")

    def get_data(self):
        return {
            "program_id": self.program_combo.currentData(),
            "academic_year_id": self.academic_year_combo.currentData(),
            "year_of_study": self.year_of_study_input.value()
        }

class CourseDialog(QDialog):
    def __init__(self, course_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matière")
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.credits_input = QSpinBox()
        self.credits_input.setRange(1, 20)
        self.semester_input = QComboBox()
        self.semester_input.addItems(["Semestre 1", "Semestre 2"])
        self.two_grades_checkbox = QCheckBox("Nécessite deux notes (CC et Examen)")
        self.two_grades_checkbox.setChecked(True)
        
        if course_data:
            self.setWindowTitle("Modifier la Matière")
            self.name_input.setText(course_data['name'])
            self.credits_input.setValue(course_data['credits'])
            self.semester_input.setCurrentIndex(course_data['semester'] - 1)
            self.two_grades_checkbox.setChecked(course_data['has_two_grades'])

        layout.addRow("Nom de la matière:", self.name_input)
        layout.addRow("Crédits:", self.credits_input)
        layout.addRow("Semestre:", self.semester_input)
        layout.addRow("", self.two_grades_checkbox)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Valider")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")

        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "credits": self.credits_input.value(),
            "semester": self.semester_input.currentIndex() + 1,
            "has_two_grades": self.two_grades_checkbox.isChecked()
        }
        
class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Changer le mot de passe")
        layout = QFormLayout(self)
        layout.setSpacing(15)

        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Ancien mot de passe:", self.old_password_input)
        layout.addRow("Nouveau mot de passe:", self.new_password_input)
        layout.addRow("Confirmer le nouveau:", self.confirm_password_input)

        buttons = QHBoxLayout()
        ok_button = QPushButton("Changer")
        ok_button.setObjectName("primary")
        cancel_button = QPushButton("Annuler")
        cancel_button.setObjectName("secondary")

        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addRow(buttons)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_passwords(self):
        return (self.old_password_input.text(), self.new_password_input.text(), self.confirm_password_input.text())

class BulletinDialog(QDialog):
    def __init__(self, student_matricule, parent=None):
        super().__init__(parent)
        self.student_matricule = student_matricule
        self.current_year_of_study = None # Pour stocker l'année d'étude
        self.setWindowTitle(f"Bulletin de l'étudiant {self.student_matricule}")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.bulletin_info_label = QLabel("Chargement...", objectName="h2")
        self.bulletin_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bulletin_info_label)

        filter_layout = QHBoxLayout()
        self.academic_year_filter = QComboBox()
        self.semester_filter = QComboBox()
        self.semester_filter.addItems(["Année complète", "Semestre 1", "Semestre 2"])

        filter_layout.addWidget(QLabel("Année Académique:"), alignment=Qt.AlignRight)
        filter_layout.addWidget(self.academic_year_filter)
        filter_layout.addWidget(QLabel("Période:"), alignment=Qt.AlignRight)
        filter_layout.addWidget(self.semester_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.academic_year_filter.currentIndexChanged.connect(self.refresh_bulletin)
        self.semester_filter.currentIndexChanged.connect(self.refresh_bulletin)

        self.bulletin_table = QTableWidget()
        self.bulletin_table.setColumnCount(5)
        self.bulletin_table.setHorizontalHeaderLabels(["Semestre", "Unités d'Enseignement", "Note Finale", "Observation", "Crédits"])
        self.bulletin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bulletin_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bulletin_table.setAlternatingRowColors(True)
        layout.addWidget(self.bulletin_table)

        self.bulletin_summary_label = QLabel()
        self.bulletin_summary_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.bulletin_summary_label, alignment=Qt.AlignRight)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()
        close_button = QPushButton("Fermer")
        close_button.setObjectName("secondary")
        close_button.clicked.connect(self.accept)
        bottom_buttons.addWidget(close_button)
        layout.addLayout(bottom_buttons)

        self.load_academic_years()

    def load_academic_years(self):
        """Charge les années académiques où l'étudiant a été inscrit."""
        self.academic_year_filter.blockSignals(True)
        self.academic_year_filter.clear()
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT ay.id, ay.name
                    FROM academic_years ay
                    JOIN students s ON s.academic_year_id = ay.id
                    WHERE s.matricule = ?
                    ORDER BY ay.start_year DESC
                """, (self.student_matricule,))
                for year_id, name in cursor.fetchall():
                    self.academic_year_filter.addItem(name, year_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les années de l'étudiant: {e}")
        finally:
            self.academic_year_filter.blockSignals(False)
        
        self.refresh_bulletin() 

    def refresh_bulletin(self):
        """Met à jour l'affichage des notes à l'écran en fonction des filtres."""
        self.bulletin_table.setRowCount(0)
        self.bulletin_summary_label.setText("")
        
        academic_year_id = self.academic_year_filter.currentData()
        if not academic_year_id:
            self.bulletin_info_label.setText("Veuillez sélectionner une année académique.")
            return

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.first_name, s.last_name, p.name, s.year_of_study
                    FROM students s
                    LEFT JOIN programs p ON s.program_id = p.id
                    WHERE s.matricule = ? AND s.academic_year_id = ?
                """, (self.student_matricule, academic_year_id))
                student_info = cursor.fetchone()
                
                if not student_info:
                    self.bulletin_info_label.setText("Aucune inscription trouvée pour cet étudiant cette année-là.")
                    return

                fname, lname, prog_name, year_of_study = student_info
                self.current_year_of_study = year_of_study
                
                academic_year_text = self.academic_year_filter.currentText()
                self.bulletin_info_label.setText(f"Bulletin de {lname.upper()} {fname} ({prog_name})\nAnnée Académique : {academic_year_text}")
                
                period_index = self.semester_filter.currentIndex()
                query = """
                    SELECT c.name, c.credits, c.semester, c.has_two_grades, g.grade1, g.grade2, g.resit_grade, d.validation_grade
                    FROM grades g
                    JOIN courses c ON g.course_id = c.id
                    JOIN programs p ON c.program_id = p.id
                    JOIN departments d ON p.department_id = d.id
                    WHERE g.student_matricule = ? AND g.academic_year_id = ? AND c.year_of_study = ?
                """
                params = [self.student_matricule, academic_year_id, year_of_study]
                
                if period_index != 0: 
                    query += " AND c.semester = ?"
                    params.append(period_index)
                query += " ORDER BY c.semester, c.name"

                cursor.execute(query, params)
                grades_data = cursor.fetchall()

                total_points, total_credits, validated_credits = 0, 0, 0
                for row_data in grades_data:
                    c_name, credits, semester, has_two_grades, g1, g2, gr, validation_grade = row_data
                    final_grade, status = MainWindow.calculate_final_grade_and_status(g1, g2, gr, has_two_grades, validation_grade)
                    
                    row = self.bulletin_table.rowCount()
                    self.bulletin_table.insertRow(row)
                    self.bulletin_table.setItem(row, 0, QTableWidgetItem(f"Semestre {semester}"))
                    self.bulletin_table.setItem(row, 1, QTableWidgetItem(c_name))
                    self.bulletin_table.setItem(row, 2, QTableWidgetItem(f"{final_grade:.2f}" if final_grade is not None else "-"))
                    self.bulletin_table.setItem(row, 3, QTableWidgetItem(status))
                    self.bulletin_table.setItem(row, 4, QTableWidgetItem(str(credits)))

                    total_credits += credits
                    if final_grade is not None:
                        total_points += final_grade * credits
                    if status == "Validée":
                        validated_credits += credits
                
                if total_credits > 0:
                    average = total_points / total_credits
                    summary = f"Moyenne: {average:.2f}/20  |  Crédits Validés: {validated_credits}/{total_credits}"
                    self.bulletin_summary_label.setText(summary)
                else:
                    self.bulletin_summary_label.setText("Aucune note à afficher pour cette période.")

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de rafraîchir le bulletin: {e}")
