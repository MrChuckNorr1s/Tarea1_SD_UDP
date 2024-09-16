# Usa la imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

# Comando para ejecutar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


