# Kanishk — GitHub connector via GitHub REST API

from connectors import ConnectorRecord


async def fetch(config: dict) -> list[ConnectorRecord]:
    """Fetch yesterday's commits across configured repos for the authenticated user."""
    raise NotImplementedError("TODO: implement GitHub connector")
