import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.core.setting import settings

PG_CONN_STRING = (
    f"postgresql://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


async def setup_langgraph_table(schemas: list[str]):
    for schema in schemas:
        async with await psycopg.AsyncConnection.connect(
            PG_CONN_STRING,
            autocommit=True,
            options=f"-c search_path={schema}"
        ) as conn:
            checkpointer = AsyncPostgresSaver(conn)
            await checkpointer.setup()

            print(f"LangGraph tables created in {schema}")