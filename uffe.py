import subprocess
import sys
from dotenv import load_dotenv
from openai import OpenAI

AGENT_NAME = "Uffe"
LLM = "gpt-4"
TERM_CMD_PREFIX = "$ "
COMMAND_PREFIX = ">>>> C:"
SYSTEM_PROMPT = f"""You are a system engineer with a specific task. 
All you have access to is a linux-like terminal. 
You are only allowed to do two things:

1. Ask question to your master. Do not ask questions unless you really have to. 
Remember to always use this if you want a response, even if you just ask if you are done.

2. Send a command to the command line. Do this by writing. "{COMMAND_PREFIX} <command>". 
Whatever the output is will be returned to you. Your terminal will keep its state 
between your messages so you can navigate around to see what's on the server.
You (the program), can be called from anywhere in the OS, not necessarily "/" or "~"
so make sure you are in the right directory before starting to execute commands.

Your master may or may not give you a lot of context. Feel free to navigate around
and see what kind of environment you are dealing with. If you are given a task
to fix something in a project, have a look around to see what kind of stuff is 
in there.

It's important that you do not do things that I have not asked for without asking first.
Also very important, check that whatevery you did was correct. If you changed a file, make
sure it was changed correctly."""

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
        print(f"Usage: {AGENT_NAME} <task>")
        exit(1)
    client = OpenAI()
    mes_history = [{"role":"system", "content":SYSTEM_PROMPT},
                   {"role":"user", "content":sys.argv[1]}]
    while True: 
        res = client.chat.completions.create(model=LLM, messages=mes_history, temperature=0.0)
        msg = res.choices[0].message.content
        assert msg is not None
        mes_history.append({"role":"system", "content":msg})
        if COMMAND_PREFIX in msg:
            cmd = fetch_content(COMMAND_PREFIX, msg)
            print(f"{TERM_CMD_PREFIX}{cmd}") 
            std_out, std_err = run_command(cmd)
            print(f"{std_err or std_out}")
            mes_history.append({"role":"system", "content":f"$ {cmd} {std_out or std_err}"})
        elif msg[-1] == "?":
            user_resp = input(f"{msg}\n>> ")
            mes_history.append({"role":"system", "content":user_resp})
        else: 
            comment = msg
            break
    print(f"{AGENT_NAME}: {comment or ''}")

if __name__ == "__main__":
    main()
