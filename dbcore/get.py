import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from .session import db as db_instance
from .models import Event, Image, Category, PublishStatusEnum


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
            .order_by(Image.id)
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
            .order_by(Image.id)
            .distinct()
            .all()
        )


def fetch_events_without_remote_event_id(website_name: str) -> list[Event]:
    """
    Get distinct events of a website where remote_event_id is missing.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .join(Event.image)
            .options(joinedload(Event.image))
            .filter(
                Event.website_name == website_name,
                Event.remote_event_id.is_(None),  # ✅ missing condition added
                Event.generated_content.is_(True),
                Event.title.isnot(None),
                Event.intro.isnot(None),
                Event.index_intro.isnot(None),
                Event.content.isnot(None),
                Image.remote_media_id.isnot(None),
                Event.location.isnot(None),
                Event.dates.isnot(None),
                Event.date_order.isnot(None),
                Event.cost.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )

def fetch_events_with_remote_event_id_and_categories(website_name: str) -> list[Event]:
    """Fetch events with remote_event_id and at least one category with remote_category_id, eagerly loading categories, ordered by Event.id."""
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .options(joinedload(Event.categories))
            .join(Event.categories)
            .filter(
                Event.website_name == website_name,
                Event.remote_event_id.isnot(None),
                Category.remote_category_id.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )


def fetch_ready_events_for_publishing(website_name: str) -> list[Event]:
    """
    Fetch events that are fully prepared and eligible for publishing:
    - Belong to the specified website
    - Have already been synced (remote_event_id is set)
    - Are marked as generated_content
    - Are not yet published (publish_status = unsynced)
    - Contain all required content fields
    - Have an associated image with a remote_media_id

    Args:
        website_name (str): Website name to filter events.

    Returns:
        list[Event]: Events ready to be published.
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .options(joinedload(Event.image))  # Eager load image relationship
            .join(Event.image)  # Join for filtering on Image
            .filter(
                Event.website_name == website_name,
                Event.publish_status == PublishStatusEnum.unsynced,

                Event.remote_event_id.isnot(None),
                Event.generated_content.is_(True),

                # Required fields
                Event.title.isnot(None),
                Event.intro.isnot(None),
                Event.index_intro.isnot(None),
                Event.content.isnot(None),
                Image.remote_media_id.isnot(None),
                Event.location.isnot(None),
                Event.dates.isnot(None),
                Event.date_order.isnot(None),
                Event.cost.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )


def fetch_events_delete_from_wordpress(website_name: str) -> list[Event]:
    with db_instance.session_scope() as session:
        return (
            session.query(Event)
            .filter(
                Event.website_name == website_name,
                Event.remote_event_id.isnot(None)
            )
            .order_by(Event.id)
            .all()
        )


def fetch_images_delete_from_wordpress(website_name: str) -> list[Event]:
    with db_instance.session_scope() as session:
        return (
            session.query(Image)
            .join(Image.events)
            .filter(
                Event.website_name == website_name,
                Image.remote_media_id.isnot(None)
            )
            .order_by(Image.id)
            .all()
        )
