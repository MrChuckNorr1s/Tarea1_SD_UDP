import os

# Ruta al archivo de datos
DATA_FILE_PATH = 'db-init/Datos.txt'
LIMIT = 50000  # Limitar a 30,000 dominios, ajusta según tus necesidades

def load_domains(file_path, limit=None):
    domains = []
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if limit and i >= limit:
                break
            domains.append(line.strip())
    return domains

if __name__ == '__main__':
    domains = load_domains(DATA_FILE_PATH, LIMIT)
    with open('limited_domains.txt', 'w') as file:
        for domain in domains:
            file.write(f"{domain}\n")
    print(f"Se ha generado el archivo 'limited_domains.txt' con {len(domains)} dominios.")
