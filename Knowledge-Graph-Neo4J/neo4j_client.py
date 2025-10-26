import os
from typing import Optional

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError


def get_driver(
    uri: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Driver:
    """Create a Neo4j Driver using env defaults when parameters are omitted."""
    resolved_uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    resolved_username = username or os.getenv('NEO4J_USERNAME')
    resolved_password = password or os.getenv('NEO4J_PASSWORD')

    if not resolved_username or not resolved_password:
        raise ValueError('Neo4j credentials not provided. Set NEO4J_USERNAME and NEO4J_PASSWORD.')

    driver = GraphDatabase.driver(
        resolved_uri,
        auth=(resolved_username, resolved_password),
    )
    driver.verify_connectivity()
    return driver


def run_health_check(driver: Driver) -> bool:
    """Return True when a basic read query succeeds against the database."""
    try:
        with driver.session() as session:
            record = session.run('RETURN 1 AS _ping').single()
            return bool(record and record.get('_ping') == 1)
    except Neo4jError:
        return False
