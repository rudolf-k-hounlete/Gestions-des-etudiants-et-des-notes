import sqlite3
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QStackedWidget, QGridLayout,
                             QMessageBox, QDialog, QFormLayout, QHeaderView,
                             QTabWidget, QFrame,
                             QSplitter)
from PySide6.QtGui import QPalette, QColor, QBrush, QLinearGradient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWebEngineCore import *
from functions import *
from Dialogs import *

class MainWindow(QMainWindow):
    data_changed_signal = Signal()

    def __init__(self):
        super().__init__()
        self.user_info = None
        self.setWindowTitle("SysGesco - Système de Gestion Scolaire")
        self.setGeometry(100, 100, 1400, 850)
        
        self.setStyleSheet(load_stylesheet())
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_page = self.create_login_page()
        self.stacked_widget.addWidget(self.login_page)
        
        self.main_page = QWidget()
        self.main_layout = QVBoxLayout(self.main_page)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.stacked_widget.addWidget(self.main_page)
        
        init_db()
        
    def create_login_page(self):
        page = QWidget()
        
        gradient_palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0d6efd"))
        gradient.setColorAt(1.0, QColor("#073a82"))
        gradient_palette.setBrush(QPalette.Window, QBrush(gradient))
        page.setAutoFillBackground(True)
        page.setPalette(gradient_palette)

        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        form_frame = QFrame()
        form_frame.setObjectName("login_frame")
        form_frame.setMaximumWidth(400)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("SysGesco")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Connexion au système")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6c757d; font-size: 16px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_button = QPushButton("Se connecter")
        login_button.setObjectName("primary")
        login_button.setMinimumHeight(45)
        login_button.clicked.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setAlignment(Qt.AlignCenter)
        
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(20)
        form_layout.addWidget(QLabel("Utilisateur"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Mot de passe"))
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_button)
        form_layout.addWidget(self.error_label)
        
        layout.addWidget(form_frame)
        
        return page
    
    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Veuillez remplir tous les champs.")
            return

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                password_hash = hash_password(password)
                cursor.execute("SELECT id, username, role, student_id FROM users WHERE username = ? AND password_hash = ?",
                               (username, password_hash))
                result = cursor.fetchone()
            
            if result:
                self.user_info = {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2],
                    'student_id': result[3]
                }
                self.setup_main_ui()
                self.stacked_widget.setCurrentIndex(1)
            else:
                self.error_label.setText("Nom d'utilisateur ou mot de passe incorrect.")
                
        except sqlite3.Error as e:
            self.error_label.setText(f"Erreur de base de données: {e}")
    
    def setup_main_ui(self):
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.setup_ui_for_role()
        self.data_changed_signal.connect(self.refresh_all_tabs)
        
        bottom_layout = QHBoxLayout()
        user_label = QLabel(f"Connecté: <b>{self.user_info['username']}</b> ({self.user_info['role']})")
        user_label.setStyleSheet("color: #6c757d;")
        
        change_pwd_button = QPushButton("Changer le mot de passe")
        change_pwd_button.setObjectName("secondary")
        change_pwd_button.clicked.connect(self.change_own_password)
        
        logout_button = QPushButton("Déconnexion")
        logout_button.setObjectName("danger")
        logout_button.clicked.connect(self.logout)
        
        bottom_layout.addWidget(user_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(change_pwd_button)
        bottom_layout.addWidget(logout_button)
        self.main_layout.addLayout(bottom_layout)
    
    def setup_ui_for_role(self):
        user_role = self.user_info['role']
        self.tabs.clear()

        if user_role == 'administrateur':
            self.tabs.addTab(self.create_academic_years_tab(), "Années Académiques")
            self.tabs.addTab(self.create_users_tab(), "Utilisateurs")
            self.tabs.addTab(self.create_departments_tab(), "Départements")
            self.tabs.addTab(self.create_programs_tab(), "Formations")
            self.tabs.addTab(self.create_students_tab(), "Étudiants")
            self.tabs.addTab(self.create_courses_grades_tab(), "Matières & Notes")
        elif user_role == 'responsable':
            self.tabs.addTab(self.create_academic_years_tab(), "Années Académiques")
            self.tabs.addTab(self.create_departments_tab(), "Départements")
            self.tabs.addTab(self.create_programs_tab(), "Formations")
            self.tabs.addTab(self.create_students_tab(), "Étudiants")
            self.tabs.addTab(self.create_courses_grades_tab(), "Matières & Notes")
        elif user_role == 'secretaire':
            self.tabs.addTab(self.create_students_tab(), "Étudiants")
            self.tabs.addTab(self.create_courses_grades_tab(), "Matières & Notes")
        
        self.refresh_all_tabs()
    
    def create_tool_button(self, text, object_name, on_click):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.clicked.connect(on_click)
        return button

    def create_academic_years_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Gestion des Années Académiques", objectName="h2"))

        self.year_table = QTableWidget()
        self.year_table.setColumnCount(2)
        self.year_table.setHorizontalHeaderLabels(["Nom", "Période"])
        self.year_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.year_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.year_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.year_table.setAlternatingRowColors(True)
        layout.addWidget(self.year_table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_tool_button("Ajouter", 'primary', self.add_academic_year))
        btn_layout.addWidget(self.create_tool_button("Modifier", 'secondary', self.edit_academic_year))
        btn_layout.addWidget(self.create_tool_button("Supprimer", 'danger', self.delete_academic_year))
        layout.addLayout(btn_layout)

        return tab

    def create_departments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Gestion des Départements", objectName="h2"))

        self.dep_table = QTableWidget()
        self.dep_table.setColumnCount(2)
        self.dep_table.setHorizontalHeaderLabels(["Nom du Département", "Note Validation"])
        self.dep_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dep_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dep_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dep_table.setAlternatingRowColors(True)
        layout.addWidget(self.dep_table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_tool_button("Ajouter", 'primary', self.add_department))
        btn_layout.addWidget(self.create_tool_button("Modifier", 'secondary', self.edit_department))
        btn_layout.addWidget(self.create_tool_button("Supprimer", 'danger', self.delete_department))
        layout.addLayout(btn_layout)

        return tab

    def create_programs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Gestion des Formations", objectName="h2"))
        
        self.prog_table = QTableWidget()
        self.prog_table.setColumnCount(3)
        self.prog_table.setHorizontalHeaderLabels(["Nom Formation", "Durée (ans)", "Département"])
        self.prog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prog_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.prog_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.prog_table.setAlternatingRowColors(True)
        layout.addWidget(self.prog_table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_tool_button("Ajouter", 'primary', self.add_program))
        btn_layout.addWidget(self.create_tool_button("Modifier", 'secondary', self.edit_program))
        btn_layout.addWidget(self.create_tool_button("Supprimer", 'danger', self.delete_program))
        layout.addLayout(btn_layout)
        
        return tab

    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Gestion des Étudiants", objectName="h2"))
        
        filter_layout = QHBoxLayout()
        self.student_prog_filter = QComboBox()
        filter_layout.addWidget(QLabel("Filtrer par formation:"))
        filter_layout.addWidget(self.student_prog_filter)
        filter_layout.addStretch()
        self.student_prog_filter.currentIndexChanged.connect(self.refresh_students_tab)
        layout.addLayout(filter_layout)

        self.stud_table = QTableWidget()
        self.stud_table.setColumnCount(6)
        self.stud_table.setHorizontalHeaderLabels(["N° Matricule", "Nom", "Prénom", "Formation", "Année Académique", "Année d'Étude"])
        self.stud_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stud_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stud_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stud_table.setAlternatingRowColors(True)
        layout.addWidget(self.stud_table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_tool_button("Créer", 'primary', self.add_student))
        btn_layout.addWidget(self.create_tool_button("Modifier", 'secondary', self.edit_student))
        btn_layout.addWidget(self.create_tool_button("Inscrire", 'secondary', self.enroll_student))
        btn_layout.addWidget(self.create_tool_button("Bulletin", 'secondary', self.view_student_bulletin))
        btn_layout.addWidget(self.create_tool_button("Supprimer", 'danger', self.delete_student))
        layout.addLayout(btn_layout)

        return tab

    def create_courses_grades_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_splitter = QSplitter(Qt.Horizontal)

        courses_widget = QWidget()
        courses_vbox = QVBoxLayout(courses_widget)
        courses_vbox.setSpacing(15)
        courses_vbox.addWidget(QLabel("Matières par Formation", objectName="h2"))

        filters_layout = QGridLayout()
        self.course_prog_filter = QComboBox()
        self.course_year_filter = QComboBox()
        self.course_semester_filter = QComboBox()
        filters_layout.addWidget(QLabel("Formation:"), 0, 0)
        filters_layout.addWidget(self.course_prog_filter, 0, 1)
        filters_layout.addWidget(QLabel("Année:"), 1, 0)
        filters_layout.addWidget(self.course_year_filter, 1, 1)
        filters_layout.addWidget(QLabel("Semestre:"), 2, 0)
        filters_layout.addWidget(self.course_semester_filter, 2, 1)
        courses_vbox.addLayout(filters_layout)

        self.course_prog_filter.currentIndexChanged.connect(self.update_course_year_filter)
        self.course_year_filter.currentIndexChanged.connect(self.refresh_courses_list)
        self.course_semester_filter.currentIndexChanged.connect(self.refresh_courses_list)

        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(4)
        self.courses_table.setHorizontalHeaderLabels(["Matière", "Crédits", "Semestre", "Type Note"])
        self.courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.courses_table.itemSelectionChanged.connect(self.refresh_grades_for_selected_course)
        self.courses_table.setAlternatingRowColors(True)
        courses_vbox.addWidget(self.courses_table)
        
        courses_btn_layout = QHBoxLayout()
        courses_btn_layout.addStretch()
        courses_btn_layout.addWidget(self.create_tool_button("Ajouter", 'primary', self.add_course))
        courses_btn_layout.addWidget(self.create_tool_button("Modifier", 'secondary', self.edit_course))
        courses_btn_layout.addWidget(self.create_tool_button("Supprimer", 'danger', self.delete_course))
        courses_vbox.addLayout(courses_btn_layout)
        
        grades_widget = QWidget()
        grades_vbox = QVBoxLayout(grades_widget)
        grades_vbox.setSpacing(15)
        grades_vbox.addWidget(QLabel("Saisie des Notes", objectName="h2"))
        year_filter_layout = QHBoxLayout()
        year_filter_layout.addWidget(QLabel("Année Académique:"))
        self.grades_year_filter = QComboBox()
        year_filter_layout.addWidget(self.grades_year_filter)
        year_filter_layout.addStretch()
        grades_vbox.addLayout(year_filter_layout)
        
        self.grades_table = QTableWidget()
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(7)
        self.grades_table.setHorizontalHeaderLabels(["Matricule", "Étudiant", "Note 1", "Note 2", "Rattrapage", "Moyenne/Finale", "Statut"])
        self.grades_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.itemChanged.connect(self.update_grade)
        self.grades_year_filter.currentIndexChanged.connect(self.refresh_grades_for_selected_course)
        self.grades_table.setAlternatingRowColors(True)
        grades_vbox.addWidget(self.grades_table)
        
        main_splitter.addWidget(courses_widget)
        main_splitter.addWidget(grades_widget)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)
        layout.addWidget(main_splitter)

        return tab
        
    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Gestion des Utilisateurs", objectName="h2"))

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(2)
        self.users_table.setHorizontalHeaderLabels(["Nom d'utilisateur", "Rôle"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        layout.addWidget(self.users_table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        reset_btn = self.create_tool_button("Réinitialiser Mot de Passe", 'secondary', self.admin_reset_password)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)

        return tab

    # --- Méthodes de rafraîchissement ---
    def refresh_all_tabs(self):
        role = self.user_info['role']
        if role in ['administrateur', 'responsable', 'secretaire']:
            self.update_filter_combos()

        if hasattr(self, 'dep_table'): self.refresh_departments_tab()
        if hasattr(self, 'prog_table'): self.refresh_programs_tab()
        if hasattr(self, 'stud_table'): self.refresh_students_tab()
        if hasattr(self, 'courses_table'): self.refresh_courses_and_grades_tab()
        if hasattr(self, 'users_table'): self.refresh_users_tab()
        if hasattr(self, 'year_table'): self.refresh_academic_years_tab()
        if hasattr(self, 'grades_year_filter'):
            self.load_academic_years_into_combo(self.grades_year_filter)

    def load_academic_years_into_combo(self, combo):
        combo.blockSignals(True)
        current_selection = combo.currentData()
        combo.clear()
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM academic_years ORDER BY start_year DESC")
                for year_id, name in cursor.fetchall():
                    combo.addItem(name, year_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Chargement des années académiques impossible: {e}")
        
        if current_selection:
            index = combo.findData(current_selection)
            if index != -1: combo.setCurrentIndex(index)
        elif combo.count() > 0:
            combo.setCurrentIndex(0)
        
        combo.blockSignals(False)


    def update_filter_combos(self):
        combos_to_update = []
        if hasattr(self, 'student_prog_filter'): combos_to_update.append(self.student_prog_filter)
        if hasattr(self, 'course_prog_filter'): combos_to_update.append(self.course_prog_filter)
        
        for combo in combos_to_update:
            combo.blockSignals(True)
            current_selection = combo.currentData()
            combo.clear()
            combo.addItem("Toutes les formations", None)
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name, duration_years FROM programs ORDER BY name")
                    for prog_id, name, duration in cursor.fetchall():
                        combo.addItem(name, {'id': prog_id, 'duration': duration})
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur de chargement des filtres : {e}")
            
            if current_selection:
                index = combo.findData(current_selection, role=Qt.UserRole)
                if index != -1: combo.setCurrentIndex(index)
            combo.blockSignals(False)
        
        if hasattr(self, 'course_prog_filter'): self.update_course_year_filter()
        
    def update_course_year_filter(self):
        if not hasattr(self, 'course_year_filter'): return
        self.course_year_filter.blockSignals(True)
        current_selection = self.course_year_filter.currentData()
        self.course_year_filter.clear()
        program_data = self.course_prog_filter.currentData()
        if program_data:
            for year in range(1, program_data['duration'] + 1):
                self.course_year_filter.addItem(f"Année {year}", year)
        
        if current_selection:
            index = self.course_year_filter.findData(current_selection)
            if index != -1: self.course_year_filter.setCurrentIndex(index)

        self.course_semester_filter.clear()
        self.course_semester_filter.addItems(["Semestre 1", "Semestre 2"])
        
        self.course_year_filter.blockSignals(False)
        self.refresh_courses_list()

    def refresh_departments_tab(self):
        if not hasattr(self, 'dep_table'): return
        self.dep_table.setRowCount(0)
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, validation_grade FROM departments ORDER BY name")
                for row, (dep_id, name, grade) in enumerate(cursor.fetchall()):
                    self.dep_table.insertRow(row)
                    name_item = QTableWidgetItem(name)
                    name_item.setData(Qt.UserRole, dep_id)
                    self.dep_table.setItem(row, 0, name_item)
                    self.dep_table.setItem(row, 1, QTableWidgetItem(f"{grade:.2f}"))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les départements: {e}")

    def refresh_programs_tab(self):
        if not hasattr(self, 'prog_table'): return
        self.prog_table.setRowCount(0)
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT p.id, p.name, p.duration_years, d.name, p.department_id
                    FROM programs p
                    JOIN departments d ON p.department_id = d.id
                    ORDER BY d.name, p.name
                """
                cursor.execute(query)
                for row_num, (p_id, p_name, duration, d_name, d_id) in enumerate(cursor.fetchall()):
                    self.prog_table.insertRow(row_num)
                    name_item = QTableWidgetItem(p_name)
                    name_item.setData(Qt.UserRole, {'id': p_id, 'name': p_name, 'duration': duration, 'department_id': d_id})
                    self.prog_table.setItem(row_num, 0, name_item)
                    self.prog_table.setItem(row_num, 1, QTableWidgetItem(str(duration)))
                    self.prog_table.setItem(row_num, 2, QTableWidgetItem(d_name))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les formations: {e}")
            
    def refresh_students_tab(self):
        if not hasattr(self, 'stud_table'): return
        self.stud_table.setRowCount(0)
        program_filter_data = self.student_prog_filter.currentData()
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT s.matricule, s.last_name, s.first_name, p.name, ay.name, s.year_of_study
                    FROM students s 
                    LEFT JOIN programs p ON s.program_id = p.id
                    LEFT JOIN academic_years ay ON s.academic_year_id = ay.id
                """
                params = []
                if program_filter_data:
                    query += " WHERE s.program_id = ?"
                    params.append(program_filter_data['id'])
                query += " ORDER BY s.last_name, s.first_name"
                
                cursor.execute(query, params)
                for row_num, (matricule, lname, fname, pname, ay_name, year_study) in enumerate(cursor.fetchall()):
                    self.stud_table.insertRow(row_num)
                    self.stud_table.setItem(row_num, 0, QTableWidgetItem(matricule))
                    self.stud_table.setItem(row_num, 1, QTableWidgetItem(lname))
                    self.stud_table.setItem(row_num, 2, QTableWidgetItem(fname))
                    self.stud_table.setItem(row_num, 3, QTableWidgetItem(pname or "Non inscrit"))
                    self.stud_table.setItem(row_num, 4, QTableWidgetItem(ay_name or "-"))
                    self.stud_table.setItem(row_num, 5, QTableWidgetItem(str(year_study) if year_study else "-"))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les étudiants: {e}")

    def refresh_academic_years_tab(self):
        if not hasattr(self, 'year_table'): return
        self.year_table.setRowCount(0)
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, start_year, end_year FROM academic_years ORDER BY start_year DESC")
                for row, (yid, name, start, end) in enumerate(cursor.fetchall()):
                    self.year_table.insertRow(row)
                    name_item = QTableWidgetItem(name)
                    name_item.setData(Qt.UserRole, {'id': yid, 'name': name, 'start_year': start, 'end_year': end})
                    self.year_table.setItem(row, 0, name_item)
                    self.year_table.setItem(row, 1, QTableWidgetItem(f"{start}-{end}"))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les années académiques: {e}")

    def refresh_courses_and_grades_tab(self):
        self.refresh_courses_list()
        
    def refresh_courses_list(self):
        if not hasattr(self, 'courses_table'): return
        self.courses_table.setRowCount(0)
        if hasattr(self, 'grades_table'): self.grades_table.setRowCount(0)
        
        program_data = self.course_prog_filter.currentData()
        year = self.course_year_filter.currentData()
        semester = self.course_semester_filter.currentIndex() + 1
        
        if not (program_data and year and semester > 0): return

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, credits, semester, has_two_grades 
                    FROM courses 
                    WHERE program_id = ? AND year_of_study = ? AND semester = ?
                    ORDER BY name
                """, (program_data['id'], year, semester))
                
                for row, (c_id, c_name, credits, sem, two_grades) in enumerate(cursor.fetchall()):
                    self.courses_table.insertRow(row)
                    item = QTableWidgetItem(c_name)
                    item.setData(Qt.UserRole, {'id': c_id, 'name': c_name, 'credits': credits, 'semester': sem, 'has_two_grades': two_grades, 'program_id': program_data['id']})
                    self.courses_table.setItem(row, 0, item)
                    self.courses_table.setItem(row, 1, QTableWidgetItem(str(credits)))
                    self.courses_table.setItem(row, 2, QTableWidgetItem(str(sem)))
                    self.courses_table.setItem(row, 3, QTableWidgetItem("2 Notes" if two_grades else "1 Note"))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les matières: {e}")


    def refresh_grades_for_selected_course(self):
        selected_items = self.courses_table.selectedItems()
        self.grades_table.setRowCount(0)
        if not selected_items or not self.grades_year_filter.currentData():
            return
        
        course_data = selected_items[0].data(Qt.UserRole)
        course_id = course_data['id']
        program_id = course_data['program_id']
        academic_year_id = self.grades_year_filter.currentData() 

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT d.validation_grade FROM departments d
                    JOIN programs p ON p.department_id = d.id
                    WHERE p.id = ?
                """, (program_id,))
                res = cursor.fetchone()
                validation_grade = res[0] if res else 10.0

                cursor.execute("""
                    SELECT s.matricule, s.last_name, s.first_name, g.grade1, g.grade2, g.resit_grade
                    FROM students s
                    LEFT JOIN grades g ON s.matricule = g.student_matricule AND g.course_id = ?
                    WHERE s.program_id = ? AND s.academic_year_id = ?
                    ORDER BY s.last_name, s.first_name
                """, (course_id, program_id, academic_year_id))


                
                self.grades_table.blockSignals(True)
                for row, (mat, lname, fname, g1, g2, gr) in enumerate(cursor.fetchall()):
                    self.grades_table.insertRow(row)
                    
                    mat_item = QTableWidgetItem(mat)
                    mat_item.setData(Qt.UserRole, course_id)
                    self.grades_table.setItem(row, 0, mat_item)
                    
                    name_item = QTableWidgetItem(f"{lname.upper()} {fname}")
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                    self.grades_table.setItem(row, 1, name_item)
                    
                    self.grades_table.setItem(row, 2, QTableWidgetItem(str(g1) if g1 is not None else ""))
                    
                    grade2_item = QTableWidgetItem(str(g2) if g2 is not None else "")
                    if not course_data['has_two_grades']:
                        grade2_item.setFlags(grade2_item.flags() & ~Qt.ItemIsEditable)
                        grade2_item.setBackground(QColor('lightgray'))
                    self.grades_table.setItem(row, 3, grade2_item)
                    
                    self.grades_table.setItem(row, 4, QTableWidgetItem(str(gr) if gr is not None else ""))

                    final_grade, status = self.calculate_final_grade_and_status(g1, g2, gr, course_data['has_two_grades'], validation_grade)
                    
                    grade_str = f"{final_grade:.2f}" if final_grade is not None else "-"
                    final_grade_item = QTableWidgetItem(grade_str)
                    final_grade_item.setFlags(final_grade_item.flags() & ~Qt.ItemIsEditable)

                    status_item = QTableWidgetItem(status)
                    status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)

                    self.grades_table.setItem(row, 5, final_grade_item)
                    self.grades_table.setItem(row, 6, status_item)

                self.grades_table.blockSignals(False)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les notes: {e}")
            
    def refresh_users_tab(self):
        if not hasattr(self, 'users_table'): return
        self.users_table.setRowCount(0)
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, role FROM users ORDER BY username")
                for row, (uid, uname, role) in enumerate(cursor.fetchall()):
                    self.users_table.insertRow(row)
                    item = QTableWidgetItem(uname)
                    item.setData(Qt.UserRole, uid)
                    self.users_table.setItem(row, 0, item)
                    self.users_table.setItem(row, 1, QTableWidgetItem(role))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les utilisateurs: {e}")

    def add_academic_year(self):
        dialog = AcademicYearDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO academic_years (name, start_year, end_year) VALUES (?, ?, ?)", 
                                   (data['name'], data['start_year'], data['end_year']))
                    conn.commit()
                QMessageBox.information(self, "Succès", f"Année académique '{data['name']}' ajoutée.")
                self.data_changed_signal.emit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Erreur", "Cette année académique existe déjà.")

    def edit_academic_year(self):
        selected_row = self.year_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une année à modifier.")
            return

        year_data = self.year_table.item(selected_row, 0).data(Qt.UserRole)
        dialog = AcademicYearDialog(year_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE academic_years SET name = ?, start_year = ?, end_year = ? WHERE id = ?",
                                   (new_data['name'], new_data['start_year'], new_data['end_year'], year_data['id']))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Année académique mise à jour.")
                self.data_changed_signal.emit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Erreur", "Ce nom d'année académique est déjà utilisé.")

    def delete_academic_year(self):
        selected_row = self.year_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une année à supprimer.")
            return

        year_data = self.year_table.item(selected_row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(self, "Confirmation", 
                                    f"Supprimer l'année académique '{year_data['name']}' ?\nCeci supprimera toutes les inscriptions associées.",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON;")
                    cursor.execute("DELETE FROM academic_years WHERE id = ?", (year_data['id'],))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Année académique supprimée.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur lors de la suppression : {e}")

    def add_department(self):
        dialog = DepartmentDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO departments (name, validation_grade) VALUES (?, ?)", 
                                       (data['name'], data['validation_grade']))
                        conn.commit()
                    QMessageBox.information(self, "Succès", f"Département '{data['name']}' ajouté.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce nom de département existe déjà.")

    def edit_department(self):
        selected_row = self.dep_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un département à modifier.")
            return

        dep_id = self.dep_table.item(selected_row, 0).data(Qt.UserRole)
        current_name = self.dep_table.item(selected_row, 0).text()
        current_grade = float(self.dep_table.item(selected_row, 1).text())
        
        dialog = DepartmentDialog({'name': current_name, 'validation_grade': current_grade}, self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE departments SET name = ?, validation_grade = ? WHERE id = ?",
                                       (data['name'], data['validation_grade'], dep_id))
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Département mis à jour.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce nom de département est déjà utilisé par un autre.")

    def delete_department(self):
        selected_row = self.dep_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un département à supprimer.")
            return

        dep_id = self.dep_table.item(selected_row, 0).data(Qt.UserRole)
        dep_name = self.dep_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer '{dep_name}' ?\nCeci supprimera toutes les formations, matières, et notes associées.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON;")
                    cursor.execute("DELETE FROM departments WHERE id = ?", (dep_id,))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Département supprimé.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur lors de la suppression : {e}")

    def add_program(self):
        dialog = ProgramDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name'] and data['department_id']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO programs (name, duration_years, department_id) VALUES (?, ?, ?)",
                                       (data['name'], data['duration'], data['department_id']))
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Formation ajoutée.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce nom de formation existe déjà.")

    def edit_program(self):
        selected_row = self.prog_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une formation à modifier.")
            return

        prog_data = self.prog_table.item(selected_row, 0).data(Qt.UserRole)
        dialog = ProgramDialog(prog_data, self)
        
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data['name'] and new_data['department_id']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE programs SET name=?, duration_years=?, department_id=? WHERE id=?",
                                       (new_data['name'], new_data['duration'], new_data['department_id'], prog_data['id']))
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Formation mise à jour.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce nom de formation est déjà utilisé.")

    def delete_program(self):
        selected_row = self.prog_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une formation à supprimer.")
            return

        prog_id = self.prog_table.item(selected_row, 0).data(Qt.UserRole)['id']
        prog_name = self.prog_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer la formation '{prog_name}' ?")
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON;")
                    cursor.execute("DELETE FROM programs WHERE id = ?", (prog_id,))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Formation supprimée.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur lors de la suppression : {e}")

    def add_student(self):
        dialog = StudentDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if not all(data.values()):
                QMessageBox.warning(self, "Champs requis", "Tous les champs doivent être remplis.")
                return

            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO students (matricule, last_name, first_name) VALUES (?, ?, ?)",
                                   (data['matricule'], data['last_name'], data['first_name']))
                    conn.commit()
                QMessageBox.information(self, "Succès", f"Étudiant '{data['first_name']} {data['last_name']}' créé.")
                self.data_changed_signal.emit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Erreur", "Ce numéro matricule est déjà utilisé.")
    
    def edit_student(self):
        selected_row = self.stud_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un étudiant à modifier.")
            return

        student_data = {
            'matricule': self.stud_table.item(selected_row, 0).text(),
            'last_name': self.stud_table.item(selected_row, 1).text(),
            'first_name': self.stud_table.item(selected_row, 2).text()
        }
        
        dialog = StudentDialog(student_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data['last_name'] and new_data['first_name']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE students SET last_name = ?, first_name = ? WHERE matricule = ?",
                                       (new_data['last_name'], new_data['first_name'], new_data['matricule']))
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Informations de l'étudiant mises à jour.")
                    self.data_changed_signal.emit()
                except sqlite3.Error as e:
                    QMessageBox.warning(self, "Erreur", f"Impossible de mettre à jour l'étudiant: {e}")

    def delete_student(self):
        selected_row = self.stud_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un étudiant.")
            return
        
        matricule = self.stud_table.item(selected_row, 0).text()
        name = f"{self.stud_table.item(selected_row, 1).text()} {self.stud_table.item(selected_row, 2).text()}"
        
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer l'étudiant '{name}' ({matricule}) ?\nCeci supprimera aussi son compte utilisateur et toutes ses notes.")
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON;")
                    cursor.execute("DELETE FROM students WHERE matricule = ?", (matricule,))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Étudiant et données associées supprimés.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur lors de la suppression : {e}")

    def enroll_student(self):
        selected_row = self.stud_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un étudiant.")
            return
        
        matricule = self.stud_table.item(selected_row, 0).text()
        name = f"{self.stud_table.item(selected_row, 1).text()} {self.stud_table.item(selected_row, 2).text()}"
        
        dialog = EnrollStudentDialog(matricule, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT id FROM academic_years WHERE id = ?", (data['academic_year_id'],))
                    if not cursor.fetchone():
                        QMessageBox.warning(self, "Erreur", "L'année académique sélectionnée n'existe pas.")
                        return
                    
                    cursor.execute("SELECT id FROM programs WHERE id = ?", (data['program_id'],))
                    if not cursor.fetchone():
                        QMessageBox.warning(self, "Erreur", "La formation sélectionnée n'existe pas.")
                        return

                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM students 
                        WHERE matricule = ? AND academic_year_id = ?
                    """, (matricule, data['academic_year_id']))
                    
                    if cursor.fetchone()[0] > 0:
                        QMessageBox.warning(self, "Inscription existante", "Cet étudiant est déjà inscrit pour cette année académique.")
                        return
                    
                    cursor.execute("""
                        UPDATE students 
                        SET program_id = ?, academic_year_id = ?, year_of_study = ?
                        WHERE matricule = ?
                    """, (data['program_id'], data['academic_year_id'], data['year_of_study'], matricule))
                    conn.commit()
                QMessageBox.information(self, "Succès", f"Étudiant {name} inscrit.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Erreur", f"Échec de l'inscription: {e}")

    def add_course(self):
        program_data = self.course_prog_filter.currentData()
        year_of_study = self.course_year_filter.currentData()

        if not (program_data and year_of_study):
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une formation et une année.")
            return
        
        dialog = CourseDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name'] and data['credits'] > 0:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO courses (name, credits, semester, program_id, year_of_study, has_two_grades) VALUES (?, ?, ?, ?, ?, ?)",
                            (data['name'], data['credits'], data['semester'], program_data['id'], year_of_study, data['has_two_grades'])
                        )
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Matière ajoutée.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Cette matière existe déjà pour cette formation/année/semestre.")

    def edit_course(self):
        selected_row = self.courses_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une matière à modifier.")
            return

        course_data = self.courses_table.item(selected_row, 0).data(Qt.UserRole)
        dialog = CourseDialog(course_data, self)
        
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data['name']:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE courses SET name=?, credits=?, semester=?, has_two_grades=? WHERE id=?",
                                       (new_data['name'], new_data['credits'], new_data['semester'], new_data['has_two_grades'], course_data['id']))
                        conn.commit()
                    QMessageBox.information(self, "Succès", "Matière mise à jour.")
                    self.data_changed_signal.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Une matière avec ce nom existe déjà dans ce contexte.")

    def delete_course(self):
        selected_row = self.courses_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une matière.")
            return
        
        course_id = self.courses_table.item(selected_row, 0).data(Qt.UserRole)['id']
        course_name = self.courses_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer la matière '{course_name}' ?")
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON;")
                    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Matière supprimée.")
                self.data_changed_signal.emit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur DB", f"Erreur lors de la suppression : {e}")

    def update_grade(self, item):
        self.grades_table.blockSignals(True)
        
        row, col = item.row(), item.column()
        
        matricule_item = self.grades_table.item(row, 0)
        if not matricule_item: 
            self.grades_table.blockSignals(False)
            return

        matricule = matricule_item.text()
        course_id = matricule_item.data(Qt.UserRole)
        
        new_value = None
        if item.text().strip():
            try:
                new_value = float(item.text().strip().replace(',', '.'))
                if not (0 <= new_value <= 20): raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Valeur invalide", "La note doit être un nombre entre 0 et 20.")
                self.refresh_grades_for_selected_course()
                self.grades_table.blockSignals(False)
                return

        column_map = {2: "grade1", 3: "grade2", 4: "resit_grade"}
        field_to_update = column_map.get(col)
        if not field_to_update: 
            self.grades_table.blockSignals(False)
            return

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                
                academic_year_id = self.grades_year_filter.currentData()
                if not academic_year_id:
                    QMessageBox.warning(self, "Erreur", "Aucune année académique sélectionnée.")
                    return
                    
                cursor.execute("SELECT id FROM grades WHERE student_matricule = ? AND course_id = ? AND academic_year_id = ?", 
                            (matricule, course_id, academic_year_id))
                grade_exists = cursor.fetchone()
                
                if grade_exists:
                    cursor.execute(f"UPDATE grades SET {field_to_update} = ? WHERE student_matricule = ? AND course_id = ? AND academic_year_id = ?", 
                                (new_value, matricule, course_id, academic_year_id))
                else:
                    cursor.execute(f"""
                        INSERT INTO grades 
                        (student_matricule, course_id, academic_year_id, {field_to_update}) 
                        VALUES (?, ?, ?, ?)
                    """, (matricule, course_id, academic_year_id, new_value))
                    
                conn.commit()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur DB", f"Impossible de sauvegarder la note : {e}")
        finally:
            self.refresh_grades_for_selected_course()
            self.grades_table.blockSignals(False)

    def change_own_password(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            old, new, confirm = dialog.get_passwords()
            if not new:
                QMessageBox.warning(self, "Erreur", "Le nouveau mot de passe ne peut être vide.")
                return
            if new != confirm:
                QMessageBox.warning(self, "Erreur", "Les nouveaux mots de passe ne correspondent pas.")
                return

            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (self.user_info['id'],))
                    current_hash = cursor.fetchone()[0]

                    if current_hash != hash_password(old):
                        QMessageBox.warning(self, "Erreur", "Ancien mot de passe incorrect.")
                        return

                    new_hash = hash_password(new)
                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, self.user_info['id']))
                    conn.commit()
                QMessageBox.information(self, "Succès", "Votre mot de passe a été changé.")
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Erreur DB", f"Impossible de changer le mot de passe : {e}")
                
    def admin_reset_password(self):
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un utilisateur.")
            return

        user_id = self.users_table.item(selected_row, 0).data(Qt.UserRole)
        username = self.users_table.item(selected_row, 0).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Nouveau mot de passe pour {username}")
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        pwd_input = QLineEdit()
        pwd_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Nouveau mot de passe:", pwd_input)
        ok_btn = QPushButton("Valider")
        ok_btn.setObjectName("primary")
        layout.addRow(ok_btn)
        
        def on_ok():
            new_pwd = pwd_input.text()
            if new_pwd:
                try:
                    with sqlite3.connect(DB_NAME) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_pwd), user_id))
                        conn.commit()
                    QMessageBox.information(self, "Succès", f"Mot de passe pour {username} réinitialisé.")
                    dialog.accept()
                except sqlite3.Error as e:
                    QMessageBox.warning(self, "Erreur DB", f"Impossible de réinitialiser le mot de passe : {e}")
        
        ok_btn.clicked.connect(on_ok)
        dialog.exec()

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.clear()
        
    def view_student_bulletin(self):
        selected_row = self.stud_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un étudiant dans la liste.")
            return

        matricule = self.stud_table.item(selected_row, 0).text()
        bulletin_dialog = BulletinDialog(student_matricule=matricule, parent=self)
        bulletin_dialog.exec()
        
    @staticmethod
    def calculate_final_grade_and_status(g1, g2, gr, has_two_grades, validation_grade):
        final_grade = None
        current_validation_grade = validation_grade if validation_grade is not None else 12.0

        if has_two_grades:
            if g1 is not None and g2 is not None:
                final_grade = (g1 + g2) / 2
        else:
            if g1 is not None:
                final_grade = g1
        
        if final_grade is None:
            return None, "Défaillant"

        effective_grade = final_grade
        if final_grade < 12 and gr is not None:
            effective_grade = gr

        if effective_grade >= current_validation_grade:
            status = "Validée"
        else:
            status = "Non validée"
            
        return effective_grade, status

