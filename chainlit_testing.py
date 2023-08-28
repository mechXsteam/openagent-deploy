import chainlit as ui
from dotenv import load_dotenv

import openagent.compiler as compiler
from openagent import memory
from openagent.compiler._program import Log

load_dotenv()


@ui.on_chat_start
def start_chat():
    compiler.llm = compiler.llms.OpenAI(model="gpt-3.5-turbo")


class ChatLog(Log):
    def append(self, entry):
        super().append(entry)
        print(entry)
        is_end = entry["type"] == "end"
        is_assistant = entry["name"] == "assistant"
        if is_end and is_assistant:
            ui.run_sync(ui.Message(content=entry["new_prefix"]).send())


memory = memory.SimpleMemory()


@ui.on_message
async def main(message: str):
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

    program(user_text=message, log=ChatLog())
