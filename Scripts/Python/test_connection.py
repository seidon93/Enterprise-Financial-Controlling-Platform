from sqlalchemy import text

from common.database import engine

with engine.connect() as connection:

    version = connection.execute(
        text("SELECT version();")
    ).scalar()

    print(version)