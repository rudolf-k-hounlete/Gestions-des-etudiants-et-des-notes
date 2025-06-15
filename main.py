from Dialogs import *
from functions import *
from Windows import *
import sys
from PySide6.QtWidgets import QApplication

DB_NAME = "gestion_scolaire.db"





def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()