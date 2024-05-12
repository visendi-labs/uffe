import subprocess
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

AGENT_NAME = "Uffe"
TERM_CMD_PREFIX = "$ "
QUESTION_PREFIX = ">>>> Q:" 
COMMAND_PREFIX = ">>>> C:"
DONE_PREFIX = ">>>> D:"
SYSTEM_PROMPT = f"""
You are a system engineer with a specific goal. All you have access to is the terminal of a Linux machine. 

You are only allowed to do three things:

1. Ask question to your master. Do this by writing "{QUESTION_PREFIX} <your question>". 
Do not ask questions unless you really have to. Remember to always use this if you want
a response, even if you just ask if you are done.

2. Send a command to the command line. Do this by writing. "{COMMAND_PREFIX} <command>". 
Whatever the output is will be returned to you. Your terminal will keep its state 
between your messages so you can navigate around to see what's on the server.

Your master may or may not give you a lot of context. Feel free to navigate around
and see what kind of environment you are dealing with. If you are given a task
to fix something in a project, have a look around to see what kind of stuff is 
in there.

3. When you are done you simply write "{DONE_PREFIX} <super short description what you did".

It's important that you do not do things that I have not asked for without asking first.
Also very important, check that whatevery you did was correct. If you changed a file, make
sure it was changed correctly.
"""

def run_command(command:str)->tuple[str,str]:
    process = subprocess.Popen("bash", stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               text=True, shell=True)
    return process.communicate(command)

def fetch_content(content_prefix:str, response:str)->str:
    return response.split(content_prefix)[1].split("\n")[0].lstrip()

def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print(f"Usage: {AGENT_NAME} <task>\n{sys.argv}")
        exit()

    mes_history = [SystemMessage(content=SYSTEM_PROMPT),
                   HumanMessage(content=sys.argv[1])]
    model = "gpt-4-turbo-2024-04-09"
    chat = ChatOpenAI(model=model)
    done = False
    while not done:
        res = chat.invoke(mes_history)
        mes_history.append(res)

        if COMMAND_PREFIX in res.content:
            cmd = fetch_content(COMMAND_PREFIX, res.content)
            print(f"{TERM_CMD_PREFIX}{cmd}") 
            std_out, std_err = run_command(cmd)
            print(f"{std_err or std_out}")
            mes_history.append(HumanMessage(content=f"$ {cmd} {std_out or std_err}"))

        elif DONE_PREFIX in res.content:
            comment = fetch_content(DONE_PREFIX, res.content)
            done=True

        elif QUESTION_PREFIX in res.content:
            q = fetch_content(QUESTION_PREFIX, res.content)
            user_resp = input(q)
            mes_history.append(HumanMessage(content=user_resp))

        else: 
            comment = res.content
            done=True
    print(f"{AGENT_NAME}: {comment or ''}")

if __name__ == "__main__":
    main()
