from chainlit.server import app
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import (
    HTMLResponse,
)
from fastapi.responses import JSONResponse

import openagent.compiler as compiler
from openagent import memory
from openagent.compiler._program import Log

load_dotenv()

compiler.llm = compiler.llms.OpenAI(model="gpt-3.5-turbo")


class ChatLog(Log):

    def append(self, entry):
        super().append(entry)
        print(entry)
        is_end = entry["type"] == "end"
        is_assistant = entry["name"] == "assistant"
        print("is end:", is_end)
        print("is_assistant:", is_assistant)
        if is_end:
            # Send the response back to the user
            print("******", entry["new_prefix"])
            return entry["new_prefix"]


memory = memory.SimpleMemory()


# just to test if fastapi responding or not
@app.get("/hello")
def hello(request: Request):
    print(request.headers)
    return HTMLResponse("Hello World")


@app.post("/chat")
async def chat(message: str):
    program = compiler(
        """
        {{#system~}}
        You are a helpful assistant
        {{~/system}}

        {{~#geneach 'conversation' stop=False}}
        {{#user~}}
        {{set 'this.user_text' (await 'user_text')  hidden=False}}
        {{~/user}}

        {{#assistant~}}
        {{gen 'this.ai_text' temperature=0 max_tokens=300}}
        {{~/assistant}}
        {{~/geneach}}""", memory=memory
    )

    # Run the program with the user message and log
    result = program(user_text=message, log=ChatLog())
    print('result****************:', result)
    return JSONResponse(content={"response": f"{result}"})
