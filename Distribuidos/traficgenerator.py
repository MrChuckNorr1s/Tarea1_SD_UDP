import requests
import time
import random
import hashlib
import matplotlib.pyplot as plt
import csv
from collections import Counter, defaultdict

API_URL = 'http://localhost:8000/text'  # URL de tu API FastAPI
DOMAINS_FILE = 'limited_domains.txt'     # Archivo con dominios
NUM_QUERIES = 75000  # Número total de consultas a realizar
CSV_FILE = 'results.csv'         # Archivo donde guardar el resumen
GRAPH_FILE = 'domain_frequency.png'      # Archivo del gráfico de frecuencias de HITs

# Inicializamos un contador de solicitudes por partición
partition_load = defaultdict(lambda: {'requests': 0, 'hits': 0, 'misses': 0})

# Definir particiones para balance de carga usando hash (en lugar de rangos)
NUM_PARTITIONS = 2  # Debe coincidir con el número de instancias Redis en la API

def get_partition_by_domain(domain):
    """Obtener la partición usando hash del dominio"""
    domain_hash = int(hashlib.md5(domain.encode()).hexdigest(), 16)
    partition = domain_hash % NUM_PARTITIONS
    return f'redis{partition + 1}'  # Redis 1 a Redis 8

def send_request(domain):
    start_time = time.time()  # Registrar el tiempo de inicio de la solicitud
    response = requests.post(
        API_URL,
        json={'text': domain},
        headers={'Content-Type': 'application/json'}
    )
    end_time = time.time()  # Registrar el tiempo de fin de la solicitud
    response_time = end_time - start_time
    return response.json(), response_time

def save_summary_to_csv(total_requests, total_time, avg_response_time, hit_count, miss_count, partition_load):
    """Función para guardar el resumen final en el archivo CSV"""
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Total requests', total_requests])
        writer.writerow(['Total time (s)', total_time])
        writer.writerow(['Average response time (s)', avg_response_time])
        writer.writerow(['Total HITs', hit_count])
        writer.writerow(['Total MISSs', miss_count])
        writer.writerow(['Partition', 'Total Requests', 'Total HITs', 'Total MISSs'])
        for partition, data in partition_load.items():
            writer.writerow([partition, data['requests'], data['hits'], data['misses']])

def generate_initial_graph(domains):
    """Generar gráfico inicial con todos los dominios numerados sin HITs aún"""
    domain_indices = range(len(domains))
    plt.figure(figsize=(10, 6))
    plt.bar(domain_indices, [0] * len(domains), color='lightblue')  # Inicialmente todos en 0
    plt.xticks(
        ticks=range(0, len(domains), 10000),  # Mostrar cada 10000 dominios
        labels=range(0, len(domains), 10000),  # Etiquetas cada 10000 dominios
        rotation=90
    )
    plt.xlabel('Índice de Dominio')
    plt.ylabel('Cantidad de HITs')
    plt.title('Frecuencia de HITs por dominio (Inicial)')
    plt.tight_layout()
    plt.savefig(GRAPH_FILE)
    print(f"Gráfico inicial guardado en {GRAPH_FILE}")

def update_graph(domains, hit_domains):
    """Actualizar gráfico con la frecuencia de HITs"""
    domain_indices = range(len(domains))
    domain_counter = Counter(hit_domains)  # Contar las repeticiones de cada dominio (HITs)
    hit_frequencies = [domain_counter.get(domain, 0) for domain in domains]  # Obtener HITs para cada dominio

    plt.figure(figsize=(10, 6))
    plt.bar(domain_indices, hit_frequencies, color='green')
    plt.xticks(
        ticks=range(0, len(domains), 10000),  # Mostrar cada 10000 dominios
        labels=range(0, len(domains), 10000),  # Etiquetas cada 10000 dominios
        rotation=90
    )
    plt.xlabel('Índice de Dominio')
    plt.ylabel('Cantidad de HITs')
    plt.title('Frecuencia de HITs por dominio')
    plt.tight_layout()

    # Guardar el gráfico en un archivo PNG
    plt.savefig(GRAPH_FILE)
    print(f"Gráfico actualizado guardado en {GRAPH_FILE}")

def main():
    # Leer dominios del archivo
    with open(DOMAINS_FILE, 'r') as file:
        domains = [line.strip() for line in file]

    # Generar gráfico inicial con todos los dominios numerados y sin HITs
    generate_initial_graph(domains)

    total_requests = NUM_QUERIES
    total_time = 0
    hit_count = 0
    miss_count = 0
    hit_domains = []  # Lista para almacenar solo los dominios que hacen HIT

    requested_domains = []  # Lista para almacenar los dominios consultados

    for index in range(1, total_requests + 1):
        domain = random.choice(domains)  # Seleccionar aleatoriamente un dominio
        requested_domains.append(domain)  # Almacenar dominio consultado

        # Obtener la partición a la que pertenece el dominio (usando hash)
        partition = get_partition_by_domain(domain)
        partition_load[partition]['requests'] += 1  # Incrementar las solicitudes para esta partición

        result, response_time = send_request(domain)
        total_time += response_time

        # Contar HIT y MISS
        message = result.get('message', '')
        if 'HIT' in message:
            hit_count += 1
            hit_domains.append(domain)  # Registrar dominio con HIT
            partition_load[partition]['hits'] += 1  # Incrementar HIT en la partición
        elif 'MISS' in message:
            miss_count += 1
            partition_load[partition]['misses'] += 1  # Incrementar MISS en la partición

        print(f"Request {index}/{total_requests} - Domain: {domain} -> Response: {result} -> Response Time: {response_time:.4f} seconds")

    # Al terminar, calcular promedio y mostrar resultados
    if total_requests > 0:
        avg_response_time = total_time / total_requests
        print(f"\nTotal requests: {total_requests}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average response time: {avg_response_time:.4f} seconds")
        print(f"Total HITs: {hit_count}")
        print(f"Total MISSs: {miss_count}")

    # Guardar el resumen final en el archivo CSV, incluyendo el balance de carga por partición
    save_summary_to_csv(total_requests, total_time, avg_response_time, hit_count, miss_count, partition_load)

    # Generar el gráfico de frecuencias basado en dominios que hicieron HIT
    update_graph(domains, hit_domains)

if __name__ == '__main__':
    main()
