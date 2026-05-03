from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConnectorRecord:
    source: str        # "teams" | "github" | "jira"
    timestamp: datetime
    summary: str       # one-line human-readable summary
    category: str      # "message" | "commit" | "ticket_update" | "comment"
    raw_data: dict     # full payload for the prompt to use
