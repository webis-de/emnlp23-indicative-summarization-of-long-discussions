FROM python:3.9-slim
ENV PRODUCTION=true
RUN pip install fastapi uvicorn python-dotenv
WORKDIR /app
COPY . .

CMD python api.py
