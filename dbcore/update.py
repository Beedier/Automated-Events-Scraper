import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from .session import db as db_instance
from .models import Event, PublishStatusEnum, Category, Image


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


def set_processed_image_path(image_id: int, image_path: str) -> bool:
    """
    Set or update the image_path of the image with the given ID.

    Args:
        image_id (int): ID of the image to update.
        image_path (str): New path to the processed image file.

    Returns:
        bool: True if updated, False if not found or on DB error.
    """
    try:
        with db_instance.session_scope() as session:
            image = session.query(Image).filter_by(id=image_id).first()
            if not image:
                return False
            image.image_path = image_path
            session.flush()
            return True
    except SQLAlchemyError:
        return False


def set_remote_media_id(image_id: int, remote_media_id: int) -> bool:
    """
    Set remote_media_id for the given image if not already set.

    Args:
        image_id (int): ID of the image.
        remote_media_id (int): Remote media ID to assign.

    Returns:
        bool: True if updated, False if already set or on error.
    """
    try:
        with db_instance.session_scope() as session:
            image = session.query(Image).filter_by(id=image_id).first()
            if not image:
                return False
            if image.remote_media_id is not None:
                return False
            image.remote_media_id = remote_media_id
            session.flush()
            return True
    except SQLAlchemyError:
        return False


def set_remote_event_id(event_id: int, remote_event_id: int) -> bool:
    """
    Set remote_event_id for the given event if not already set.

    Args:
        event_id (int): ID of the event.
        remote_event_id (int): Remote event ID to assign.

    Returns:
        bool: True if updated, False if already set or on error.
    """
    try:
        with db_instance.session_scope() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                return False
            if event.remote_event_id is not None:
                return False
            event.remote_event_id = remote_event_id
            session.flush()
            return True
    except SQLAlchemyError:
        return False


def set_event_generated_content(
    event_id: int,
    category_names: list[str] = None,
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
    Update all content-related fields of an event, including category assignment.

    Args:
        event_id (int): ID of the event to update.
        category_names (list[str], optional): List of existing category names to assign. Skips any not found.
        title (str, optional): Title of the event.
        index_intro (str, optional): Short introduction for indexing.
        intro (str, optional): Full introduction paragraph.
        content (str, optional): Main event content.
        dates (str, optional): Human-readable date or date range.
        date_order (str, optional): Sortable date string in YYYYMMDD format.
        location (str, optional): Location of the event.
        cost (str, optional): Cost of attending the event.
        generated_content (bool, optional): Flag indicating whether content was AI-generated. Defaults to True.
        publish_status (PublishStatusEnum, optional): Current publishing status. Defaults to 'unsynced'.

    Returns:
        bool: True if the update succeeds, False if event is not found or a database error occurs.
    """

    try:
        with db_instance.session_scope() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                logger.warning(f"Event not found. Event ID: {event_id}")
                return False

            # Assign all values, even if None
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

            # Handle category assignment (skip missing)
            if category_names is not None:
                updated_categories = []
                for name in category_names:
                    category = session.query(Category).filter_by(name=name).first()
                    if category:
                        updated_categories.append(category)
                    else:
                        logger.warning(f"Category '{name}' not found. Skipping.")
                event.categories = updated_categories

            session.add(event)
            logger.info(f"Event updated. ID: {event.id}, Generated: {generated_content}")
            return True

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Failed to update event content for Event ID {event_id} (Error ID: {err_id})")
        return False
