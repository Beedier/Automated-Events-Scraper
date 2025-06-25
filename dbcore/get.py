import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from .session import db as db_instance
from .models import Event


logger = logging.getLogger(__name__)

def fetch_events_without_web_content(website_name: str) -> list[Event]:
    """
    Retrieve events from a specific website with no web_content.

    Args:
        website_name (str): Website name to filter events.

    Returns:
        list[Event]: List of matching Event instances.
    """
    try:
        with db_instance.session_scope() as session:
            return (
                session.query(Event)
                .filter_by(website_name=website_name)
                .filter(Event.web_content.is_(None))
                .order_by(Event.id)
                .all()
            )
    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to fetch events without web_content (ID: {err_id})")
        return []


def fetch_events_by_website(website_name: str) -> list[Event]:
    """
    Retrieve all events for a specific website, ordered by event ID.

    Args:
        website_name (str): Website name to filter events.

    Returns:
        list[Event]: Matching Event instances.
    """
    try:
        with db_instance.session_scope() as session:
            return (
                session.query(Event)
                .filter_by(website_name=website_name)
                .order_by(Event.id)
                .all()
            )
    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to fetch events for website '{website_name}' (ID: {err_id})")
        return []
