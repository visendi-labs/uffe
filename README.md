## Uffe

This is a sub-100 lines LLM agent with a long term memory that can actually perform
tasks. Uffe is a real doer, he doesn't ask for permission he just gets shit
done. The only tool he has access to is your terminal.

Uffe currently only has 1 dependency: [openai](https://pypi.org/project/openai/)

https://github.com/visendi-labs/uffe/assets/7818582/c877882d-cde0-490f-bcdc-fb54b30451d9

### How to Use

1. Clone this repository.
2. Ensure you have a `.env` containing OPENAI_API_KEY.
3. Install dependencies `$ pip install -r requirement.txt`
4. Run the script.

### ⚠️ Disclaimer ⚠️

Goes without saying but it will cost you money to run this agent. There is no
limit of how much, it can very well get stuck in an infinity loop and drain
your OpenAI account.

Use with caution, this agent can (and probably will) do unexpected things using
your computer. It has access to whatever you have access to. Use with caution.
We do not take responsibility for any damages caused by using this.
