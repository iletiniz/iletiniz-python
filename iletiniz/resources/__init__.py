"""Iletiniz API kaynak (resource) modülleri."""

from iletiniz.resources.health import HealthResource
from iletiniz.resources.messages import MessagesResource

__all__ = ["HealthResource", "MessagesResource"]
