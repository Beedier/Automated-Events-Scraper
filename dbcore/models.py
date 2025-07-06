import enum
from dbcore.session import Base
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean,
    func, ForeignKey, Enum, Table
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
# Association Table for many-to-many between Event and Category
# -------------------------------------------------------------------
event_category_association = Table(
    "event_category_association",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

# -------------------------------------------------------------------
# Event model - represents a scraped or created event entry
# -------------------------------------------------------------------
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    event_url = Column(String, unique=True, nullable=False, index=True)
    website_name = Column(String, nullable=False, index=True)

    web_content = Column(Text, nullable=True, default=None)
    title = Column(Text, nullable=True, default=None)
    index_intro = Column(Text, nullable=True, default=None)
    intro = Column(Text, nullable=True, default=None)
    content = Column(Text, nullable=True, default=None)

    dates = Column(String, nullable=True, default=None)
    date_order = Column(String(8), nullable=True, default=None)
    location = Column(String, nullable=True, default=None)
    cost = Column(String, nullable=True, default=None)

    generated_content = Column(Boolean, nullable=False, default=False)

    remote_event_id = Column(Integer, nullable=True, index=True, default=None)
    publish_status = Column(
        Enum(PublishStatusEnum, name="publish_status_enum"),
        nullable=False,
        default=PublishStatusEnum.unsynced
    )

    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    image = relationship("Image", back_populates="events")

    # New many-to-many relationship
    categories = relationship(
        "Category",
        secondary=event_category_association,
        back_populates="events"
    )

    def __repr__(self):
        return f"Event(id={self.id}, image_id={self.image_id})"

# -------------------------------------------------------------------
# Image model - represents an image attached to an event
# -------------------------------------------------------------------
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    remote_media_id = Column(Integer, nullable=True, default=None)
    image_url = Column(String, unique=True, nullable=False)
    image_path = Column(String, nullable=True, default=None)

    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    events = relationship("Event", back_populates="image")

# -------------------------------------------------------------------
# Category model - represents a category attached to an event
# -------------------------------------------------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    remote_category_id = Column(Integer, unique=True, nullable=False)

    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    # New many-to-many relationship
    events = relationship(
        "Event",
        secondary=event_category_association,
        back_populates="categories"
    )
