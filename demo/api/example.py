import os

os.environ["CLIENT_ID"] = "<your-client-id>"
os.environ["CLIENT_SECRET"] = "<your-client-secret>"
OPENAI_API_KEY = (
    "<your-openai-api-key>"  # set this to None if you want only the clustering
)
URL = "https://www.reddit.com/ynqtgx"

from pipeline import Pipeline

OPENAI_API_KEY = None

if OPENAI_API_KEY:
    model = "gpt-3.5-turbo"
    api_key = OPENAI_API_KEY
else:
    model = None
    api_key = None

pipeline = Pipeline()

result = pipeline(url=URL, model=model, api_key=api_key)

# result["root"] contains the discussion in a tree format
# result["result"] is a dictionary
#   - each key is the identifier of a comment in the dicussion.
#   - the value is a list of cluster information about each sentence in the comment in order where for an element e:
#     - e["cluster"]["trueValue"] is the cluster id assigned by hdbscan
#     - e["x"] and e["y"] are the coordinates for visualization
# result["labels"] and result["frames"] contain the labels and frames for each cluster if a model was provided
