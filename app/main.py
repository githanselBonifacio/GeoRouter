from datetime import datetime

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import genetic, crud_cuida

app = FastAPI()
app.title = "Geo router api"
app.version = "0.0.1"

app.include_router(genetic.router)
app.include_router(crud_cuida.router)
origins = [
    "http://localhost",
    "http://localhost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', tags=["Test Api"])
def test():
    return "test api routerGeo"+str(datetime.now())
