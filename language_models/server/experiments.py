import requests

i = 1

while True:
    print(i)
    requests.post("http://localhost:5000", json={"batch": ["test"]})
    i += 1


from transformers import AutoTokenizer

model = "tiiuae/falcon-40b"

tokenizer = AutoTokenizer.from_pretrained(model)
