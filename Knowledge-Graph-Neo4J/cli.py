import argparse
from dotenv import load_dotenv
from neo4j.exceptions import Neo4jError

from neo4j_client import get_driver, run_health_check
from wikipedia_fetch import preview_wikipedia_page
from utils import extract_entities, parse_entities, persist_entities, print_section
from graph_rag import GraphRAG


def ingest_data(driver):
    """Extract entities from Wikipedia and persist in Neo4j."""
    pages = [
        "PayPal_Inc.",
        "PayPal",
        "Apple_Inc.",
        "Customer_experience",
        "E-commerce",
        "Online_shopping",
        "Consumer_behavior",
        "Product_management",
        "Amazon_(company)",
        "Brand_loyalty",
        "Digital_Payments"
    ]

    for page in pages:
        try:
            preview = preview_wikipedia_page(page)
            print_section(f'Wikipedia Preview: {page}', preview[:800])
        except ValueError as exc:
            print_section(f'Wikipedia Preview: {page}', str(exc))
            continue

        try:
            entities_text = extract_entities(preview)
            parsed_entities = parse_entities(entities_text)

            if parsed_entities:
                print_section(f'Wikipedia Entities: {page}', repr(parsed_entities))
                persist_entities(driver, parsed_entities)
            else:
                fallback = entities_text.strip() or '[]'
                print_section(f'Wikipedia Entities: {page}', fallback)
        except Exception as exc:
            print_section(f'Wikipedia Entities: {page}', f'Failed to extract entities: {exc}')

    print_section("Ingestion Status", "Data ingestion completed successfully.")


def run_graphrag(driver):
    """Run GraphRAG reasoning interactively."""
    try:
        print_section("GraphRAG Mode", "Graph Reasoning Mode Initialized.")
        rag = GraphRAG(driver)

        while True:
            query = input("\nAsk a question (or type 'exit' to quit): ").strip()
            if query.lower() in {"exit", "quit"}:
                print_section("Session Ended", "GraphRAG session closed.")
                break

            try:
                answer = rag.answer_question(query)
                print_section("GraphRAG Answer", answer)
            except Exception as exc:
                print_section("GraphRAG Error", f"Failed to generate answer: {exc}")

    except Exception as exc:
        print_section("GraphRAG Init Error", str(exc))


def main() -> None:
    """CLI entry point for ingesting data, running GraphRAG, or both."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Knowledge Graph CLI - Ingest data, run GraphRAG, or both."
    )
    parser.add_argument(
        "--mode",
        choices=["ingest", "graphrag", "both"],
        default="graphrag",
        help="Choose operation mode: ingest | graphrag | both (default: both)"
    )

    args = parser.parse_args()

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
    except Exception as exc:
        print_section('Neo4j Status', f'Health check failed: {exc}')

    if args.mode == "ingest":
        ingest_data(driver)
    elif args.mode == "graphrag":
        run_graphrag(driver)
    elif args.mode == "both":
        ingest_data(driver)
        run_graphrag(driver)

    driver.close()
    print_section("Neo4j Connection", "Closed successfully.")


if __name__ == "__main__":
    main()
