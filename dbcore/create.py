import logging
import hashlib
from copy import deepcopy
from typing import Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .session import db as db_instance, Database
from .models import Event, Image

logger = logging.getLogger(__name__)


def _error_id(error: Exception) -> str:
    return hashlib.md5(str(error).encode()).hexdigest()[:8]  # Short error ID


def get_or_create_image(
    image_url: str,
    db: Database = db_instance,
    image_path: Optional[str] = None,
    remote_media_id: Optional[int] = None
) -> Optional[Image]:
    try:
        with db.session_scope() as session:
            image = session.query(Image).filter_by(image_url=image_url).first()
            if image:
                return image

            image = Image(
                image_url=image_url,
                image_path=image_path,
                remote_media_id=remote_media_id
            )
            session.add(image)
            session.flush()
            logger.info(f"Image inserted successfully with ID: {image.id}")
            return image

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Error creating image (ID: {err_id})")
        return None


def create_event(
    event_url: str,
    website_name: str,
    db: Database = db_instance,
    **kwargs
) -> Optional[Event]:
    data = deepcopy(kwargs)
    image = None

    if "image_url" in data:
        image = get_or_create_image(
            db=db,
            image_url=data.pop("image_url"),
            image_path=data.pop("image_path", None),
            remote_media_id=data.pop("remote_media_id", None)
        )
        if image is None:
            logger.warning("Image creation failed. Event not created.")
            return None

    try:
        with db.session_scope() as session:
            event = Event(
                event_url=event_url,
                website_name=website_name,
                image=image,
                **data
            )
            session.add(event)
            session.flush()
            logger.info(f"Event inserted successfully with ID: {event.id}")
            return event

    except IntegrityError as e:
        err_id = _error_id(e)
        logger.warning(f"Integrity error on event insert (ID: {err_id})")
        return None

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Database error on event insert (ID: {err_id})")
        return None
