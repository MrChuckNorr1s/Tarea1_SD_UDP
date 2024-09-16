from fastapi import FastAPI
from pydantic import BaseModel
import grpc
import gRPC_pb2
import gRPC_pb2_grpc

app = FastAPI()

class ResolveResponse(BaseModel):
    resolved_text: str

def get_dns_resolution(text: str) -> str:
    with grpc.insecure_channel('grpc-server:50051') as channel:
        stub = gRPC_pb2_grpc.CacheServiceStub(channel)
        response = stub.GetText(gRPC_pb2.TextRequest(text=text))
        return response.value

@app.get("/resolve/{text}", response_model=ResolveResponse)
async def resolve_domain(text: str):
    try:
        resolved_text = get_dns_resolution(text)
        return {"resolved_text": resolved_text}
    except grpc.RpcError as e:
        return {"resolved_text": f"Error while resolving text: {e}"}
