import logging
import hashlib
from copy import deepcopy
from typing import Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .session import db as db_instance, Database
from .models import Event, Image, Category

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
    categories = []

    # Handle image creation if provided
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

    # Handle category assignment
    category_names = data.pop("category_names", [])
    try:
        with db.session_scope() as session:
            # Lookup or create categories
            for name in category_names:
                category = session.query(Category).filter_by(name=name).first()
                if not category:
                    logger.info(f"Creating missing category: {name}")
                    category = Category(name=name, remote_category_id=0)  # Adjust ID logic if needed
                    session.add(category)
                    session.flush()
                categories.append(category)

            # Create the Event
            event = Event(
                event_url=event_url,
                website_name=website_name,
                image=image,
                categories=categories,
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


def create_category(
    name: str,
    remote_category_id: int,
    db: Database = db_instance
) -> Optional[Category]:
    """
    Create and persist a new Category.

    Args:
        name (str): Category name (unique).
        remote_category_id (int): Remote system category ID (unique).
        db (Database): Database instance for session management.

    Returns:
        Optional[Category]: Created Category object or None on failure.
    """
    try:
        with db.session_scope() as session:
            category = session.query(Category).filter_by(name=name).first()
            if category:
                return category

            category = Category(name=name, remote_category_id=remote_category_id)
            session.add(category)
            session.flush()
            return category

    except IntegrityError as e:
        err_id = _error_id(e)
        logger.warning(f"Integrity error on category insert (ID: {err_id})")
        return None

    except SQLAlchemyError as e:
        err_id = _error_id(e)
        logger.error(f"Database error on category insert (ID: {err_id})")
        return None
