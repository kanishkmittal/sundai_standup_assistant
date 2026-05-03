# Deepika — Claude API prompt construction and standup generation

from connectors import ConnectorRecord


async def generate(records: list[ConnectorRecord]) -> str:
    """Build prompt from connector records and call Claude API to generate standup."""
    raise NotImplementedError("TODO: implement prompt generation")
