from src._core.domain.events.domain_event import DomainEvent


class UserCreated(DomainEvent):
    event_type: str = "user.created"
    user_id: int
    username: str


class UserUpdated(DomainEvent):
    event_type: str = "user.updated"
    user_id: int


class UserDeleted(DomainEvent):
    event_type: str = "user.deleted"
    user_id: int
