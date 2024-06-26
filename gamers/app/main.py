from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
import logging
from app import players_pb2

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = "broker:19092"
KAFKA_TOPIC = "gamers"
KAFKA_GROUP_CONSUMER_ID = "gamers-comsumer-group"

class GamePlayersRegistration(SQLModel):
    player_name: str
    age: int
    email: str
    phone_number: str

async def consume():
    # Milestone: CONSUMER INTIALIZE
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER
    )

    await consumer.start()
    try:
        async for msg in consumer:
            logging.info(
                "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                    msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                    msg.timestamp)
            )
    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("starting consumer")
    asyncio.create_task(consume())
    yield

    print("stoping consumer")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello world"}


@app.post("/register-player")
async def register_new_player(player_data: GamePlayersRegistration):
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
    


    players_proto=players_pb2.GamerPlayers(player_name=player_data.player_name, age=player_data.age,email=player_data.email,phone_number=player_data.phone_number)
    serialized = players_proto.SerializeToString()
    print(f"Serialized:",serialized)

    

    await producer.start()

    try:
        await producer.send_and_wait(KAFKA_TOPIC, player_data.model_dump_json().encode('utf-8'))
    finally:
        await producer.stop()

    return player_data.model_dump_json() 