from llm import get_llm
import json
import re

# Updated Ontology for Customers-Products Knowledge Graphs
ONTOLOGY_TYPES = {
    'Customer',     # e.g., Geoffrey Duncan Opiyo, Alice
    'Product',      # e.g., iPhone 15, AirPods
    'Brand',        # e.g., Apple, Samsung, PayPal
    'Category',     # e.g., Electronics, Clothing
    'Interaction',  # e.g., Purchase, Review, Like
    'Preference',   # e.g., High Quality, Affordable
    'Feature',      # e.g., Battery Life, Screen Size
    'Date'          # e.g., 2025-10-26
    "Transaction",  # e.g., Order12345
    'PaymentMethod' # e.g., Credit Card, PayPal
}

def print_section(title: str, body: str) -> None:
    """Render a titled block of text for console output."""
    separator = '-' * len(title)
    print(title)
    print(separator)
    print(body)
    print()

def clean_entity_name(entity_name: str) -> str:
    """Remove leading bullets, numbering, punctuation, and whitespace from entity names."""
    cleaned = re.sub(r"^\s*\d*[\.\)]?\s*", "", entity_name)
    cleaned = re.sub(r"^\s*[\*\-•]+\s*", "", cleaned)
    return cleaned.strip()

def parse_entities(entities_text: str) -> list[tuple[str, str]]:
    """Parse the LLM JSON response into a list of (entity, type) tuples."""
    raw = entities_text.strip()
    if not raw:
        return []

    start_idx = raw.find('[')
    end_idx = raw.rfind(']')
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        return []

    payload = raw[start_idx:end_idx + 1]
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []

    entities: list[tuple[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        entity_name = item.get('entity')
        entity_type = item.get('type')
        if not entity_name or not entity_type:
            continue
        normalized_type = entity_type.strip()
        if normalized_type not in ONTOLOGY_TYPES:
            normalized_type = normalized_type.title()
        if normalized_type not in ONTOLOGY_TYPES:
            continue
        entities.append((clean_entity_name(str(entity_name)), normalized_type))
    return entities

def sanitize_label(label: str) -> str:
    """Convert a free-form label into a Neo4j-safe label."""
    normalized = re.sub(r"\s+", "_", label.strip())
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip('_')
    if not normalized:
        normalized = "Label"
    if not normalized[0].isalpha():
        normalized = f"Label_{normalized}"
    return normalized[0].upper() + normalized[1:] if len(normalized) > 1 else normalized.upper()

def create_node(tx, label: str, name: str) -> None:
    """Create or reuse a node with the given label and name."""
    query = f"MERGE (n:{label} {{name: $name}})"
    tx.run(query, name=name)


def create_relationship(tx, entity1: str, entity2: str, relationship: str) -> None:
    """Create or reuse a directed relationship between two named nodes."""
    query = (
        f"MATCH (a {{name: $entity1}}), (b {{name: $entity2}}) "
        f"MERGE (a)-[r:{relationship}]->(b) "
        "RETURN type(r)"
    )
    tx.run(query, entity1=entity1, entity2=entity2)

def persist_entities(driver, entities: list[tuple[str, str]]) -> None:
    """Create nodes and relationships in Neo4j from parsed entities (Customer-Product-Payment Knowledge Graph)."""
    if not entities:
        return

    with driver.session() as session:
        for i, (entity1_name, entity1_type) in enumerate(entities):
            # Ensure node exists or merge
            session.write_transaction(create_node, sanitize_label(entity1_type), entity1_name)

            for j, (entity2_name, entity2_type) in enumerate(entities):
                if i == j:
                    continue

                # CUSTOMER–PRODUCT relationships
                if entity1_type == 'Customer' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'PURCHASED')
                elif entity1_type == 'Customer' and entity2_type == 'Preference':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'HAS_PREFERENCE')
                elif entity1_type == 'Customer' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'TRUSTS')
                elif entity1_type == 'Customer' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'VIEWED')

                # PRODUCT–BRAND–CATEGORY relationships
                elif entity1_type == 'Product' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'OFFERED_BY')
                elif entity1_type == 'Product' and entity2_type == 'Category':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'BELONGS_TO')
                elif entity1_type == 'Product' and entity2_type == 'Feature':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'HAS_FEATURE')
                elif entity1_type == 'Product' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'SIMILAR_TO')

                # PAYMENT + TRANSACTION relationships
                elif entity1_type == 'Customer' and entity2_type == 'PaymentMethod':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'USES')
                elif entity1_type == 'PaymentMethod' and entity2_type == 'Transaction':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'PROCESSES')
                elif entity1_type == 'Customer' and entity2_type == 'Transaction':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'INITIATED')

                # GENERAL FALLBACK (optional)
                elif entity1_type == 'Category' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'REPRESENTED_BY')


def extract_entities(text: str) -> str:
    """Extract entities and their types from text using Gemini (Customer-Product-Preference domain)."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return '[]'

    # Define the JSON schema expected from Gemini
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "entity": {"type": "string"},
                "type": {
                    "type": "string",
                    "enum": [
                        "Customer",
                        "Product",
                        "Brand",
                        "Category",
                        "Interaction",
                        "Preference",
                        "Feature",
                        "Date",
                        "Transaction",
                        "PaymentMethod"
                    ],
                },
            },
            "required": ["entity", "type"],
        },
    }

    # LLM instruction prompt for Gemini
    prompt = f"""
    You are a market intelligence expert building a Knowledge Graph of customer-product relationships.

    Extract all relevant entities and their types from the text below using ONLY these types:
    Customer, Product, Brand, Category, Interaction, Preference, Feature, Date, PaymentMethod.

    Guidelines:
    - Customers are people or user identifiers.
    - Products are physical or digital items.
    - Brands are companies offering products.
    - Categories group products.
    - Interactions describe user actions (purchase, view, like, review, payment, ).
    - Preferences describe opinions (e.g., affordable, durable, convenient, secure).
    - Features describe product characteristics (e.g., battery life, security, integration).
    - Dates represent temporal information such as release or transaction times.

    Return **valid JSON** that matches this schema:
    {schema}

    Text:
    {cleaned_text}
    """

    # Initialize Gemini model
    llm = get_llm('gemini-2.5-flash', temperature=0.0)
    response = llm.invoke(prompt)
    content = getattr(response, 'content', response)

    # Handle both list and text responses robustly
    if isinstance(content, list):
        content = ''.join(
            str(part.get('text', part)) if isinstance(part, dict) else str(part)
            for part in content
        )

    return str(content).strip()
