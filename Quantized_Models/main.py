from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # dummy, required by SDK but ignored by Ollama
    max_retries=3, timeout=120
)

response = client.chat.completions.create(
    model="gemma2:2b-instruct-q4_0",
    messages=[
        {"role": "user", "content": "Who is Hillary Arinda?"}
    ],
)

print(response.choices[0].message.content)