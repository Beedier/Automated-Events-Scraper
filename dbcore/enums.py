import enum

# -------------------------------------------------------------------
# Enum for publish status of events
# -------------------------------------------------------------------
class PublishStatusEnum(str, enum.Enum):
    UNSYNCED = "unsynced"
    DRAFT = "draft"
    PUBLISHED = "published"

# -------------------------------------------------------------------
# Enum for event categories
#
# Use a string-backed Enum where the values are slugs. This makes
# JSON schema and Pydantic validation easier (incoming JSON uses slugs).
# -------------------------------------------------------------------
class EventCategoryEnum(enum.Enum):
    CONFERENCES_AND_NETWORKING_EVENTS = "Conferences and Networking Events"
    EDUCATION_TRAINING_AND_CPD = "Education Training and CPD"
    CULTURAL_EVENTS_AND_EXHIBITIONS = "Cultural Events and Exhibitions"
