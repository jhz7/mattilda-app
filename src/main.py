from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager

load_dotenv()

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass


app = FastAPI(lifespan=lifespan)
