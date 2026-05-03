import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared import ConnectorRecord


async def generate_standup(config: dict) -> str:
    """Call all connectors, merge results, generate standup via Claude API."""
    raise NotImplementedError("TODO: implement orchestrator")
