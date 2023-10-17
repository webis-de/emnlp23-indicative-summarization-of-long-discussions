# Demo

You can access a deployment of the demo via: [https://discussion-explorer.web.webis.de](https://discussion-explorer.web.webis.de)  

## Run Locally
To use the demo locally, you need docker-compose.
Go to the demo folder and run `docker-compose up`.

If you want to apply the approach to new discussions, create an `.env` file in the `demo` folder with the following content and run `docker-compose up`:

```bash
CLIENT_ID=<client-id>
CLIENT_SECRET=<client-secret>
```

Replace `<client-id>` and `<client-secret>` with the values obtained by creating an Reddit app: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

# Pipeline

If you are interested in using the pipeline in your own code or you want to modify this approach, see the `demo/api/example.py` file.
It shows an example for using the pipeline with python.
Make sure to install all dependencies from `demo/api/Pipfile.lock`.
You can generate a requirements file by running `pipenv requirements > requirements.txt` in the `demo/api` folder.

# Evaluation

## Cluster Label Generation

The `evaluation/label_generation` folder contains files for setting the evaluation up and showing evaluation results.
It also contains the annotation interface used for the human evaluation.
Run `./human_evaluation.py` in this folder to obtain the results from our human evaluation.
Note that all value have already been pre-computed and are stored in the `data` folder.

Use `./evaluate.py` to obtain the results from automatic evaluation.
The values for this evaluation were computed using the `llm_experiment.py` script.
We deployed the language models on our custom infrastructure using the code in the `language_models/server/` folder.
Therefore the `llm_experiment.py` script does not work without deploying the language models on some capable server and supplying information about the service to the script.

## Media Frame Assignment

The `evaluation/media_frames` folder contains files for setting the evaluation up and showing evaluation results.
Use `./step_4_evaluate.py` to obtain the results.
The `step_3_generate_media_frames.py` file was used to assign the frames but does not work without deploying the language models on some capable server and supplying information about the service to the script.
The `step_1_generate_data.py` script was used to generate the initial dataset the we annotated manually using google docs and the `step_2_extract_annotations.py` script was used to combine the annotated documents into one evaluation dataset.
The `data` folder contains all data files that were generated in this evaluation.
