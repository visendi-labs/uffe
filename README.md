Uffe is...
* a **sub-100 lines** LLM agent. 
* fitted with **long term memory**.
* **self-conscious** in the sense that all the code in uffe.py is injected into the system prompt.
* going to **use your terminal**. Whatever you have access to, uffe has access to.
* a real doer, he will probably not ask for permission, he just gets things done.
* completely independent. You can run uffe.py on vanilla python.

https://github.com/visendi-labs/uffe/assets/7818582/c877882d-cde0-490f-bcdc-fb54b30451d9

### How to install ⚙️

1. Clone this repository.
2. Ensure you have a `.env` containing OPENAI_API_KEY.
3. `$ python uffe.py`
4. *Optional*: Make an alias 'uffe' pointing to 'python /path/to/uffe.py' 

### Disclaimer ⚠️ 

Goes without saying but although this repository is completely open source and free, OpenAI will charge you money for using their LLM. 
There is no limit of how much tokens uffe will use, it can very well get stuck in an infinite loop and drain your OpenAI account.

Use with caution, this agent can (and probably will) do unexpected things using your computer. It has access to whatever you have access to. 
Use with caution. We do not take responsibility for any damages caused by using this.

### TODO 📝
- Improve memory
