# Deepika — Orchestrator: calls all connectors and feeds results to prompt

from connectors import ConnectorRecord


async def generate_standup(config: dict) -> str:
    """Call all connectors, merge results, generate standup via Claude API."""
    raise NotImplementedError("TODO: implement orchestrator")
