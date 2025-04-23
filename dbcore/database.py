from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base


class Database:
    """Database manager for SQLAlchemy Base, engine and session."""

    def __init__(self, db_url: str):
        self.engine = create_engine(url=db_url, echo=False)
        self.Base = declarative_base()
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False, expire_on_commit=False)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_tables(self):
        self.Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of database operations.

        This context manager automatically:
        - opens a new session,
        - commits the transaction if everything succeeds,
        - rolls back if any exception occurs,
        - and finally closes the session.

        Yields:
            session (Session): SQLAlchemy session object for DB operations.
        """
        session = self.get_session()
        try:
            # Yield the session to the block using this context
            yield session
            # Commit the transaction if no exception occurs
            session.commit()
        except:
            # Rollback on any exception to avoid corrupt state
            session.rollback()
            raise
        finally:
            # Always close the session after use
            session.close()
