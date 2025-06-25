import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from .session import db as db_instance
from .models import Event, PublishStatusEnum


logger = logging.getLogger(__name__)

def set_event_web_content(event_id: int, web_content: str, generated_content: bool = False) -> bool:
    """
    Update web_content and generated_content of the Event by event_id.

    Args:
        event_id (int): ID of the event to update.
        web_content (str): New content to store.
        generated_content (bool): Flag indicating if the content was generated.

    Returns:
        bool: True if update succeeded, False otherwise.
    """
    try:
        with db_instance.session_scope() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                logger.warning(f"Event not found with ID: {event_id}")
                return False

            event.web_content = web_content
            event.generated_content = generated_content
            session.add(event)

            logger.info(f"Event web content updated. ID: {event.id}")
            return True

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to update event web content (ID: {err_id})")
        return False


def set_processed_image_path(event_id: int, image_path: str) -> bool:
    """
    Set or update the `image_path` of the image associated with a specific event.

    Args:
        event_id (int): ID of the event whose image record needs to be updated.
        image_path (str): Absolute or relative path to the processed image file.

    Returns:
        bool: True if the update succeeds, False if event/image not found or on DB error.
    """
    try:
        with db_instance.session_scope() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event or not event.image:
                logger.warning(f"Event or associated image not found. Event ID: {event_id}")
                return False

            event.image.image_path = image_path  # ✅ Corrected field
            session.add(event.image)

            logger.info(
                f"Updated image path. Event ID: {event.id}, Image ID: {event.image.id}, Path: {event.image.image_path}"
            )
            return True

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to update image path for Event ID {event_id} (Error ID: {err_id})")
        return False


def set_event_generated_content(
    event_id: int,
    category: str = None,
    title: str = None,
    index_intro: str = None,
    intro: str = None,
    content: str = None,
    dates: str = None,
    date_order: str = None,
    location: str = None,
    cost: str = None,
    generated_content: bool = True,
    publish_status: PublishStatusEnum = PublishStatusEnum.unsynced
) -> bool:
    """
    Set all content-related fields of an event, even if values are None.

    Args:
        event_id (int): ID of the event to update.
        category (str): Category label.
        title (str): Title of the event.
        index_intro (str): Short intro for indexing.
        intro (str): Full intro paragraph.
        content (str): Main event content.
        dates (str): Human-readable date range.
        date_order (str): Sortable final date in YYYYMMDD.
        location (str): Event location.
        cost (str): Event cost.
        generated_content (bool): Whether the content is AI-generated.
        publish_status (PublishStatusEnum): Current publishing status.

    Returns:
        bool: True if update succeeds, False if event not found or on DB error.
    """
    try:
        with db_instance.session_scope() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                logger.warning(f"Event not found. Event ID: {event_id}")
                return False

            # Assign all values, even if None
            event.category = category
            event.title = title
            event.index_intro = index_intro
            event.intro = intro
            event.content = content
            event.dates = dates
            event.date_order = date_order
            event.location = location
            event.cost = cost
            event.generated_content = generated_content
            event.publish_status = publish_status

            session.add(event)
            logger.info(f"Event updated. ID: {event.id}, Generated: {generated_content}")
            return True

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to update event content for Event ID {event_id} (Error ID: {err_id})")
        return False
