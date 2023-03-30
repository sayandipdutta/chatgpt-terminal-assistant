# chatgpt-terminal-assistant
OpenAI's ChatGPT as a terminal assistant.

* Note: Under active development, expect breaking changes.

# Usage
1. Clone the repo
2. Install the requirements `pip install -r requirements.txt`
3. [Get api key from your openai account](https://platform.openai.com/docs/api-reference/authentication).
4. Set `OPENAI_API_KEY` environment variable: `export OPENAI_API_KEY=your-api-key-here`
5. Run the program from the directory where you cloned the repo, `python assistant.py`.

*Note: This program uses OpenAI ChatCompletion API. Check out the [pricing](https://openai.com/pricing) at their website. 
At the time of writing this, 'gpt-3.5-turbo' costs `$0.002 for every 1000 tokens`.

# Screenshot
![Screenshot](/media/assistant.png)
