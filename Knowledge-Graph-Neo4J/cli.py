from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv

from neo4j_client import get_driver, run_health_check
from wikipedia_fetch import preview_wikipedia_page
from utils import extract_entities, parse_entities, persist_entities, print_section


def main() -> None:
    """Entry point for running the Wikipedia legal knowledge extraction and Neo4j persistence."""
    load_dotenv()

    # List of landmark Supreme Court cases and core legal topics
    cases = [
        "Roe_v._Wade",
        "Brown_v._Board_of_Education",
        "Miranda_v._Arizona",
        "Marbury_v._Madison",
        "Gideon_v._Wainwright",
        "Plessy_v._Ferguson",
        "Criminal_law",
        "Evidence_law",
        "Corporate_crime",
        "International_criminal_law",
        "Cybercrime",
        "White-collar_crime",
        "Criminal_procedure",
        "Sentencing",
        "Juvenile_delinquency",
        "Constitutional_law",
        "Tort_law",
        "Contract_law",
        "Administrative_law",
        "Property_law",
        "Common_law"
    ]

    # Connect to Neo4j
    try:
        driver = get_driver()
    except (Neo4jError, ValueError) as exc:
        print_section('Neo4j Status', f'Failed to connect to Neo4j: {exc}')
        return

    # Verify connection
    try:
        if run_health_check(driver):
            print_section('Neo4j Status', 'Connection verified (RETURN 1).')
        else:
            print_section('Neo4j Status', 'Connection established, but health check query failed.')
    except Exception as exc:
        print_section('Neo4j Status', f'Health check failed: {exc}')

    # Loop through each case/topic and process it
    for case in cases:
        try:
            preview = preview_wikipedia_page(case)
            print_section(f'Wikipedia Preview: {case}', preview[:800])  # show first 800 chars only
        except ValueError as exc:
            print_section(f'Wikipedia Preview: {case}', str(exc))
            continue

        try:
            # Extract and parse entities using Gemini
            entities_text = extract_entities(preview)
            parsed_entities = parse_entities(entities_text)

            if parsed_entities:
                print_section(f'Wikipedia Entities: {case}', repr(parsed_entities))
                persist_entities(driver, parsed_entities)
            else:
                fallback = entities_text.strip() or '[]'
                print_section(f'Wikipedia Entities: {case}', fallback)
        except Exception as exc:
            print_section(f'Wikipedia Entities: {case}', f'Failed to extract entities: {exc}')

    # Close Neo4j connection
    driver.close()

if __name__ == '__main__':
    main()
