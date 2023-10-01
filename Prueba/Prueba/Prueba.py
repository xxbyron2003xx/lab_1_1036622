import json

data = []

with open('datos.txt', 'r') as file:
    for line in file:
        action, json_data = line.strip().split(';', 1)
        data_dict = json.loads(json_data)
        
        if action == 'INSERT':
            data.append(data_dict)
        elif action == 'PATCH':
            # Buscar el elemento existente y actualizarlo
            for item in data:
                if item.get('dpi') == data_dict.get('dpi'):
                    item.update(data_dict)
        elif action == 'DELETE':
            # Eliminar el elemento existente
            for item in data:
                if item.get('dpi') == data_dict.get('dpi'):
                    data.remove(item)

# Imprimir los datos resultantes
for item in data:
    print(item)

