from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from supabase import create_client, Client
from config import SUPABASE_URL,SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI()

class Item(BaseModel):
    id: str

class airplaneId(BaseModel):
    id: str

connections = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/airplane")
async def create_item(item: airplaneId):
    airplane = supabase.table('airplanes').select("*").eq('refined_id',item.id).execute()
    print(airplane.data[0]['id'])
    history = supabase.table('preservation').select("*").eq("airplane_id", airplane.data[0]['id']).execute()
    report = supabase.table('report').select("*").eq("airplane_id", airplane.data[0]['id']).execute()

    print(history.data)
    for conn in connections:
        try:
            await conn.send_json({'airplane': airplane.data[0], 'history': history.data, 'report': report.data[0]})
        except RuntimeError:
            if conn in connections:
                connections.remove(conn)
    return airplane.data[0]

@app.websocket("/wsairplane")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    _ = await websocket.receive_text()