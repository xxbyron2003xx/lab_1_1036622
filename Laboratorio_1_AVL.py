from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QLabel, QMessageBox, QInputDialog, QWidget, QHBoxLayout
import sys
import json
import os
from PyQt5.QtWidgets import QTextBrowser

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address
        self.activo = True

    def desactivar(self):
        self.activo = False

    def activar(self):
        self.activo = True

class NodoAVL:
    def __init__(self, persona):
        self.persona = persona
        self.izquierda = None
        self.derecha = None
        self.altura = 1 

class AVL:
    def __init__(self):
        self.raiz = None
        self.activo = True  

    def cambiar_estado(self, estado):
        self.activo = estado

    def altura(self, nodo):
        if nodo is None:
            return 0
        return nodo.altura

    def balance(self, nodo):
        if nodo is None:
            return 0
        return self.altura(nodo.izquierda) - self.altura(nodo.derecha)

    def insertar(self, persona):
        if not self.activo:
            return

        self.raiz = self._insertar_en_arbol(self.raiz, persona)

    def _insertar_en_arbol(self, nodo, persona):
        if nodo is None:
            return NodoAVL(persona)
        
        if persona.dpi < nodo.persona.dpi:
            nodo.izquierda = self._insertar_en_arbol(nodo.izquierda, persona)
        elif persona.dpi > nodo.persona.dpi:
            nodo.derecha = self._insertar_en_arbol(nodo.derecha, persona)
        else:
            return nodo

        nodo.altura = 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))

        balance = self.balance(nodo)

        if balance > 1 and persona.dpi < nodo.izquierda.persona.dpi:
            return self._rotar_derecha(nodo)

        if balance < -1 and persona.dpi > nodo.derecha.persona.dpi:
            return self._rotar_izquierda(nodo)

        if balance > 1 and persona.dpi > nodo.izquierda.persona.dpi:
            nodo.izquierda = self._rotar_izquierda(nodo.izquierda)
            return self._rotar_derecha(nodo)

        if balance < -1 and persona.dpi < nodo.derecha.persona.dpi:
            nodo.derecha = self._rotar_derecha(nodo.derecha)
            return self._rotar_izquierda(nodo)

        return nodo

    def _rotar_izquierda(self, nodo):
        nueva_raiz = nodo.derecha
        nodo.derecha = nueva_raiz.izquierda
        nueva_raiz.izquierda = nodo
        nodo.altura = 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))
        nueva_raiz.altura = 1 + max(self.altura(nueva_raiz.izquierda), self.altura(nueva_raiz.derecha))
        return nueva_raiz

    def _rotar_derecha(self, nodo):
        nueva_raiz = nodo.izquierda
        nodo.izquierda = nueva_raiz.derecha
        nueva_raiz.derecha = nodo
        nodo.altura = 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))
        nueva_raiz.altura = 1 + max(self.altura(nueva_raiz.izquierda), self.altura(nueva_raiz.derecha))
        return nueva_raiz

    def mostrar(self, nodo=None):
        if not self.activo:
            return []

        if nodo is None:
            nodo = self.raiz

        resultado = []
        if nodo:
            resultado.append(f"DPI: {nodo.persona.dpi}")
            resultado.append(f"Nombre: {nodo.persona.nombre}")
            resultado.append(f"Fecha de Nacimiento: {nodo.persona.date_birth}")
            resultado.append(f"Dirección: {nodo.persona.address}")

            if nodo.izquierda:
                resultado.extend(self.mostrar(nodo.izquierda))

            if nodo.derecha:
                resultado.extend(self.mostrar(nodo.derecha))

        return resultado

    def buscar(self, dpi, nodo=None):
        if not self.activo:
            return None

        if nodo is None:
            nodo = self.raiz

        if nodo is None:
            return None

        if dpi == nodo.persona.dpi:
            return nodo.persona
        elif dpi < nodo.persona.dpi:
            return self.buscar(dpi, nodo.izquierda)
        else:
            return self.buscar(dpi, nodo.derecha)

    def desactivar_persona(self, dpi):
        persona = self.buscar(dpi)
        if persona:
            persona.desactivar()
            return True
        return False

    def activar_persona(self, dpi):
        persona = self.buscar(dpi)
        if persona:
            persona.activar()
            return True
        return False

    def esta_activa(self, dpi):
        persona = self.buscar(dpi)
        if persona:
            return persona.activo
        return False

    def actualizar(self, dpi, nuevos_datos):
        if not self.activo:
            return

        self.raiz = self._actualizar_en_arbol(self.raiz, dpi, nuevos_datos)

    def _actualizar_en_arbol(self, nodo, dpi, nuevos_datos):
        if nodo is None:
            return None

        if dpi < nodo.persona.dpi:
            nodo.izquierda = self._actualizar_en_arbol(nodo.izquierda, dpi, nuevos_datos)
        elif dpi > nodo.persona.dpi:
            nodo.derecha = self._actualizar_en_arbol(nodo.derecha, dpi, nuevos_datos)
        else:
            persona = nodo.persona
            persona.nombre = nuevos_datos['nombre']
            persona.date_birth = nuevos_datos['date_birth']
            persona.address = nuevos_datos['address']

        nodo.altura = 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))

        balance = self.balance(nodo)

        return nodo

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Administrar Personas")
        self.setGeometry(100, 100, 400, 400)

        self.boton_cargar = QPushButton("Cargar", self)
        self.boton_cargar.setGeometry(120, 10, 140, 40)
        self.boton_cargar.clicked.connect(self.cargar)

        self.boton_buscar = QPushButton("Buscar", self)
        self.boton_buscar.setGeometry(120, 60, 140, 40)
        self.boton_buscar.clicked.connect(self.buscar)

        self.input_buscar = QLineEdit(self)
        self.input_buscar.setGeometry(100, 110, 180, 40)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.setGeometry(120, 160, 140, 40)
        self.boton_actualizar.clicked.connect(self.actualizar)

        self.boton_eliminar = QPushButton("Eliminar", self)
        self.boton_eliminar.setGeometry(120, 210, 140, 40)
        self.boton_eliminar.clicked.connect(self.eliminar)

        self.boton_mostrar_datos = QPushButton("Mostrar Datos", self)
        self.boton_mostrar_datos.setGeometry(120, 360, 140, 40)
        self.boton_mostrar_datos.clicked.connect(self.mostrar_datos)

        self.arbol = AVL()

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo TXT", "", "TXT Files (*.txt)")
        if archivo:
            try:
                archivo_absoluto = os.path.abspath(archivo)
                with open(archivo_absoluto, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        try:
                            parts = line.strip().split(';')
                            if len(parts) == 2:
                                accion = parts[0]
                                datos_json = parts[1]

                                if accion == 'INSERT':
                                    datos = json.loads(datos_json)
                                    persona = Persona(datos['name'], datos['dpi'], datos['dateBirth'], datos['address'])
                                    self.arbol.insertar(persona)
                                elif accion == 'DELETE':
                                    datos = json.loads(datos_json)
                                    dpi_a_eliminar = datos['dpi']
                                    self.arbol.desactivar_persona(dpi_a_eliminar)
                                elif accion == 'PATCH':
                                    datos = json.loads(datos_json)
                                    dpi_a_actualizar = datos['dpi']
                                    nuevos_datos = {
                                        'nombre': datos['name'],
                                        'date_birth': datos['dateBirth'],
                                        'address': datos['address']
                                    }
                                    self.arbol.actualizar(dpi_a_actualizar, nuevos_datos)
                        except json.JSONDecodeError as e:
                            print(f"Error al analizar JSON en línea: {line}")
                            print(f"Mensaje de error: {str(e)}")
                    QMessageBox.information(self, "Éxito", "Datos cargados exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar el archivo: {str(e)}")

    def buscar(self):
        dpi_a_buscar = self.input_buscar.text()
        if dpi_a_buscar:
            persona = self.arbol.buscar(dpi_a_buscar)
            if persona:
                QMessageBox.information(self, "Resultado de búsqueda", f"Persona encontrada:\n"
                                                                        f"DPI: {persona.dpi}\n"
                                                                        f"Nombre: {persona.nombre}\n"
                                                                        f"Fecha de Nacimiento: {persona.date_birth}\n"
                                                                        f"Dirección: {persona.address}")
            else:
                QMessageBox.warning(self, "Resultado de búsqueda", "No se encontró ninguna persona con el DPI especificado.")
        else:
            QMessageBox.warning(self, "Error", "Ingrese un DPI válido para buscar.")

    def actualizar(self):
        dpi_a_actualizar, ok = QInputDialog.getText(self, "Actualizar Persona", "Ingrese el DPI de la persona a actualizar:")
        if ok:
            persona = self.arbol.buscar(dpi_a_actualizar)
            if persona:
                dialogo_actualizar = ActualizarPersonaDialog(persona)
                if dialogo_actualizar.exec_() == QDialog.Accepted:
                    nuevos_datos = dialogo_actualizar.obtener_datos_actualizados()
                    if nuevos_datos:
                        self.arbol.actualizar(dpi_a_actualizar, nuevos_datos)
                        QMessageBox.information(self, "Éxito", "Persona actualizada exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "La operación de actualización fue cancelada.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado.")

    def eliminar(self):
        dpi_a_eliminar, ok = QInputDialog.getText(self, "Eliminar Persona", "Ingrese el DPI de la persona a eliminar:")
        if ok:
            if self.arbol.desactivar_persona(dpi_a_eliminar):
                QMessageBox.information(self, "Éxito", "Persona marcada como inactiva exitosamente.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado.")

    def mostrar_datos(self):
        datos = self.arbol.mostrar()
        if datos:
            dialogo_mostrar = MostrarDatosDialog("\n".join(datos))
            dialogo_mostrar.exec_()


class MostrarDatosDialog(QDialog):
    def __init__(self, datos):
        super().__init__()

        self.setWindowTitle("Mostrar Datos")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.texto_datos = QTextBrowser(self)
        self.texto_datos.setPlainText(datos)
        layout.addWidget(self.texto_datos)

        self.setLayout(layout)

class ActualizarPersonaDialog(QDialog):
    def __init__(self, persona):
        super().__init__()

        self.setWindowTitle("Actualizar Persona")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.input_nombre = QLineEdit(self)
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_nombre.setText(persona.nombre)
        layout.addWidget(self.input_nombre)

        self.input_date_birth = QLineEdit(self)
        self.input_date_birth.setPlaceholderText("Fecha de Nacimiento")
        self.input_date_birth.setText(persona.date_birth)
        layout.addWidget(self.input_date_birth)

        self.input_address = QLineEdit(self)
        self.input_address.setPlaceholderText("Dirección")
        self.input_address.setText(persona.address)
        layout.addWidget(self.input_address)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.clicked.connect(self.accept)
        layout.addWidget(self.boton_actualizar)

        self.setLayout(layout)

    def obtener_datos_actualizados(self):
        nuevos_datos = {}
        nuevos_datos['nombre'] = self.input_nombre.text()
        nuevos_datos['date_birth'] = self.input_date_birth.text()
        nuevos_datos['address'] = self.input_address.text()
        return nuevos_datos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
