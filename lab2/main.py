# SQLAlchemy setup
import json
from decimal import Decimal
from typing import Set, List, Dict
from datetime import datetime

from fastapi import FastAPI
from pydantic import field_validator, BaseModel
from sqlalchemy import MetaData, create_engine, Column, Integer, Float, String, Table, DateTime
from starlette.websockets import WebSocket, WebSocketDisconnect

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: Decimal
    longitude: Decimal


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator('timestamp', mode='before')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: Decimal
    longitude: Decimal
    timestamp: datetime


# FastAPI app setup
app = FastAPI()

# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()


# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))


# FastAPI CRUD endpoints
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    # Insert data to database
    # Send data to subscribers
    with engine.begin() as conn:
        try:
            for item in data:
                ins = processed_agent_data.insert().values(
                    road_state=item.road_state,
                    x=item.agent_data.accelerometer.x,
                    y=item.agent_data.accelerometer.y,
                    z=item.agent_data.accelerometer.z,
                    latitude=item.agent_data.gps.latitude,
                    longitude=item.agent_data.gps.longitude,
                    timestamp=item.agent_data.timestamp
                )
                conn.execute(ins)
        except Exception as e:
            return {"error": str(e)}
    await send_data_to_subscribers(data)  # Sending data to subscribers
    return {"message": "Data inserted successfully"}


@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    with engine.connect() as conn:
        select_query = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
        result = conn.execute(select_query)
        data = result.fetchone()
        if data:
            return data
        else:
            return {"message": "Data not found"}


@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    with engine.connect() as conn:
        select_query = processed_agent_data.select()
        result = conn.execute(select_query)
        data = result.fetchall()
        return data


from sqlalchemy.sql import select


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    with engine.begin() as conn:
        update_query = (
            processed_agent_data.update()
                .where(processed_agent_data.c.id == processed_agent_data_id)
                .values(
                road_state=data.road_state,
                x=data.agent_data.accelerometer.x,
                y=data.agent_data.accelerometer.y,
                z=data.agent_data.accelerometer.z,
                latitude=data.agent_data.gps.latitude,
                longitude=data.agent_data.gps.longitude,
                timestamp=data.agent_data.timestamp
            )
        )
        conn.execute(update_query)

    # Отримання оновлених даних
    with engine.connect() as conn:
        select_query = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
        updated_result = conn.execute(select_query)
        updated_data = updated_result.fetchone()
        if updated_data:
            updated_data_dict = dict(updated_data)
            return ProcessedAgentDataInDB(**updated_data_dict)
        else:
            return {"message": "Data not found"}


@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=Dict[str, str])
def delete_processed_agent_data(processed_agent_data_id: int):
    with engine.begin() as conn:
        delete_query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
        result = conn.execute(delete_query)

    # Перевірка, чи було видалення успішним
    if result.rowcount > 0:
        return {"message": "Data deleted successfully"}
    else:
        return {"message": "Data not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
