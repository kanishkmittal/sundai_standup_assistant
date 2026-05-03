import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared import ConnectorRecord


async def fetch(config: dict) -> list[ConnectorRecord]:
    """Fetch yesterday's messages from a Teams group chat for the authenticated user."""
    raise NotImplementedError("TODO: implement Teams connector")
