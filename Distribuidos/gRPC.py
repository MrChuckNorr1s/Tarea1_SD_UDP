import grpc
from concurrent import futures
import gRPC_pb2
import gRPC_pb2_grpc
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class CacheServiceServicer(gRPC_pb2_grpc.CacheServiceServicer):

    def GetText(self, request, context):
        # Ejecutar dig para forzar la resolución DNS sin caché
        try:
            # Configurar el timeout para la ejecución del comando
            timeout = 1.5  # en segundos
            start_time = time.time()
            
            # Usar ThreadPoolExecutor para ejecutar el comando con timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(subprocess.run,
                                         ['dig', '+short', request.text, '@8.8.8.8'],  # Usando un servidor DNS público (Google en este caso)
                                         stdout=subprocess.PIPE,
                                         text=True)
                try:
                    result = future.result(timeout=timeout)  # Esperar el resultado con un timeout
                except TimeoutError:
                    # Si el tiempo de espera se agota
                    dns_result = "Error"
                    return gRPC_pb2.TextResponse(value=dns_result)
                
            dns_result = result.stdout.strip()  # El resultado de la consulta DNS
            
            # Si no hay IP, asignar una IP por defecto
            if not dns_result:
                dns_result = "0.0.0.0"

        except Exception as e:
            # Manejo de errores y respuesta
            dns_result = f"Error "

        # Enviar el resultado de la consulta
        return gRPC_pb2.TextResponse(value=dns_result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gRPC_pb2_grpc.add_CacheServiceServicer_to_server(CacheServiceServicer(), server)
    print("Binding server to port 50051")
    server.add_insecure_port('[::]:50051')
    print("Starting server")
    server.start()
    print("gRPC Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

