from ollama import Client
from pprint import pprint

client = Client(host="http://localhost:11434")



messages = [
    {"role": "user", "content": "Tell me a joke."}
]

response = client.chat(
    model="llama3.2",
    messages = messages
)

print("--- Full response: ---")
pprint(response)