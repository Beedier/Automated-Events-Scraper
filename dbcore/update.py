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
