#!/usr/bin/env python3

import json
import logging
import os
import uuid
from pathlib import Path
from typing import List

import dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

dotenv.load_dotenv(override=True)

VALID_USERS = os.environ.get("USERS", "").split()
PORT = int(os.environ.get("PORT", "5000"))
PRODUCTION = os.environ.get("PRODUCTION", "false") == "true"
HOST = "0.0.0.0" if PRODUCTION else "localhost"
FRONTEND_PORT = PORT if PRODUCTION else "3000"

ROOT_PATH = Path("/") if PRODUCTION else Path(__file__).parent.parent
DATA_PATH = ROOT_PATH.parent / "data"
EXAMPLES_PATH = DATA_PATH / "examples.json"
USERS_PATH = DATA_PATH / "users"


USERS_PATH.mkdir(exist_ok=True)
INSTANCE_ID = str(uuid.uuid4())

EXAMPLES = json.loads(EXAMPLES_PATH.read_text())


def read_userdata(user):
    path = USERS_PATH / f"{user}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_userdata(user, data):
    path = USERS_PATH / f"{user}.json"
    return path.write_text(json.dumps(data))


def failure(reason):
    return {"success": False, "reason": reason, "instance": INSTANCE_ID}


def success(data=None):
    result = {"success": True, "instance": INSTANCE_ID}
    if data is not None:
        result["data"] = data
    return result


def is_duplicate_free(keys):
    return len(set(keys)) == len(keys)


def get_state_inconcistency(unranked, ranking, all_keys, current_ranking=None):
    combined = unranked + ranking
    if not is_duplicate_free(combined):
        return "DUPLICATE KEYS"
    if set(combined) != all_keys:
        return "KEYS MISSMATCH"
    if current_ranking is not None and current_ranking != ranking:
        return "RANKING MISSMATCH"
    return None


uvicorn_logger = logging.getLogger("uvicorn")

App = FastAPI()

CORS = "http://localhost" if not PRODUCTION else os.environ["CORS"]
App.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{CORS}:{FRONTEND_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@App.get("/api/{user_id}")
async def get_examples(user_id: str):
    if user_id not in VALID_USERS:
        return failure("UNKNOWN USER")
    rankings = read_userdata(user_id)
    for key in EXAMPLES.keys():
        rankings.setdefault(key, [])
    return success({"examples": EXAMPLES, "rankings": rankings})


@App.get("/api/{user_id}/{example_id}")
async def get_ranking(user_id: str, example_id: str):
    if user_id not in VALID_USERS:
        return failure("UNKNOWN USER")
    if example_id not in EXAMPLES:
        return failure("UNKNOWN EXAMPLE ID")
    ranking = read_userdata(user_id).get(example_id, [])
    return success({"ranking": ranking})


class SetRankingValidator(BaseModel):
    previous_unranked: List[str]
    previous_ranking: List[str]
    next_unranked: List[str]
    next_ranking: List[str]


@App.post("/api/{user_id}/{example_id}")
async def update_ranking(user_id: str, example_id: str, body: SetRankingValidator):
    if user_id not in VALID_USERS:
        return failure("UNKNOWN USER")
    if example_id not in EXAMPLES:
        return failure("UNKNOWN EXAMPLE ID")
    userdata = read_userdata(user_id)
    hypotheses = EXAMPLES[example_id]["hypotheses"]
    all_keys = set(hypotheses.keys())
    current_ranking = userdata.get(example_id, [])
    inconcistency = get_state_inconcistency(
        body.previous_unranked, body.previous_ranking, all_keys, current_ranking
    )
    if inconcistency:
        return failure(f"PREVIOUS STATE {inconcistency}")
    inconcistency = get_state_inconcistency(
        body.next_unranked, body.next_ranking, all_keys
    )
    if inconcistency:
        return failure(f"NEXT STATE {inconcistency}")
    userdata[example_id] = body.next_ranking
    write_userdata(user_id, userdata)
    return success()


@App.on_event("startup")
def startup():
    for user in VALID_USERS:
        uvicorn_logger.info(f"USER: {CORS}:{FRONTEND_PORT}/{user}")


if __name__ == "__main__":
    uvicorn.run(App, host=HOST, port=PORT)
