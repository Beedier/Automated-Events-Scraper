import logging
from .create import _error_id
from sqlalchemy.exc import SQLAlchemyError
from .session import db as db_instance
from .models import Event


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
