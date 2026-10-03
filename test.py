
from ollama import chat

def ask_bot(prompt):

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

while True:

    question = input("You: ")

    if question == "quit":
        break

    answer = ask_bot(question)

    print("Bot:", answer)