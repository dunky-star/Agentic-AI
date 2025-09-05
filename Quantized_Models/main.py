from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy, required by SDK but ignored by Ollama
)

response = client.chat.completions.create(
    model="gemma2:2b-instruct-q4_0",
    messages=[
        {"role": "user", "content": "Hello Ollama from OpenAI client!"}
    ],
)

print(response.choices[0].message.content)