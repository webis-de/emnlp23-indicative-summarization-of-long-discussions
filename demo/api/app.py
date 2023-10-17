import json
import traceback
from pathlib import Path
from typing import List, Literal, Optional

import prawcore
import uvicorn
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import HTTPException, ValidationException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from humps import camelize
from pydantic import (AfterValidator, AnyUrl, BaseModel, ConfigDict, Field,
                      ValidationError, model_validator)
from typing_extensions import Annotated

from clients import OpenAIClient
from config import DEVELOP
from disconnect import cancel_on_disconnect
from models import (LabelsModel, ObjectIdField, PostModel,
                    PrecomputedOverviewModel, StoredOverviewModel)
from pipeline import Pipeline
from store import P
from util.thread import CancableThread


def truncate_string(string, max_len=128):
    return (string[:max_len].rstrip() + "...") if len(string) > max_len else string


class SuccessJSONResponse(JSONResponse):
    def __init__(self, content, *args, **kwargs):
        content = {"success": True, "data": content}
        super().__init__(content, *args, **kwargs)


class ErrorJSONResponse(JSONResponse):
    def __init__(self, error_type, message=None, errors=None, *args, **kwargs):
        content = {"success": False, "error": error_type}
        if message is not None:
            content["message"] = message
        if errors is not None:
            content["errors"] = errors
        super().__init__(content, *args, **kwargs)


class ExceptionHandlerRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                return await original_route_handler(request)
            except HTTPException:
                raise
            except (ValidationError, ValidationException) as err:
                errors = err.errors()
                for entry in errors:
                    entry["loc"] = entry["loc"][1:]
                    print(entry["input"].keys())
                    del entry["input"]
                print(errors)
                return ErrorJSONResponse("VALIDATION", errors=errors, status_code=422)
            except prawcore.exceptions.ResponseException as err:
                return ErrorJSONResponse(
                    "APPLICATION",
                    message=f"the reddit client failed ({err}), maybe the supplied CLIENT_ID and CLIENT_SECRET are wrong",
                    status_code=500,
                )
            except Exception as err:
                print(traceback.format_exc())
                return ErrorJSONResponse(
                    "APPLICATION", message=str(err), status_code=500
                )

        return custom_route_handler


NAME_MAP = {
    "T0++": "T0",
    "text-davinci-003": "GPT3.5",
    "Llama-65B": "LLaMA-65B",
    "Llama-30B": "LLaMA-30B",
    "gpt-4": "GPT-4",
    "gpt-3.5-turbo": "ChatGPT",
}

STATIC_PATH = Path(__file__).parent / "static.json"
STATIC = json.loads(STATIC_PATH.read_text())
for e in STATIC.values():
    new_labels = {}
    for model, values in e["labels"].items():
        renamed = NAME_MAP.get(model, model)
        new_labels[renamed] = values
    e["labels"] = new_labels
    new_frames = {}
    for model, values in e["frames"].items():
        renamed = NAME_MAP.get(model, model)
        new_frames[renamed] = {renamed: values[model]}
    e["frames"] = new_frames
STATIC_LIST = [
    PrecomputedOverviewModel(
        **{**value, "id": key, "labels": list(value["labels"].keys())}
    ).model_dump()
    for key, value in STATIC.items()
]

pipeline = Pipeline()

app = FastAPI()

if DEVELOP:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


api_router = APIRouter(
    route_class=ExceptionHandlerRoute, default_response_class=SuccessJSONResponse
)


def clean_prompt(v):
    if v is not None:
        v = v.strip()
    return v


CleanString = Annotated[str, AfterValidator(clean_prompt)]


class FromRedditUrlValidator(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=camelize)

    url: AnyUrl
    model: Optional[Literal[tuple(OpenAIClient.MODELS)]] = None
    api_key: Optional[str] = None
    direct_label_instruction: Optional[CleanString] = Field(None)
    dialogue_label_instruction: Optional[CleanString] = Field(None)
    direct_frame_instruction: Optional[CleanString] = Field(None)
    dialogue_frame_instruction: Optional[CleanString] = Field(None)
    max_tokens_per_cluster: Optional[int] = Field(None, ge=256)
    top_p: float = Field(0.5, ge=0.0, le=1.0)
    temperature: float = Field(0.0, ge=0.0, le=2.0)

    @model_validator(mode="after")
    def check_none(self):
        api_key = self.api_key
        model = self.model
        if api_key is None and model is not None:
            raise ValueError("api_key is not given while model is given")
        if api_key is not None and model is None:
            raise ValueError("model is not given while api_key is given")
        return self


class PrecomputedValidator(BaseModel):
    id: str


class GetStoredValidator(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: ObjectIdField


@api_router.get("/list_precomputed", response_model=List[PrecomputedOverviewModel])
async def list_precomputed():
    return STATIC_LIST


@api_router.post("/from_precomputed", response_model=PostModel)
async def from_precomputed(body: PrecomputedValidator):
    try:
        return STATIC[body.id]
    except KeyError:
        raise HTTPException(404, f"unknown id {truncate_string(body.id)}")


@api_router.get("/precomputed/labels", response_model=LabelsModel)
async def precomputed_labels(id: str):
    return STATIC[id]


@api_router.post("/from_url", response_model=PostModel)
@cancel_on_disconnect
async def from_url(body: FromRedditUrlValidator, request: Request):
    result = await CancableThread(
        target=lambda: pipeline(**body.model_dump())
    ).execute()
    await P.insert(result)
    return result


@api_router.get("/stored", response_model=List[StoredOverviewModel])
async def stored():
    return await P.list()


@api_router.post("/stored", response_model=PostModel)
async def stored(body: GetStoredValidator):
    result = await P.get(body.id)
    if result is None:
        raise HTTPException(404, f"unknown id {body.id}")
    return result


@api_router.get("/stored/labels", response_model=LabelsModel)
async def stored_labels(id: ObjectIdField):
    return await P.labels(id)


app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return Response()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
