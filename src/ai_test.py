"""Quick check that the Groq API key works."""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

reply = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Explain what a pit stop is in one sentence."}],
)
print(reply.choices[0].message.content)