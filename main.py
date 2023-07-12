from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

import uvicorn
import sqlalchemy as sa

from model.base import Alchemy
from model.model import Entity

app = FastAPI()
templates = Jinja2Templates(directory="templates")
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
    _alch = Alchemy(filename="connection_params.json")
    with _alch.get_session() as session:
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
    _alch = Alchemy(filename="connection_params.json")
    with _alch.get_session() as session:
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
    return "It's still under construction"
    # return templates.TemplateResponse("api_start.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
