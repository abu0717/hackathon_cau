import uvicorn
from fastapi import FastAPI
from routers import router
from settings import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
async def home():
    return "hello"


def main():
    uvicorn.run(app=app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
