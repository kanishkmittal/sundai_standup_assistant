import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared import ConnectorRecord


async def generate(records: list[ConnectorRecord]) -> str:
    """Build prompt from connector records and call Claude API to generate standup."""
    raise NotImplementedError("TODO: implement prompt generation")
