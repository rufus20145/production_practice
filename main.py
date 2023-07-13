from typing_extensions import Annotated
from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import sqlalchemy as sa

from model.base import Alchemy
from model.model import ApiKey, Entity
from monitor import ChangeMonitor

DEFAULT_FILENAME = "connection_params.json"

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db = Alchemy(filename=DEFAULT_FILENAME)
monitors = {}

# TODO переделать favicon как тут https://stackoverflow.com/a/70075352/21970878
# это решение выглядит более красиво
favicon_path = "favicon.ico"


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/objects", response_class=HTMLResponse)
@app.get("/objects/all", response_class=HTMLResponse)
def get_all_objects(request: Request):
    with db.get_session() as session:
        query = sa.select(Entity)
        result = session.scalars(query)
        entities = result.all()

    return templates.TemplateResponse(
        "objects.html", {"request": request, "entities": entities}
    )


@app.get("/objects/{entity_id}", response_class=HTMLResponse)
def get_object(request: Request, entity_id: int):
    if entity_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid entity id"
        )
    with db.get_session() as session:
        query = sa.select(Entity).filter(Entity.entity_id == entity_id)
        result = session.scalars(query)
        entities = result.all()

    if len(entities) == 0:
        return templates.TemplateResponse(
            "object.html",
            {"request": request, "entity_id": entity_id, "entities": entities},
        )

    return templates.TemplateResponse(
        "object.html",
        {"request": request, "entity_id": entity_id, "entities": entities},
    )


@app.get("/api/v1/start", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("api_start.html", {"request": request})


@app.post("/api/v1/create", response_class=JSONResponse)
async def create_api_key(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
):
    api_key = ApiKey(name=name, description=description)

    with db.get_session() as session:
        session.add(api_key)
        session.commit()

    return api_key


@app.get("/api/v1/keys", response_class=HTMLResponse)
async def get_api_keys(request: Request):
    with db.get_session() as session:
        query = sa.select(ApiKey)
        result = session.scalars(query)
        api_keys = list(result.all())

    return templates.TemplateResponse(
        "api_keys.html", {"request": request, "api_keys": api_keys}
    )


@app.get("/api/v1/get_initial_data", response_class=HTMLResponse)
def get_initial_data(api_key: str):
    with db.get_session() as session:
        query = sa.select(ApiKey).filter(ApiKey.key == api_key)
        api_key = session.scalar(query)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    if api_key.is_valid:
        if api_key.key in monitors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already got initial data",
            )
        monitor = ChangeMonitor(DEFAULT_FILENAME)
        monitors[api_key.key] = monitor
        return monitor.get_initial_state()


# TODO пофиксить повторное использование переменной api_key


@app.get("/api/v1/get_updates", response_class=HTMLResponse)
def get_updates(api_key: str):
    with db.get_session() as session:
        query = sa.select(ApiKey).filter(ApiKey.key == api_key)
        api_key = session.scalar(query)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    if api_key.is_valid:
        if api_key.key not in monitors:
            raise HTTPException(
                status_code=status.HTTP_425_TOO_EARLY,
                detail="You need to get initial data first",
            )
        monitor = monitors[api_key.key]
        return monitor.get_update()


if __name__ == "__main__":
    # made for debug purposes
    uvicorn.run(app, host="127.0.0.1", port=8000)
