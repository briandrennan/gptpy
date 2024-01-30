import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the model name from the environment variable or use the current value as a constant
MODEL = os.getenv("GPTPY_MODEL_NAME") or "gpt-4-1106-preview"

# Get the API key from the environment variable
API_KEY = os.getenv("GPTPY_OPENAI_API_KEY")

# Create the OpenAI client
client = OpenAI(api_key=API_KEY)

CONTENT = (
    os.getenv("GPTPY_SYSTEM_PROMPT")
    or "You are a helpful assistant. The maximum length of a response should be 120 characters in width."
)

messages = [{"role": "system", "content": CONTENT}]
usage = None

while True:
    req = input("Question: ")

    if req in ["", "done", "exit", "/done", "/exit"]:
        break
    elif req == "/spill":
        print(messages)
    elif req == "/dump":
        messages = messages[0:1]
        usage = None
        print("Message context reset.")
    elif req.startswith("/drop"):
        for arg in req.split(" "):
            if arg == "/drop":
                continue
            try:
                index = int(arg)
                if index >= 0 and index < len(messages):
                    messages.pop(index)
                    print(messages)
            except ValueError:
                print(
                    "Error: Unrecognized spill token",
                    arg,
                    "The value must be an integer.",
                )
                break

        usage = None
    elif req.startswith("/save") and len(messages) > 1:
        if len(req) > 7:
            file_name = req[6:]
        else:
            file_name = "chat-output.md"

        print(f'Saving to the file "{file_name}"')
        with open(file_name, "w") as file:
            for msg in messages:
                role = msg["role"]
                text = msg["content"]
                file.write(f"Role=**{str.upper(role)}**\n---\n")
                file.write(text)
                file.write("\n---\n")

            if usage != None:
                file.write(
                    f"\n`(token info: prompts={response.usage.prompt_tokens}, completions={response.usage.completion_tokens}, total={response.usage.total_tokens})`\n"
                )
    elif req.startswith("/load"):
        try:
            path = req[len("/load") :].lstrip()
            with open(path) as file:
                text = file.read()
                content = f"<file_name>{path}</file_name>\n<|im_start|>{text}<|im_end|>"
                messages.append({"role": "user", "content": content})
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("\n---\n")
        messages.append({"role": "user", "content": req})
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.1
        )
        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        print(response.choices[0].message.content)
        usage = response.usage
        print(
            f"\n(token info: prompts={response.usage.prompt_tokens}; completions={response.usage.completion_tokens}; total={response.usage.total_tokens})\n"
        )
        print()
