import enum
from dbcore.session import Base
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean,
    func, ForeignKey, Enum
)
from sqlalchemy.orm import relationship

# -------------------------------------------------------------------
# Enum for publish status of events
# -------------------------------------------------------------------
class PublishStatusEnum(str, enum.Enum):
    unsynced = "unsynced"
    draft = "draft"
    published = "published"

# -------------------------------------------------------------------
# Event model - represents a scraped or created event entry
# -------------------------------------------------------------------
class Event(Base):
    __tablename__ = "events"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique event URL and originating website
    event_url = Column(String, unique=True, nullable=False, index=True)
    website_name = Column(String, nullable=False, index=True)

    # Raw and processed content fields
    category = Column(String, nullable=True, default=None)
    web_content = Column(Text, nullable=True, default=None)
    title = Column(Text, nullable=True, default=None)
    index_intro = Column(Text, nullable=True, default=None)
    intro = Column(Text, nullable=True, default=None)
    content = Column(Text, nullable=True, default=None)

    # Dates (original and sortable) and location
    dates = Column(String, nullable=True, default=None)
    date_order = Column(String(8), nullable=True, default=None)  # e.g., YYYYMMDD
    location = Column(String, nullable=True, default=None)
    cost = Column(String, nullable=True, default=None)

    # Whether the content was AI-generated or not
    generated_content = Column(Boolean, nullable=False, default=False)

    # Remote system tracking
    remote_event_id = Column(Integer, nullable=True, index=True, default=None)
    publish_status = Column(
        Enum(PublishStatusEnum, name="publish_status_enum"),
        nullable=False,
        default=PublishStatusEnum.unsynced
    )

    # Timestamps
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    # Image relationship (optional)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    image = relationship("Image", back_populates="events")

    def __repr__(self):
        """
        String representation of Event object, useful for debugging.
        """
        return f"Event(id={self.id}, image_id={self.image.id if self.image else None})"

# -------------------------------------------------------------------
# Image model - represents an image attached to an event
# -------------------------------------------------------------------
class Image(Base):
    __tablename__ = "images"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Optional reference to external image (e.g., Beed.ier)
    remote_media_id = Column(Integer, nullable=True, default=None)

    # Image URL (must be unique)
    image_url = Column(String, unique=True, nullable=False)

    # Local Path
    image_path = Column(String, nullable=True, default=None)

    # Timestamps
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    # Relationship to Events
    events = relationship("Event", back_populates="image")
