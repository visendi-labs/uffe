import subprocess
import sys
import os
from openai import OpenAI
from pathlib import Path

AGENT_NAME = "Uffe"
LLM = "gpt-4o"
MEMORY_FILE = Path.home() / f".{AGENT_NAME.lower()}"
TERM_CMD_PREFIX = "$ "
COMMAND_PREFIX = ">>>> C:"
INSTALL_DIR = Path(__file__).resolve().parent
SOURCE_LOCATION = INSTALL_DIR / "uffe.py"
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

def memorize(conversation: list[dict[str,str]]) -> None:
    mes_history = [{"role":"system", "content":SYSTEM_PROMPT_MEMORIZE.format(memory = recall() or "blank")},
                   {"role":"user", "content": f"This is what happened: {conversation}"}]
    new_memory = OpenAI().chat.completions.create(model=LLM, messages=mes_history, temperature=0.0).choices[0].message.content # type: ignore
    assert new_memory is not None
    with open(MEMORY_FILE, 'w') as f:
        f.write(new_memory)

def recall() -> str:
    try:
        with open(MEMORY_FILE) as f:
            return f.read()
    except FileNotFoundError:
        return ""

def run_command(command:str)->tuple[str,str]:
    process = subprocess.Popen("bash", stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               text=True, shell=True)
    return process.communicate(command)

def fetch_content(content_prefix:str, response:str)->str:
    return response.split(content_prefix)[1].split("\n")[0].lstrip()

def main()->None:
    if len(sys.argv) < 2:
        print(f"Usage: {AGENT_NAME} <task>")
        exit(1)
    mes_history = [{"role":"system", "content":SYSTEM_PROMPT_MASTER.format(
        source_location=SOURCE_LOCATION, code=SOURCE, memory=recall(), command_prefix=COMMAND_PREFIX)},
                   {"role":"user", "content":' '.join(sys.argv[1:])}]

    while True: 
        res = OpenAI().chat.completions.create(model=LLM, messages=mes_history, temperature=0.0) # type: ignore
        msg = res.choices[0].message.content
        assert msg is not None
        mes_history.append({"role":"system", "content":msg})
        if COMMAND_PREFIX in msg:
            cmd = fetch_content(COMMAND_PREFIX, msg)
            print(f"{TERM_CMD_PREFIX}{cmd}") 
            std_out, std_err = run_command(cmd)
            print(f"{std_err or std_out}")
            mes_history.append({"role":"user", "content":f"$ {cmd} {std_out or std_err}"})
        elif msg[-1] == "?":
            user_resp = input(f"{msg}\n>> ")
            mes_history.append({"role":"user", "content":user_resp})
        else: 
            comment = msg
            mes_history.append({"role":"user", "content": comment})
            break
    print(f"{AGENT_NAME}: {comment or ''}")
    print(f"{AGENT_NAME}: Memorizing noteworthy details...")
    memorize(mes_history[1:])

if __name__ == "__main__":
    main()
