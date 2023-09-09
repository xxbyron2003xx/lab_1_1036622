from pickle import NONE
import sys
import json
import math
from this import s
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QLabel, QMessageBox, QInputDialog, QWidget, QHBoxLayout

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address

class Nodo:
    def __init__(self):
        self.claves = []
        self.claves_usadas = 0
        self.hoja = True
        self.hijo = []

class ArbolB:
    def __init__(self, grado):
        self.grado = grado
        self.lower = math.floor(self.grado-1)
        self.upper = (2*grado - 1)
        self.raiz = Nodo()


    def insertar (self, persona):
        if self.raiz.claves_usadas <= self.upper:
            self.raiz.claves.append(persona)
        else:
            r = self.raiz
            if self.raiz.claves_usadas == self.upper:
                s = Nodo()
                self.raiz = s
                s.hoja = False
                s.claves_usadas = 0
                s.hijo[0] = r
                self.dividir(s, 0, r)
                self.insertar_Nodo(s, persona)
            else:
                self.insertar_Nodo(r, persona)

    def insertar_Nodo (self, nodo, persona):
        if nodo.hoja:
            i = nodo.claves_usadas
            while i>=1 & persona.dpi < nodo.claves[i-1].dpi:
                nodo.claves[i] = nodo.clave[i-1]
                i -= 1
            nodo.claves[i] = persona
            nodo.claves_usadas += 1
        else:
            j = 0
            while j < nodo.claves_usadas & persona.dpi > nodo.clave[j].dpi:
                j += 1
            if nodo.hijo[j].claves_usadas == (2*self.t-1):
                self.dividir(nodo, j, nodo.hijo[j])
                if persona.dpi > nodo.claves[j]:
                    j += 1
            self.insertar_Nodo(nodo.hijo[j], persona)

    def dividir(self, padre, posicion, hijo):
        nuevo = Nodo()
        nuevo.hoja = hijo.hoja
        nuevo.claves_usadas = self.t -1
        j = 0
        while j < self.t - 1:
            j += 1
            nuevo.claves[j] =hijo.claves[j+self.t]

        if (hijo.hoja == False):
            k = 0
            while k < self.t:
                k += 2
                nuevo.hijo[k] = hijo.hijo[k+s]

        hijo.claves_usadas = self.t - 1
        j = padre.claves_usadas
        while j < posicion:
            padre.hijo[j+1] = padre.hijo [j]

        padre.hijo[posicion + 1] = nuevo
        j = padre.claves_usadas
        while j < posicion:
            j -= 1
            padre.claves[j+1] =padre.claves[j]

        padre.claves[posicion] = hijo.claves[self.t - 1]
        padre.claves_usadas += 1


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

        self.arbol = ArbolB(grado=3)

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        if archivo:
            try:
                with open(archivo, 'r') as file:
                    lineas = file.readlines()

                if len(lineas) >= 2:  # Verificar que haya al menos dos líneas (encabezado y al menos un dato)
                    for linea in lineas[1:]:
                        partes = linea.strip().split(';')
                        if len(partes) >= 2:  # Verificar si hay al menos dos partes
                            accion, json_str = partes[0], partes[1]
                            if accion == 'INSERT':
                                datos_json = json.loads(json_str)
                                persona = Persona(
                                    datos_json.get('name', ''),         # Usar get() para manejar campos faltantes
                                    datos_json.get('dpi', ''),
                                    datos_json.get('dateBirth', ''),
                                    datos_json.get('address', '')
                                )
                                # Insertar en el árbol B
                                self.arbol.insertar(persona)
                            elif accion == 'DELETE':
                                datos_json = json.loads(json_str)
                                dpi_a_eliminar = datos_json['dpi']
                                # Eliminar del árbol B
                                self.arbol.eliminar(dpi_a_eliminar)
                            elif accion == 'PATCH':
                                datos_json = json.loads(json_str)
                                dpi_a_actualizar = datos_json['dpi']
                                # Verificar si la clave existe en el diccionario de datos antes de actualizarla
                                if self.arbol.buscar(dpi_a_actualizar):  # Asumiendo que tienes un método buscar en el árbol
                                    # Actualizar en el árbol B solo si la clave existe
                                    self.arbol.actualizar(dpi_a_actualizar, datos_json)

                    QMessageBox.information(self, "Éxito", "Datos cargados exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "El archivo está vacío o no contiene suficientes líneas para procesar.")
            except Exception as e:
                print("Error al cargar datos:", str(e))

    def eliminar(self):
        dpi, ok_pressed = QInputDialog.getText(self, "Eliminar", "Ingrese el DPI de la persona a eliminar:")
        if ok_pressed:
            resultado = self.arbol.eliminar(dpi)
            if resultado:
                QMessageBox.information(self, "Éxito", "Persona eliminada exitosamente del árbol B.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró la persona con el DPI especificado en el árbol B.")

    def actualizar(self):
        dpi, ok_pressed = QInputDialog.getText(self, "Actualizar", "Ingrese el DPI de la persona a actualizar:")
        if ok_pressed:
            nuevos_datos, ok_pressed = QInputDialog.getText(self, "Actualizar", "Ingrese los nuevos datos en formato JSON:")
            if ok_pressed:
                try:
                    datos_json = json.loads(nuevos_datos)
                    resultado = self.arbol.actualizar(dpi, datos_json)
                    if resultado:
                        QMessageBox.information(self, "Éxito", "Persona actualizada exitosamente en el árbol B.")
                    else:
                        QMessageBox.warning(self, "Error", "No se encontró la persona con el DPI especificado en el árbol B.")
                except Exception as e:
                    QMessageBox.warning(self, "Error", "Formato JSON incorrecto. Asegúrate de ingresar los nuevos datos correctamente.")

    def mostrar(self):
        dialogo = DialogoMostrarPersonas(self.arbol._recorrer_arbol(self.arbol.raiz))
        dialogo.exec_()

    def buscar(self):
        texto_buscar = self.input_buscar.text().lower()
        personas_encontradas = []
        for clave, persona in self.arbol._recorrer_arbol(self.arbol.raiz):
            if texto_buscar in clave.lower() or texto_buscar in persona.nombre.lower():
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
                        data = {
                            'name': persona.nombre,
                            'dpi': persona.dpi,
                            'dateBirth': persona.date_birth,
                            'address': persona.address
                        }
                        data_str = json.dumps(data)
                        file.write(f"INSERT;{data_str}\n")

                QMessageBox.information(self, "Éxito", "Búsqueda exportada exitosamente.")
            except Exception as e:
                print("Error al exportar la búsqueda:", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())

