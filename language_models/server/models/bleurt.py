import tensorflow as tf

for gpu in tf.config.list_physical_devices("GPU"):
    tf.config.experimental.set_memory_growth(gpu, True)

from math import ceil
from pathlib import Path
from urllib.parse import urljoin
from zipfile import ZipFile

import bleurt.score
import requests
from tqdm import tqdm


def download_file(url, save_path, chunk_size=20 * 1024**2):
    Path(save_path).parent.mkdir(exist_ok=True, parents=True)
    with requests.get(url, stream=True) as req:
        req.raise_for_status()

        length = req.headers.get("Content-length")
        total = ceil(int(length) / chunk_size) if length is not None else None
        chunks = tqdm(
            req.iter_content(chunk_size=chunk_size), postfix=save_path.name, total=total
        )

        with open(save_path, "wb") as file:
            for chunk in chunks:
                file.write(chunk)


class BLEURTScorer:
    MODEL = "BLEURT-20"
    MODEL_PATH = Path("~/.cache/bleurt/").expanduser()

    def __init__(self):
        self.setup()

    @classmethod
    def setup(cls, force=False):
        if force or not (cls.MODEL_PATH / cls.MODEL).exists():
            model_base_url = "https://storage.googleapis.com/bleurt-oss-21/"
            model_url = urljoin(model_base_url + "/", cls.MODEL + ".zip")
            zip_path = cls.MODEL_PATH / "model.zip"
            download_file(model_url, zip_path)
            with ZipFile(zip_path, "r") as zip_file:
                zip_file.extractall(cls.MODEL_PATH)

    def __init__(self):
        self.bleurt = bleurt.score.BleurtScorer(str(self.MODEL_PATH / self.MODEL))

    def __call__(self, batch):
        hypotheses, references = zip(*batch)
        return self.bleurt.score(
            references=references, candidates=hypotheses, batch_size=len(batch)
        )


class Model:
    TYPE = "metric"

    PREFERRED_SETTINGS = {
        "num_threads": 1,
        "batch_size": 128,
        "cache_size": 0,
    }

    def __init__(self):
        self.bleurt_scorer = BLEURTScorer()

    def __call__(self, batch):
        return self.bert_scorer(batch)
