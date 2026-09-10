from pathlib import Path

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Model(DeclarativeBase):
    metadata = MetaData(naming_convention={
        'ix': 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent

db_file_name = 'db.sqlite'
db_file_path = PROJECT_DIR / 'db.sqlite'

DATABASE_URL = f'sqlite:///{db_file_path}'

engine = create_engine(
    url=DATABASE_URL,
    echo=False,
)

SessionMaker = sessionmaker(engine)


from models import TaskRun

if not db_file_path.exists():
    Model.metadata.create_all(engine)