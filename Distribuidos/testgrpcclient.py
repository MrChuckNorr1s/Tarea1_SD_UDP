import grpc
import gRPC_pb2
import gRPC_pb2_grpc

def run():
    # Conectarse al servidor gRPC (asegúrate de que esté corriendo)
    channel = grpc.insecure_channel('grpc-server:50051')
    stub = gRPC_pb2_grpc.CacheServiceStub(channel)

    # Hacer una solicitud
    text = "youtube.com"  # Cambia esto por el dominio que quieras resolver
    request = gRPC_pb2.TextRequest(text=text)

    try:
        response = stub.GetText(request)
        print(f"Respuesta del servidor: {response.value}")
    except grpc.RpcError as e:
        print(f"Error en la comunicación con el servidor gRPC: {e}")

if __name__ == "__main__":
    run()
