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

class NodoArbolB:
    def __init__(self, hoja=True):
        self.claves = []
        self.hijos = []
        self.hoja = hoja

class ArbolB:
    def __init__(self, grado):
        self.raiz = NodoArbolB()
        self.grado = grado

    def insert(self, clave, persona):
        nodo_actual = self.raiz
        if len(nodo_actual.claves) == (2 * self.grado) - 1:
            nueva_raiz = NodoArbolB(hoja=False)
            nueva_raiz.hijos.append(self.raiz)
            self.dividir(nueva_raiz, 0, self.raiz)
            self.raiz = nueva_raiz

        self.insertar_no_lleno(self.raiz, clave, persona)

    def insertar_no_lleno(self, nodo, clave, persona):
        i = len(nodo.claves) - 1

        while i >= 0 and clave < nodo.claves[i]:
            i -= 1

        i += 1

        if nodo.hoja:
            nodo.claves.insert(i, clave)
            nodo.hijos.insert(i, persona)
        else:
            if len(nodo.hijos[i].claves) == (2 * self.grado) - 1:
                self.dividir(nodo, i, nodo.hijos[i])
                if clave > nodo.claves[i]:
                    i += 1
            self.insertar_no_lleno(nodo.hijos[i], clave, persona)

    def dividir(self, nodo_padre, indice, nodo_hijo):
        nuevo_nodo = NodoArbolB(hoja=nodo_hijo.hoja)

        nodo_padre.claves.insert(indice, nodo_hijo.claves[self.grado - 1])
        nodo_padre.hijos.insert(indice + 1, nuevo_nodo)
        nodo_hijo.claves = nodo_hijo.claves[:self.grado - 1]
        nodo_hijo.hijos = nodo_hijo.hijos[:self.grado]

        for i in range(self.grado - 1):
            nuevo_nodo.claves.append(nodo_hijo.claves[self.grado])
            nodo_hijo.claves.pop(self.grado)

        if not nodo_hijo.hoja:
            for i in range(self.grado):
                nuevo_nodo.hijos.append(nodo_hijo.hijos[self.grado])
                nodo_hijo.hijos.pop(self.grado)

    def _recorrer_arbol(self, nodo):
        if nodo is not None:
            for i in range(len(nodo.claves)):
                if nodo.hoja:
                    yield nodo.claves[i], nodo.hijos[i]  
                else:
                    yield from self._recorrer_arbol(nodo.hijos[i])
                    yield nodo.claves[i], nodo.hijos[i]  
            if not nodo.hoja:
                yield from self._recorrer_arbol(nodo.hijos[-1])

    def actualizar(self, clave, nuevos_datos):
        return self._actualizar(self.raiz, clave, nuevos_datos)

    def _actualizar(self, nodo, clave, nuevos_datos):
        i = 0
        while i < len(nodo.claves) and clave > nodo.claves[i]:
            i += 1

        if i < len(nodo.claves) and clave == nodo.claves[i]:
            # Actualizar los datos de la persona (nodo.hijos[i]) solo si están presentes en nuevos_datos
            if 'name' in nuevos_datos:
                nodo.hijos[i].nombre = nuevos_datos['name']
            if 'dpi' in nuevos_datos:
                nodo.hijos[i].dpi = nuevos_datos['dpi']
            if 'dateBirth' in nuevos_datos:
                nodo.hijos[i].date_birth = nuevos_datos['dateBirth']
            if 'address' in nuevos_datos:
                nodo.hijos[i].address = nuevos_datos['address']
            return True
        elif nodo.hoja:
            # La clave no se encontró en el árbol B
            return False
        else:
            # Continuar la búsqueda en el siguiente nivel del árbol
            return self._actualizar(nodo.hijos[i], clave, nuevos_datos)


    def eliminar(self, clave):
        if not self.raiz.claves:
            return False

        resultado, nuevo_nodo_raiz = self._eliminar(self.raiz, clave)

        if nuevo_nodo_raiz is not None:
            self.raiz = nuevo_nodo_raiz

        return resultado

    def _eliminar(self, nodo, clave):
        i = 0
        while i < len(nodo.claves) and clave > nodo.claves[i]:
            i += 1

        if i < len(nodo.claves) and clave == nodo.claves[i]:
            if nodo.hoja:
                del nodo.claves[i]
                return True, None
            else:
                return self._eliminar_nodo_interno(nodo, clave, i)
        else:
            if nodo.hoja:
                return False, None
            else:
                return self._eliminar_subarbol(nodo, clave, i)

    def _eliminar_nodo_interno(self, nodo, clave, indice):
        hijo_actual = nodo.hijos[indice]

        if len(hijo_actual.claves) >= self.grado:
            predecesor_clave, predecesor_persona = self._encontrar_predecesor(hijo_actual, indice)
            resultado, nuevo_nodo_raiz = self._eliminar(hijo_actual, predecesor_clave)
            nodo.claves[indice] = predecesor_clave
            return resultado, nuevo_nodo_raiz

        hijo_siguiente = nodo.hijos[indice + 1]

        hijo_actual.claves.extend(nodo.claves[indice:indice + 1] + hijo_siguiente.claves)
        hijo_actual.hijos.extend(hijo_siguiente.hijos)

        del nodo.claves[indice]
        del nodo.hijos[indice + 1]

        if len(hijo_actual.claves) > (2 * self.grado) - 1:
            predecesor_clave, predecesor_persona = self._encontrar_predecesor(hijo_actual, indice)
            resultado, nuevo_nodo_raiz = self._eliminar(hijo_actual, predecesor_clave)
            nodo.claves[indice] = predecesor_clave
            return resultado, nuevo_nodo_raiz

        return self._eliminar(hijo_actual, clave)

    def _encontrar_predecesor(self, nodo, indice):
        nodo_actual = nodo.hijos[indice]
        while not nodo_actual.hoja:
            nodo_actual = nodo_actual.hijos[-1]
        return nodo_actual.claves[-1], nodo_actual.hijos[-1]

    def _eliminar_subarbol(self, nodo, clave, indice):
        hijo_actual = nodo.hijos[indice]
        hermano_izquierdo = None
        hermano_derecho = None

        if indice > 0:
            hermano_izquierdo = nodo.hijos[indice - 1]

        if indice < len(nodo.claves):
            hermano_derecho = nodo.hijos[indice + 1]

        if hermano_derecho and len(hermano_derecho.claves) >= self.grado:
            nodo.claves.insert(indice, hermano_derecho.claves.pop(0))
            if not hermano_derecho.hoja:
                nodo.hijos.insert(indice + 1, hermano_derecho.hijos.pop(0))
            return self._eliminar(hijo_actual, clave)

        elif hermano_izquierdo and len(hermano_izquierdo.claves) >= self.grado:
            nodo.claves.insert(indice, hermano_izquierdo.claves.pop())
            if not hermano_izquierdo.hoja:
                nodo.hijos.insert(indice, hermano_izquierdo.hijos.pop())
            return self._eliminar(hijo_actual, clave)

        elif hermano_derecho:
            hijo_actual.claves.append(nodo.claves.pop(indice))
            if not hermano_derecho.hoja:
                hijo_actual.hijos.append(hermano_derecho.hijos.pop(0))
            nodo.hijos.pop(indice + 1)
            return self._eliminar(hijo_actual, clave)

        elif hermano_izquierdo:
            hermano_izquierdo.claves.append(nodo.claves.pop(indice - 1))
            if not hermano_izquierdo.hoja:
                hermano_izquierdo.hijos.append(hijo_actual.hijos.pop(0))
            nodo.hijos.pop(indice)
            return self._eliminar(hermano_izquierdo, clave)

    def buscar(self, clave):
        return self._buscar(self.raiz, clave)

    def _buscar(self, nodo, clave):
        i = 0
        while i < len(nodo.claves) and clave > nodo.claves[i]:
            i += 1

        if i < len(nodo.claves) and clave == nodo.claves[i]:
            return nodo.hijos[i]  # Devolver el valor correspondiente
        elif nodo.hoja:
            return None  # La clave no se encontró en el árbol B
        else:
            return self._buscar(nodo.hijos[i], clave)




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
                            self.arbol.insert(datos_json['dpi'], persona)
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
