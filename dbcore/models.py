from dbcore.session import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_url = Column("Event URL", String, unique=True, nullable=False)
    website_name = Column("Website Name", String, nullable=False)

    web_content = Column("Web Content", Text, nullable=True)
    title = Column("Title", Text, nullable=True)
    index_intro = Column("Index Intro", Text, nullable=True)
    intro = Column("Intro", Text, nullable=True)
    content = Column("Content", Text, nullable=True)
    dates = Column("Dates", String, nullable=True)
    date_order = Column("Date Order", String(8), nullable=True)
    location = Column("Location", String, nullable=True)
    cost = Column("Cost", String, nullable=True)
    generated_content = Column("Generated Content", Boolean, nullable=False, default=False)

    beedier_event_id = Column("Beedier Event ID", Integer, nullable=True)
    published = Column("Published", Boolean, nullable=False, default=False)

    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    image_id = Column(Integer, ForeignKey("image.id"), nullable=True)
    image = relationship("Image", back_populates="event")

    def __repr__(self):
        return f"Event(id={self.id}, image_id={self.image.id})"


class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    beedier_media_id = Column("Beedier Media ID", Integer, nullable=True)
    image_url = Column("Image URL", String, unique=True, nullable=False)

    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    events = relationship("Event", back_populates="image")
