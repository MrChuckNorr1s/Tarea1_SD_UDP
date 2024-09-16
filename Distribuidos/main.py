from fastapi import FastAPI
from pydantic import BaseModel
import redis
import httpx
import hashlib

app = FastAPI()

class TextModel(BaseModel):
    text: str

# Lista de clientes Redis
redis_clients = [
    redis.Redis(host='redis1', port=6379, decode_responses=True),
    redis.Redis(host='redis2', port=6379, decode_responses=True),

]

def get_redis_client(text: str):
    # Calcular el hash del texto y determinar la partición
    text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
    partition = text_hash % len(redis_clients)
    return redis_clients[partition]

# URL del servicio gRPC Client
GRPC_CLIENT_URL = 'http://grpc-client:8002/resolve/'

# Tiempo de vida de la cache (TTL)
CACHE_TTL = 3600

# Configurar el timeout en segundos (1.5 segundos)
TIMEOUT_SECONDS = 1.5

@app.post("/text")
async def add_text_to_cache(text_model: TextModel):
    text = text_model.text
    redis_client = get_redis_client(text)

    # Verificar si el texto está en caché
    cached_value = redis_client.get(text)
    if cached_value:
        return {"message": f"HIT: {cached_value}"}

    # No encontrado en caché - hacer solicitud al gRPC Client
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(GRPC_CLIENT_URL + text)
            response.raise_for_status()
            response_data = response.json()
            print("gRPC Client Response:", response_data)

            # Manejar múltiples IPs y almacenarlas como una lista
            dns_value = response_data.get("resolved_text")
            if dns_value is None:
                return {"message": "No resolved text found in response"}

            # Almacenar el resultado en Redis con TTL
            redis_client.setex(text, CACHE_TTL, dns_value)
            return {"message": f"MISS: {dns_value}"}
        except httpx.RequestError as e:
            return {"message": f"Error while resolving text: {e}"}
        except httpx.TimeoutException:
            return {"message": "Request to gRPC Client timed out"}
