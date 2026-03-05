from ollama import Client
from pprint import pprint

client = Client(host="http://localhost:11434")

response = client.embed(
    model="llama3.2",
    input="Tell me a joke.",
)

print("--- Full response: ---")
pprint(response)