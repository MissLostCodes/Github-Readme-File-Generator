from agno.agent import Agent
from agno.models.openai import OpenAILike
from  agno.tools.file import FileTools
from dotenv import load_dotenv
import os

load_dotenv()

MODEL ="moonshotai/kimi-k2"
API_KEY = os.getenv("KIMI_API_KEY")
BASE_URL="https://openrouter.ai/api/v1"

agent = Agent(
    model=OpenAILike(id=MODEL, api_key=API_KEY , base_url=BASE_URL , max_tokens=4000 ),
    tools=[FileTools()],
    description=(
        "You are a technical writer. Clone the repo, scan its structure, "
        "and return a complete README.md (raw markdown only)."
    ),
    markdown=True  # tells the agent to format its answer in markdown
)