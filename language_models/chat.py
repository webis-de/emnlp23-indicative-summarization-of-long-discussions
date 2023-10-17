#!/usr/bin/env python

import argparse
from os import environ
from pathlib import Path

import dotenv
from client.chat import DEFAULT_MODEL_ARGS, ChatClient

dotenv.load_dotenv()

MODEL_HOSTS = environ.get("MODEL_HOSTS").split()
SAVE_FOLDER = Path("~").expanduser() / ".cache" / "llm_chat"

parser = argparse.ArgumentParser()
parser.add_argument("--model", default=None)
parser.add_argument("--load", default=None)
parser.add_argument("--list", action="store_true")
parser.add_argument("--save", action="store_true")
args = parser.parse_args()

model = args.model
load_name = args.load
save = args.save


if args.list:
    if not SAVE_FOLDER.exists():
        saved = []
    else:
        saved = [path.stem for path in SAVE_FOLDER.glob("*.json")]
    if not saved:
        print("--- no chats saved yet ---")
    else:
        for chat_name in saved:
            print(chat_name)
    exit(0)


if model is None and load_name is None:
    print("provide either --model or --load")
    exit(0)


extra_args = {"save": save}


if load_name is not None:
    client = ChatClient.load(
        host=MODEL_HOSTS, chat_folder=SAVE_FOLDER, name=load_name, **extra_args
    )
else:
    try:
        model_args = DEFAULT_MODEL_ARGS[model]
    except KeyError:
        model_args = {}

    client = ChatClient(
        model,
        host=MODEL_HOSTS,
        chat_folder=SAVE_FOLDER,
        name=load_name,
        **model_args,
        **extra_args
    )

client.chat_loop()
