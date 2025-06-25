import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from .session import db as db_instance
from .models import Event, Image


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


def fetch_events_without_image_path(website_name: str):
    """
    Retrieve all events for a website where the associated image has no image_path.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .join(Event.image)
            .options(joinedload(Event.image))
            .filter(Event.website_name == website_name)
            .filter(Image.image_path == None)  # noqa: E711
            .order_by(Event.id)
            .all()
        )

def fetch_events_with_web_content(website_name: str):
    """
    Retrieve all events for a given website that already have non-empty web content.

    Args:
        website_name (str): The name of the website to filter events by.

    Returns:
        List[Event]: A list of Event objects with non-null web_content.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .filter_by(website_name=website_name)
            .filter(Event.web_content.isnot(None))
            .order_by(Event.id)
            .all()
        )


def fetch_events_with_non_generated_content(website_name: str):
    """
    Retrieve events for a given website that:
    - have non-null web content, and
    - the content was not auto-generated (i.e., generated_content is False)

    Args:
        website_name (str): The name of the website to filter events by.

    Returns:
        List[Event]: Events with manually written or verified web content.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .options(joinedload(Event.image))  # Eager load the image relationship
            .filter_by(website_name=website_name)
            .filter(
                (Event.generated_content.is_(False)) &
                (Event.web_content.isnot(None))
            )
            .order_by(Event.id)
            .all()
        )
