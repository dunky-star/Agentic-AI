from llm import get_llm
import json
import re
from typing import List, Tuple

# Ontology tailored for customer-product interactions
ONTOLOGY_TYPES = {
    'Customer',
    'Product',
    'Brand',
    'Category',
    'Interaction',
    'Preference',
    'Feature',
    'Date',
    'Transaction',
    'PaymentMethod',
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


def parse_entities(entities_text: str) -> List[Tuple[str, str]]:
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

    entities: List[Tuple[str, str]] = []
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
        normalized = 'Label'
    if not normalized[0].isalpha():
        normalized = f'Label_{normalized}'
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


def persist_entities(driver, entities: List[Tuple[str, str]]) -> None:
    """Create nodes and relationships in Neo4j from customer-product entities."""
    if not entities:
        return

    with driver.session() as session:
        for i, (entity1_name, entity1_type) in enumerate(entities):
            session.write_transaction(create_node, sanitize_label(entity1_type), entity1_name)

            for j, (entity2_name, entity2_type) in enumerate(entities):
                if i == j:
                    continue

                # Customer interactions
                if entity1_type == 'Customer' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'PURCHASED')
                elif entity1_type == 'Customer' and entity2_type == 'Preference':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'HAS_PREFERENCE')
                elif entity1_type == 'Customer' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'TRUSTS')
                elif entity1_type == 'Customer' and entity2_type == 'Interaction':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'PERFORMED')
                elif entity1_type == 'Customer' and entity2_type == 'PaymentMethod':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'USES')
                elif entity1_type == 'Customer' and entity2_type == 'Transaction':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'INITIATED')

                # Product relationships
                elif entity1_type == 'Product' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'OFFERED_BY')
                elif entity1_type == 'Product' and entity2_type == 'Category':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'BELONGS_TO')
                elif entity1_type == 'Product' and entity2_type == 'Feature':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'HAS_FEATURE')
                elif entity1_type == 'Product' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'SIMILAR_TO')

                # Temporal and transactional links
                elif entity1_type == 'Transaction' and entity2_type == 'Product':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'INCLUDES')
                elif entity1_type == 'Transaction' and entity2_type == 'Date':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'OCCURRED_ON')
                elif entity1_type == 'PaymentMethod' and entity2_type == 'Transaction':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'PROCESSES')

                # Category / Brand association
                elif entity1_type == 'Category' and entity2_type == 'Brand':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'REPRESENTED_BY')


def extract_entities(text: str) -> str:
    """Extract customer-product entities and their types using the configured LLM."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return '[]'

    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "entity": {"type": "string"},
                "type": {
                    "type": "string",
                    "enum": sorted(ONTOLOGY_TYPES),
                },
            },
            "required": ["entity", "type"],
        },
    }

    prompt = f"""
    Extract entities and their types from the text below.
    Use only the following types: {', '.join(sorted(ONTOLOGY_TYPES))}.
    Output valid JSON only that matches this schema:
    {schema}

    Text:
    {cleaned_text}
    """

    llm = get_llm('gemini-2.5-flash', temperature=0.0)
    response = llm.invoke(prompt)
    content = getattr(response, 'content', response)

    if isinstance(content, list):
        content = ''.join(
            str(part.get('text', part)) if isinstance(part, dict) else str(part)
            for part in content
        )

    return str(content).strip()
