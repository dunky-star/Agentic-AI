from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv

from neo4j_client import get_driver, run_health_check
from wikipedia_fetch import preview_wikipedia_page
from utils import extract_entities, parse_entities, persist_entities, print_section

def main() -> None:
    """Entry point for running the Wikipedia preview, entity extraction, and Neo4j health check."""
    load_dotenv()

    preview: str | None = None
    try:
        preview = preview_wikipedia_page()
        print_section('Wikipedia Preview', preview)
    except ValueError as exc:
        print_section('Wikipedia Preview', str(exc))

    if preview:
        try:
            entities_text = extract_entities(preview)
            parsed_entities = parse_entities(entities_text)
            if parsed_entities:
                print_section('Wikipedia Entities', repr(parsed_entities))
            else:
                fallback = entities_text.strip() or '[]'
                print_section('Wikipedia Entities', fallback)
                parsed_entities = []
        except Exception as exc:  # noqa: BLE001 - surface model errors to the console
            print_section('Wikipedia Entities', f'Failed to extract entities: {exc}')
            parsed_entities = []
    else:
        parsed_entities = []

    try:
        driver = get_driver()
    except (Neo4jError, ValueError) as exc:
        print_section('Neo4j Status', f'Failed to connect to Neo4j: {exc}')
        return

    try:
        if run_health_check(driver):
            print_section('Neo4j Status', 'Connection verified (RETURN 1).')
        else:
            print_section('Neo4j Status', 'Connection established, but health check query failed.')

        try:
            persist_entities(driver, parsed_entities)
        except Exception as exc:
            print_section('Neo4j Persistence', f'Failed to persist entities: {exc}')
    finally:
        driver.close()

if __name__ == '__main__':
    main()
