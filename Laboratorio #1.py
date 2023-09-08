import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QLabel, QMessageBox, QInputDialog

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Administrar Personas")
        self.setGeometry(100, 100, 400, 400)

        self.boton_cargar = QPushButton("Cargar", self)
        self.boton_cargar.setGeometry(120, 10, 140, 40)
        self.boton_cargar.clicked.connect(self.cargar)

        self.boton_mostrar = QPushButton("Mostrar", self)
        self.boton_mostrar.setGeometry(120, 60, 140, 40)
        self.boton_mostrar.clicked.connect(self.mostrar)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.setGeometry(120, 110, 140, 40)
        self.boton_actualizar.clicked.connect(self.actualizar)

        self.boton_buscar = QPushButton("Buscar", self)
        self.boton_buscar.setGeometry(120, 160, 140, 40)
        self.boton_buscar.clicked.connect(self.buscar)

        self.input_buscar = QLineEdit(self)
        self.input_buscar.setGeometry(100, 200, 180, 40)

        self.boton_eliminar = QPushButton("Eliminar", self)
        self.boton_eliminar.setGeometry(120, 250, 140, 40)
        self.boton_eliminar.clicked.connect(self.eliminar)

        self.arbol_personas = {}

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        if archivo:
            self.arbol_personas.clear()
            try:
                with open(archivo, 'r') as file:
                    lineas = file.readlines()

                for linea in lineas[1:]:
                    partes = linea.strip().split(';')
                    if len(partes) == 2:
                        accion, json_str = partes[0], partes[1]
                        if accion == 'INSERT':
                            datos_json = json.loads(json_str)
                            persona = Persona(
                                datos_json['name'],
                                datos_json['dpi'],
                                datos_json['dateBirth'],
                                datos_json['address']
                            )
                            self.arbol_personas[datos_json['dpi']] = persona
                        elif accion == 'DELETE':
                            datos_json = json.loads(json_str)
                            dpi_a_eliminar = datos_json['dpi']
                            if dpi_a_eliminar in self.arbol_personas:
                                del self.arbol_personas[dpi_a_eliminar]
                        elif accion == 'PATCH':
                            datos_json = json.loads(json_str)
                            dpi_a_actualizar = datos_json['dpi']
                            if dpi_a_actualizar in self.arbol_personas:
                                persona_actual = self.arbol_personas[dpi_a_actualizar]
                                for clave, valor in datos_json.items():
                                    if clave != 'dpi':
                                        setattr(persona_actual, clave, valor)

            except Exception as e:
                print("Error al cargar JSON:", str(e))


    def eliminar(self):
        dpi, ok_pressed = QInputDialog.getText(self, "Eliminar", "Ingrese el DPI de la persona a eliminar:")
        if ok_pressed:
            if dpi in self.arbol_personas:
                del self.arbol_personas[dpi]
                QMessageBox.information(self, "Éxito", "Persona eliminada exitosamente.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró la persona con el DPI especificado.")

    def actualizar(self):
        dpi, ok_pressed = QInputDialog.getText(self, "Actualizar", "Ingrese el DPI de la persona a actualizar:")
        if ok_pressed:
            if dpi in self.arbol_personas:
                persona_actual = self.arbol_personas[dpi]
                dialogo = DialogoActualizar(persona_actual)
                resultado = dialogo.exec_()
                if resultado == QDialog.Accepted:
                    # Actualizar los datos de la persona
                    persona_actual.nombre = dialogo.input_nombre.text()
                    persona_actual.date_birth = dialogo.input_fecha_nacimiento.text()
                    persona_actual.address = dialogo.input_direccion.text()
                    QMessageBox.information(self, "Éxito", "Persona actualizada exitosamente.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró la persona con el DPI especificado.")


    def mostrar(self):
        dialogo = DialogoMostrarPersonas(self.arbol_personas.values())
        dialogo.exec_()

    def buscar(self):
        texto_buscar = self.input_buscar.text().lower()
        personas_encontradas = []
        for dpi, persona in self.arbol_personas.items():
            if texto_buscar in dpi.lower() or texto_buscar in persona.nombre.lower():
                personas_encontradas.append(persona)

        if personas_encontradas:
            dialogo = DialogoMostrarPersonas(personas_encontradas)
            resultado = dialogo.exec_()
            if resultado == QDialog.Accepted:
                archivo_salida, _ = QFileDialog.getSaveFileName(self, "Guardar Búsqueda como TXT", "", "Text Files (*.txt)")
                if archivo_salida:
                    try:
                        with open(archivo_salida, 'w') as file:
                            file.write("RESULTADO DE LA BÚSQUEDA\n")
                            for persona in personas_encontradas:
                                file.write(f"DPI: {persona.dpi}\n")
                                file.write(f"Nombre: {persona.nombre}\n")
                                file.write(f"Fecha de Nacimiento: {persona.date_birth}\n")
                                file.write(f"Dirección: {persona.address}\n")
                                file.write("\n")

                        QMessageBox.information(self, "Éxito", "Búsqueda exportada exitosamente.")
                    except Exception as e:
                        print("Error al exportar la búsqueda:", str(e))
        else:
            QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI o nombre especificado en la búsqueda.")



