# Sistemas Distribuidos
> Tarea 1: Sistema de caché para solicitudes DNS


## General Information
- Este proyecto implementa un sistema distribuido de caché para resolver solicitudes DNS utilizando **FastAPI**, **gRPC**, y **Redis**. El objetivo es mejorar el rendimiento de las solicitudes DNS almacenando los resultados en caché y distribuyendo las consultas a través de múltiples nodos de Redis.
- Luego de establecer la conexión se planea analizar los distintos escenarios que se piden en la tarea.


<!-- You don't have to answer all the questions - just the ones relevant to your project. -->


## Technologies Used
- Terminal Ubuntu 22.04
- Cliente y Servidor gRPC.
- Python-3 o superior, con sus dependencias.
- Redis
- FastAPI
- Contenedores Docker

## Setup
Descargar la carpeta **Distribuidos** para tener todos los archivos necesarios para levantar el sistema caché.

Antes de establecer la conexión entre los contenedores, se crea el archivo docker-compose.yml, la cual se encarga de hacer correr los múltiples contenedores de Docker para así facilitar el despliegue de los servicios del sistema, asegurando que se inicien, se conecten entre sí a través de una red común y se mantengan operativos.

Se crean los contenedores descritos en el docker-compose.yml:
```diff
sudo docker-compose up --build -d
```
Además, se trabajarán con 50.000 dominios de los 20 millones de dominios del dataset, por lo que se corre un código para crear un archivo **limited_domains.txt**:
```diff
python3 limitar_dominios.py
```
Con esto, se puede avanzar al uso del sistema.

## Usage

Para correr el sistema, simplementa se utiliza el comando **python3** para iniciar el generador de tráfico.

```diff
python3 traficgenerator.py
```




