from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QLabel, QMessageBox, QInputDialog, QWidget, QHBoxLayout
import sys
import math
import json

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address

class Nodo:
    def __init__(self):
        self.claves = []
        self.hijos = []
        self.hoja = True

class ArbolB:
    def __init__(self, grado):
        self.grado = grado
        self.raiz = None

    def insertar(self, persona):
        if self.raiz is None:
            self.raiz = Nodo()
        if len(self.raiz.claves) == 2 * self.grado - 1:
            nueva_raiz = Nodo()
            nueva_raiz.hijos.append(self.raiz)
            self.dividir(nueva_raiz, 0)
            self.raiz = nueva_raiz
        self.insertar_nodo(self.raiz, persona)

    def insertar_nodo(self, nodo, persona):
        i = len(nodo.claves) - 1
        while i >= 0 and persona.dpi < nodo.claves[i].dpi:
            i -= 1
        i += 1
        if nodo.hoja:
            nodo.claves.insert(i, persona)
        else:
            if len(nodo.hijos) == 0:
                nodo.hijos.append(None)  # Agregar primer hijo si no hay ninguno
            if len(nodo.hijos[i].claves) == (2 * self.grado) - 1:
                self.dividir(nodo, i)
                if persona.dpi > nodo.claves[i].dpi:
                    i += 1
            self.insertar_nodo(nodo.hijos[i], persona)


    def dividir(self, nodo, indice):
        nuevo_nodo = Nodo()
        nodo_hijo = nodo.hijos[indice]
        nodo.claves.insert(indice, nodo_hijo.claves.pop(self.grado - 1))
        nuevo_nodo.hoja = nodo_hijo.hoja
        nodo.hijos.insert(indice + 1, nuevo_nodo)
        nodo.claves.insert(indice, nodo_hijo.claves.pop(self.grado - 1))
        if not nodo_hijo.hoja:
            nuevo_nodo.hijos.extend(nodo_hijo.hijos[self.grado:])
            del nodo_hijo.hijos[self.grado:]

    def mostrar(self):
        if self.raiz is not None:
            return self._recorrer_arbol(self.raiz)
        else:
            return []

    def _recorrer_arbol(self, nodo):
        resultados = []

        for i in range(len(nodo.claves)):
            if not nodo.hoja:
                resultados.extend(self._recorrer_arbol(nodo.hijos[i]))
            resultados.append(nodo.claves[i])

        if not nodo.hoja:
            resultados.extend(self._recorrer_arbol(nodo.hijos[len(nodo.claves)]))

        return resultados


    def buscar(self, dpi):
        if self.raiz is not None:
            return self._buscar_en_arbol(self.raiz, dpi)
        else:
            return None

    def _buscar_en_arbol(self, nodo, dpi):
        i = 0
        while i < len(nodo.claves) and dpi > nodo.claves[i].dpi:
            i += 1
        if i < len(nodo.claves) and dpi == nodo.claves[i].dpi:
            return nodo.claves[i]
        elif nodo.hoja:
            return None
        else:
            return self._buscar_en_arbol(nodo.hijos[i], dpi)

    def eliminar(self, dpi):
        if self.raiz is not None:
            eliminado, _ = self._eliminar_en_arbol(self.raiz, dpi)
            if eliminado:
                return True
        return False

    def _eliminar_en_arbol(self, nodo, dpi):
        if nodo is None:
            return False, None

        indice = 0
        while indice < len(nodo.claves) and dpi > nodo.claves[indice].dpi:
            indice += 1

        if indice < len(nodo.claves) and dpi == nodo.claves[indice].dpi:
            if nodo.hoja:
                nodo.claves.pop(indice)
            else:
                dpi_antecesor = self._obtener_dpi_antecesor(nodo, indice)
                nodo.claves[indice] = dpi_antecesor
                eliminado, nodo_modificado = self._eliminar_en_arbol(nodo.hijos[indice + 1], dpi_antecesor.dpi)
                if nodo_modificado is not None:
                    nodo.hijos[indice + 1] = nodo_modificado
                if eliminado:
                    eliminado, nodo_modificado = self._eliminar_en_arbol(nodo.hijos[indice], dpi)
                    if nodo_modificado is not None:
                        nodo.hijos[indice] = nodo_modificado

        elif nodo.hoja:
            return False, None

        else:
            if indice == len(nodo.claves):
                indice -= 1
            dpi_hijo = nodo.claves[indice]
            if len(nodo.hijos[indice].claves) <= self.grado - 1:
                hermano = None
                if indice > 0 and len(nodo.hijos[indice - 1].claves) > self.grado - 1:
                    hermano = nodo.hijos[indice - 1]
                elif indice < len(nodo.hijos) - 1 and len(nodo.hijos[indice + 1].claves) > self.grado - 1:
                    hermano = nodo.hijos[indice + 1]
                if hermano:
                    self._mover_clave(nodo, indice, hermano)
                else:
                    if indice > 0:
                        hermano = nodo.hijos[indice - 1]
                    else:
                        hermano = nodo.hijos[indice + 1]
                    nodo_modificado = self._combinar_nodos(nodo, indice, hermano)
                    return self._eliminar_en_arbol(nodo_modificado, dpi)

            eliminado, nodo_modificado = self._eliminar_en_arbol(nodo.hijos[indice], dpi)
            if nodo_modificado is not None:
                nodo.hijos[indice] = nodo_modificado

        if len(nodo.claves) < self.grado - 1:
            return False, None

        return True, nodo

    def _eliminar_en_nodo_no_hoja(self, nodo, indice):
        dpi_antecesor = self._obtener_dpi_antecesor(nodo, indice)
        if len(nodo.hijos[indice].claves) >= self.grado:
            nodo.claves[indice] = dpi_antecesor
            return self._eliminar_en_arbol(nodo.hijos[indice], dpi_antecesor.dpi)
        elif len(nodo.hijos[indice + 1].claves) >= self.grado:
            dpi_sucesor = self._obtener_dpi_sucesor(nodo, indice)
            nodo.claves[indice] = dpi_sucesor
            return self._eliminar_en_arbol(nodo.hijos[indice + 1], dpi_sucesor.dpi)
        else:
            self._combinar_nodos(nodo, indice)
            return self._eliminar_en_arbol(nodo.hijos[indice], dpi_antecesor.dpi)

    def _obtener_dpi_antecesor(self, nodo, indice):
        nodo_actual = nodo.hijos[indice]
        while not nodo_actual.hoja:
            nodo_actual = nodo_actual.hijos[-1]
        return nodo_actual.claves[-1]

    def _obtener_dpi_sucesor(self, nodo, indice):
        nodo_actual = nodo.hijos[indice + 1]
        while not nodo_actual.hoja:
            nodo_actual = nodo_actual.hijos[0]
        return nodo_actual.claves[0]

    def _combinar_nodos(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano = nodo.hijos[indice + 1]
        hijo.claves.append(nodo.claves[indice])
        hijo.claves.extend(hermano.claves)
        if not hijo.hoja:
            hijo.hijos.extend(hermano.hijos)
        del nodo.claves[indice]
        del nodo.hijos[indice + 1]

    def actualizar(self, dpi, nuevos_datos):
        persona = self.buscar(dpi)
        if persona:
            persona.nombre = nuevos_datos.get('nombre', persona.nombre)
            persona.date_birth = nuevos_datos.get('date_birth', persona.date_birth)
            persona.address = nuevos_datos.get('address', persona.address)
            return True
        else:
            return False


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

        self.arbol = ArbolB(2)

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        if archivo:
            try:
                with open(archivo, 'r') as file:
                    lineas = file.readlines()

                if len(lineas) >= 2:
                    for linea in lineas[1:]:
                        partes = linea.strip().split(';')
                        if len(partes) >= 2:
                            accion, json_str = partes[0], partes[1]
                            if accion == 'INSERT':
                                datos_json = json.loads(json_str)
                                persona = Persona(
                                    datos_json.get('name', ''),
                                    datos_json.get('dpi', ''),
                                    datos_json.get('dateBirth', ''),
                                    datos_json.get('address', '')
                                )
                                self.arbol.insertar(persona)
                            elif accion == 'DELETE':
                                datos_json = json.loads(json_str)
                                dpi_a_eliminar = datos_json['dpi']
                                self.arbol.eliminar(dpi_a_eliminar)
                            elif accion == 'PATCH':
                                datos_json = json.loads(json_str)
                                dpi_a_actualizar = datos_json['dpi']
                                if self.arbol.buscar(dpi_a_actualizar):
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
        personas = self.arbol.mostrar()
        if personas:
            dialogo = DialogoMostrarPersonas(personas)
            dialogo.exec_()
        else:
            QMessageBox.warning(self, "Error", "El árbol B está vacío.")

    def buscar(self):
        texto_buscar = self.input_buscar.text().lower()
        persona_encontrada = self.arbol.buscar(texto_buscar)
        if persona_encontrada:
            dialogo = DialogoMostrarPersonas([persona_encontrada])
            dialogo.exec_()
        else:
            QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI o nombre especificado en la búsqueda.")


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
                    file.write("RESULTADO DE LA BÚSQUEDA\n")
                    for persona in self.personas:
                        file.write(f"DPI: {persona.dpi}\n")
                        file.write(f"Nombre: {persona.nombre}\n")
                        file.write(f"Fecha de Nacimiento: {persona.date_birth}\n")
                        file.write(f"Dirección: {persona.address}\n")
                        file.write("\n")

                QMessageBox.information(self, "Éxito", "Búsqueda exportada exitosamente.")
            except Exception as e:
                print("Error al exportar la búsqueda:", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
