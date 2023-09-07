import json

class Persona:
    def __init__(self, nombre, dpi, date_birth, address):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address

with open('datos.txt', 'r') as archivo_txt:
    lineas = archivo_txt.readlines()

personas = []

for linea in lineas[1:]:
    partes = linea.strip().split(';')
    if len(partes) == 2:
        accion, datos_json_str = partes
        if accion == 'INSERT':
            try:
                datos_json_dict = json.loads(datos_json_str)
                persona = Persona(
                    datos_json_dict['name'],
                    datos_json_dict['dpi'],
                    datos_json_dict['dateBirth'],
                    datos_json_dict['address']
                )
                personas.append(persona)
            except json.JSONDecodeError as e:
                print(f"Error al analizar JSON en la línea: {linea}")
        elif accion == 'DELETE':
            print(f"Registro eliminado: {datos_json_str}")
        else:
            print(f"Acción desconocida en la línea: {linea}")

for persona in personas:
    print(f"{persona.nombre}, {persona.dpi},{persona.date_birth}, {persona.address}")
