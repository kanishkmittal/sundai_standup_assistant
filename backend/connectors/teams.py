# Kanishk — Teams connector via Microsoft Graph API

from connectors import ConnectorRecord


async def fetch(config: dict) -> list[ConnectorRecord]:
    """Fetch yesterday's messages from a Teams group chat for the authenticated user."""
    raise NotImplementedError("TODO: implement Teams connector")
