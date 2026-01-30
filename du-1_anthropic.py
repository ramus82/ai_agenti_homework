import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "tell me a joke"}
    ],
)
print("--- Full response: ---")
print(response)
print("--- Response content: ---")
print(response.content[0].text)
