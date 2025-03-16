from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import sys
import random
import string
from deap import base, creator, tools, algorithms

class BitLocker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BitLocker")
        self.setGeometry(200, 200, 400, 600)
        self.initUI()
        self.saved_passwords = []
        self.init_genetic_algorithm()
    
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #E6E6FA;
            }
            QLabel {
                color: #2D3748;
                font-family: 'Arial';
            }
            QPushButton {
                background-color: #4C51BF;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #6B46C1;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #CBD5E0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Espacio para el logo
        logo_label = QLabel("BitLocker")  # Aquí podrías agregar una imagen si lo deseas
        logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Entrada para el nombre de la cuenta o propósito de la contraseña
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("Ingrese el propósito (correo, sitio web, etc.)")
        layout.addWidget(self.account_input)
        
        # Botón para generar la contraseña
        self.generate_button = QPushButton("Generar Contraseña")
        self.generate_button.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_button)
        
        # Campo de salida para mostrar la contraseña generada
        self.password_output = QTextEdit()
        self.password_output.setReadOnly(True)
        layout.addWidget(self.password_output)
        
        # Botón para guardar la contraseña
        self.save_button = QPushButton("Guardar Contraseña")
        self.save_button.clicked.connect(self.save_password)
        layout.addWidget(self.save_button)
        
        # Tabla para mostrar las contraseñas guardadas
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Propósito", "Contraseña"])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def init_genetic_algorithm(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        caracteres = string.ascii_letters + string.digits + string.punctuation
        self.toolbox.register("attr_char", random.choice, caracteres)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_char, 12)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        def evaluar_contraseña(ind):
            contraseña = "".join(ind)
            puntuacion = sum([
                any(c.islower() for c in contraseña),
                any(c.isupper() for c in contraseña),
                any(c.isdigit() for c in contraseña),
                any(c in string.punctuation for c in contraseña),
                len(contraseña) >= 12
            ])
            return puntuacion,
        
        self.toolbox.register("evaluate", evaluar_contraseña)
        self.toolbox.register("mate", tools.cxTwoPoint)
        
        def mutar_contraseña(ind, indpb=0.3):
            for i in range(len(ind)):
                if random.random() < indpb:
                    opciones = list(caracteres)
                    opciones.remove(ind[i])
                    ind[i] = random.choice(opciones)
            return ind,
        
        self.toolbox.register("mutate", mutar_contraseña)
        self.toolbox.register("select", tools.selTournament, tournsize=2)
    
    def generate_password(self):
        poblacion = self.toolbox.population(n=100)
        max_gen = 50
        mu, lambda_ = 100, 200
        
        for gen in range(max_gen):
            offspring = algorithms.varAnd(poblacion, self.toolbox, cxpb=0.5, mutpb=0.2)
            fits = [self.toolbox.evaluate(ind)[0] for ind in offspring]
            
            if max(fits) == 5:
                break
            
            poblacion = self.toolbox.select(offspring, mu)
        
        mejor_contraseña = tools.selBest(poblacion, 1)[0]
        self.password_output.setText("".join(mejor_contraseña))
    
    def save_password(self):
        purpose = self.account_input.text().strip()
        password = self.password_output.toPlainText().strip()
        
        if not purpose or not password:
            QMessageBox.warning(self, "Error", "Debe ingresar un propósito y generar una contraseña.")
            return
        
        self.saved_passwords.append((purpose, password))
        self.update_table()
        self.account_input.clear()
        self.password_output.clear()
    
    def update_table(self):
        self.table.setRowCount(len(self.saved_passwords))
        for row, (purpose, password) in enumerate(self.saved_passwords):
            self.table.setItem(row, 0, QTableWidgetItem(purpose))
            self.table.setItem(row, 1, QTableWidgetItem(password))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BitLocker()
    window.show()
    sys.exit(app.exec())
