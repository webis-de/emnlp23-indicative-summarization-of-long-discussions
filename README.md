To use the demo locally, you need docker-compose.
Go to the demo folder and run `docker-compose up`.

If you want to apply the approach to new discussions, create an `.env` file in the `demo` folder with the following content and run `docker-compose up`:

```bash
CLIENT_ID=<client-id>
CLIENT_SECRET=<client-secret>
```

Replace `<client-id>` and `<client-secret>` with the values obtained by creating an Reddit app: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

If you are interested in using the pipeline in your own code or you want to modify this approach, see the `demo/api/example.py` file.
It shows an example for using the pipeline with python.
Make sure to install all dependencies from `demo/api/Pipfile.lock`.
You can generate a requirements file by running `pipenv requirements > requirements.txt` in the `demo/api` folder.
