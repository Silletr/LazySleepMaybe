from os import environ
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()
completion = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
      {
        "role": "user",
        "content": "Xxplain how math.sqrt() works in Python in very simple way"
      }
    ],
    temperature=0.6,
    max_completion_tokens=1024,
    top_p=0.95,
    reasoning_effort="default",
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
