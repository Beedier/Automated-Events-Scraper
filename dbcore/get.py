import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from .session import db as db_instance
from .models import Event, Image


logger = logging.getLogger(__name__)

def fetch_events_without_web_content(website_name: str) -> list[Event]:
    """
    Fetch events from the specified website that have no web content
    but have an associated image with a valid image path.

    Args:
        website_name (str): Name of the website to filter events by.

    Returns:
        list[Event]: A list of Event objects matching the criteria.
    """
    try:
        with db_instance.session_scope() as session:
            return (
                session.query(Event)
                .join(Event.image)
                .filter(
                    Event.website_name == website_name,
                    Event.web_content.is_(None),
                    Image.image_path.isnot(None)
                )
                .order_by(Event.id)
                .all()
            )
    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to fetch events without web_content (ID: {err_id})")
        return []


def fetch_events_by_website(website_name: str) -> list[Event]:
    """
    Fetch all events for the specified website that have an associated image
    with a valid image path, ordered by event ID.

    Args:
        website_name (str): Name of the website to filter events by.

    Returns:
        list[Event]: A list of Event objects matching the criteria.
    """
    try:
        with db_instance.session_scope() as session:
            return (
                session.query(Event)
                .join(Event.image)
                .options(joinedload(Event.image))
                .filter(
                    Event.website_name == website_name,
                    Image.image_path.isnot(None)
                )
                .order_by(Event.id)
                .all()
            )
    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to fetch events for website '{website_name}' (ID: {err_id})")
        return []


def fetch_images_without_image_path(website_name: str) -> list[Image]:
    """
    Retrieve unique images used by events from a given website
    where the image_path is missing (None).

    Args:
        website_name (str): The website name to filter associated events.

    Returns:
        list[Image]: List of unique Image objects with no image_path.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Image)
            .join(Image.events)
            .filter(
                Event.website_name == website_name,
                Image.image_path.is_(None)
            )
            .distinct()
            .all()
        )


def fetch_events_with_web_content(website_name: str) -> list[Event]:
    """
    Retrieve all events for a given website that already have non-empty web content.

    Args:
        website_name (str): The name of the website to filter events by.

    Returns:
        list[Event]: A list of Event objects with non-null web_content.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .filter(
                Event.website_name == website_name,
                Event.web_content.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )


def fetch_events_with_non_generated_content(website_name: str) -> list[Event]:
    """
    Retrieve events for a given website that:
    - have non-null web content, and
    - the content was not auto-generated (i.e., generated_content is False)

    Args:
        website_name (str): The name of the website to filter events by.

    Returns:
        list[Event]: Events with manually written or verified web content.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .options(joinedload(Event.image))  # Eager load the image relationship
            .filter(
                Event.website_name == website_name,
                Event.generated_content.is_(False),
                Event.web_content.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )


def fetch_images_without_remote_media_id(website_name: str) -> list[Image]:
    """
    Get distinct images used by events of a website where remote_media_id is missing.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Image)
            .join(Image.events)
            .filter(
                Event.website_name == website_name,
                Event.generated_content.is_(True),
                Image.remote_media_id.is_(None)
            )
            .distinct()
            .all()
        )
