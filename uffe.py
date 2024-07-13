import subprocess
import sys
import os
import json
from pathlib import Path
from urllib.request import Request, urlopen

AGENT_NAME = "Uffe"
LLM = "gpt-4o"
LLM_URL = 'https://api.openai.com/v1/chat/completions'
MEMORY_FILE = Path.home() / f".{AGENT_NAME.lower()}"
TERM_CMD_PREFIX = "$ "
COMMAND_PREFIX = ">>>> C:"
SOURCE_LOCATION = Path(__file__)
INSTALL_DIR = SOURCE_LOCATION.resolve().parent
with open(INSTALL_DIR / "prompts" / "master.txt") as f:
    SYSTEM_PROMPT_MASTER = f.read()
with open(INSTALL_DIR / "prompts" / "memorize.txt") as f:
    SYSTEM_PROMPT_MEMORIZE = f.read()
with open(INSTALL_DIR / ".env", 'r') as file:
    for line in file:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value
with open(SOURCE_LOCATION) as f:
    SOURCE = f.read()

def getenv(key:str, default=0): return type(default)(os.getenv(key, default))

def memorize(conversation: list[dict[str,str]]) -> None:
    mes_history = [{"role":"system", "content":SYSTEM_PROMPT_MEMORIZE.format(memory = recall() or "blank")},
                   {"role":"user", "content":f"This is what happened: {conversation}"}]
    new_memory = chat(mes_history)
    with open(MEMORY_FILE, 'w') as f:
        f.write(new_memory)

def recall() -> str:
    try:
        with open(MEMORY_FILE) as f:
            return f.read()
    except FileNotFoundError:
        return ""

def run_command(command:str)->str:
    if getenv("SAFEMODE", default=1) > 0: 
        if input("run command? [Y/n] ").strip().lower() != 'y':
            return "user aborted command"
    stdout, stderr = subprocess.Popen("bash", stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               text=True, shell=True, encoding="utf-8").communicate(command)
    return stdout or stderr

def chat(mes_history: list[dict[str, str]]) -> str:
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'}
    data = json.dumps({'model': LLM, 'messages': mes_history, 'temperature': 0.0}).encode('utf-8')
    with urlopen(Request(LLM_URL, data=data, headers=headers)) as response:
        response_body = response.read()
    return json.loads(response_body)['choices'][0]['message']['content']

def main()->None:
    if len(sys.argv) < 2:
        print(f"Usage: {AGENT_NAME} <task>")
        exit(1)
    mes_history = [{"role":"system", "content":SYSTEM_PROMPT_MASTER.format(
        source_location=SOURCE_LOCATION, code=SOURCE, memory=recall(), command_prefix=COMMAND_PREFIX)},
                   {"role":"user", "content":' '.join(sys.argv[1:])}]
    while True: 
        msg = chat(mes_history)
        mes_history.append({"role":"system", "content":msg})
        if COMMAND_PREFIX in msg:
            cmd = msg.split(COMMAND_PREFIX)[1].lstrip()
            print(f"{TERM_CMD_PREFIX}{cmd}") 
            cmd_out = run_command(cmd)
            print(f"{cmd_out}")
            mes_history.append({"role":"user", "content":f"{TERM_CMD_PREFIX}{cmd}\n{cmd_out}"})
        elif msg[-1] == "?":
            user_resp = input(f"{msg}\n>> ")
            mes_history.append({"role":"user", "content":user_resp})
        else: 
            comment = msg
            mes_history.append({"role":"user", "content":comment})
            break
    if comment: print(f"{AGENT_NAME}: {comment}")
    print(f"{AGENT_NAME}: Memorizing noteworthy details...")
    memorize(mes_history[1:])

if __name__ == "__main__":
    main()
