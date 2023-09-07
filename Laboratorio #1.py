import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Menú")
        self.setGeometry(100, 100, 400, 300)

        self.boton_cargar = QPushButton("Cargar Archivo", self)
        self.boton_cargar.setGeometry(150, 120, 100, 40)
        self.boton_cargar.clicked.connect(self.mostrar)

    def mostrar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        if archivo:
            try:
                with open(archivo, 'r') as file:
                    lineas = file.readlines()

                personas = []

                for linea in lineas[1:]:
                    partes = linea.strip().split(';')
                    if len(partes) == 2 and partes[0] == 'INSERT':
                        json_str = partes[1]
                        datos_json = json.loads(json_str)
                        persona = Persona(
                            datos_json['name'],
                            datos_json['dpi'],
                            datos_json['dateBirth'],
                            datos_json['address']
                        )
                        personas.append(persona)

                dialogo = VentanaEmergente(personas)
                dialogo.exec_()
            except Exception as e:
                print("Error al cargar y mostrar JSON:", str(e))

class VentanaEmergente(QDialog):
    def __init__(self, personas):
        super().__init__()

        self.setWindowTitle("Datos de Personas")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        
        datos_personas = []
        for persona in personas:
            datos_personas.append(f"Nombre: {persona.nombre}")
            datos_personas.append(f"DPI: {persona.dpi}")
            datos_personas.append(f"Fecha de Nacimiento: {persona.date_birth}")
            datos_personas.append(f"Dirección: {persona.address}")
            datos_personas.append("")  
            
        self.text_edit.setPlainText("\n".join(datos_personas))

        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(app.exec_())