class DialogoActualizar(QDialog):
    def __init__(self, persona):
        super().__init__()

        self.setWindowTitle("Actualizar Persona")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()

        self.label_nombre = QLabel("Nombre:")
        self.input_nombre = QLineEdit()
        self.label_dpi = QLabel("DPI:")
        self.input_dpi = QLineEdit()
        self.label_fecha_nacimiento = QLabel("Fecha de Nacimiento (AAAA-MM-DD):")
        self.input_fecha_nacimiento = QLineEdit()
        self.label_direccion = QLabel("Dirección:")
        self.input_direccion = QLineEdit()

        self.layout.addWidget(self.label_nombre)
        self.layout.addWidget(self.input_nombre)
        self.layout.addWidget(self.label_dpi)
        self.layout.addWidget(self.input_dpi)
        self.layout.addWidget(self.label_fecha_nacimiento)
        self.layout.addWidget(self.input_fecha_nacimiento)
        self.layout.addWidget(self.label_direccion)
        self.layout.addWidget(self.input_direccion)

        # Botones Aceptar y Cancelar
        self.boton_aceptar = QPushButton("Aceptar", self)
        self.boton_cancelar = QPushButton("Cancelar", self)
        self.boton_aceptar.clicked.connect(self.accept)
        self.boton_cancelar.clicked.connect(self.reject)
        self.layout.addWidget(self.boton_aceptar)
        self.layout.addWidget(self.boton_cancelar)

        self.setLayout(self.layout)

        self.persona = persona
        self.cargar_datos()

    def cargar_datos(self):
        self.input_nombre.setText(self.persona.nombre)
        self.input_dpi.setText(self.persona.dpi)
        self.input_fecha_nacimiento.setText(self.persona.date_birth)
        self.input_direccion.setText(self.persona.address)

    def accept(self):
        self.persona.nombre = self.input_nombre.text()
        self.persona.dpi = self.input_dpi.text()
        self.persona.date_birth = self.input_fecha_nacimiento.text()
        self.persona.address = self.input_direccion.text()
        super().accept()



class DialogoMostrarPersonas(QDialog):
    def __init__(self, personas):
        super().__init__()

        self.setWindowTitle("Mostrar Personas")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)

        self.personas = personas

        datos_personas = []
        for persona in self.personas:
            datos_personas.append(f"DPI: {persona.dpi}")
            datos_personas.append(f"Nombre: {persona.nombre}")
            datos_personas.append(f"Fecha de Nacimiento: {persona.date_birth}")
            datos_personas.append(f"Dirección: {persona.address}")
            datos_personas.append("")

        self.text_edit.setPlainText("\n".join(datos_personas))

        self.layout.addWidget(self.text_edit)

        # Agrega el botón de exportar búsqueda
        self.boton_exportar_busqueda = QPushButton("Exportar Búsqueda", self)
        self.boton_exportar_busqueda.setGeometry(150, 250, 150, 30)
        self.boton_exportar_busqueda.clicked.connect(self.exportar_busqueda)

        self.layout.addWidget(self.boton_exportar_busqueda)
        self.setLayout(self.layout)

    def exportar_busqueda(self):
        archivo_salida, _ = QFileDialog.getSaveFileName(self, "Guardar Búsqueda como TXT", "", "Text Files (*.txt)")
        if archivo_salida:
            try:
                with open(archivo_salida, 'w') as file:
                    file.write("ACTION;DATA\n")
                    for persona in self.personas:
                        datos_json = {
                            'name': persona.nombre,
                            'dpi': persona.dpi,
                            'dateBirth': persona.date_birth,
                            'address': persona.address
                        }
                        json_str = json.dumps(datos_json)
                        file.write(f"INSERT;{json_str}\n")

                QMessageBox.information(self, "Éxito", "Búsqueda exportada exitosamente.")
            except Exception as e:
                print("Error al exportar la búsqueda:", str(e))
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(app.exec_())
