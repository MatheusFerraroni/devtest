from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy import create_engine, event
from sqlalchemy import text

engine = create_engine('sqlite:///elevator.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)
