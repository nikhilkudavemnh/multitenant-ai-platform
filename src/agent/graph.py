from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain.agents import create_agent
from psycopg import AsyncConnection

from src.agent.tools import http_request, web_search
from src.core.setting import settings
from langchain.chat_models import init_chat_model

PG_CONN_STRING = (
    f"postgresql://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

AGENT_CACHE = {}


async def get_agent(schema: str):

    if schema in AGENT_CACHE:
        return AGENT_CACHE[schema]["agent"]

    conn = await AsyncConnection.connect(
        PG_CONN_STRING,
        autocommit=True,
        options=f"-c search_path={schema}"
    )

    checkpointer = AsyncPostgresSaver(conn)

    model = init_chat_model("google_genai:gemini-2.5-flash-lite")

    agent = create_agent(
        model,
        [web_search, http_request],
        checkpointer=checkpointer
    )

    AGENT_CACHE[schema] = {
        "agent": agent,
        "conn": conn,
        "checkpointer": checkpointer,
    }

    return agent