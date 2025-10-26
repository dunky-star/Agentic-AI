from llm import get_llm
import json
import re

# Updated Ontology for Legal Knowledge Graphs
ONTOLOGY_TYPES = {
    'Case',        # e.g., Roe v. Wade
    'Court',       # e.g., Supreme Court of the United States
    'Law',         # e.g., Civil Rights Act, Constitution
    'Crime',       # e.g., Fraud, Murder
    'Party',       # e.g., Plaintiff, Defendant
    'Evidence',    # e.g., Witness Testimony, Document
    'Verdict',     # e.g., Guilty, Overturned
    'Date'         # e.g., 1973
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
    """Create nodes and relationships in Neo4j from the parsed entities."""
    if not entities:
        return

    with driver.session() as session:
        for i, (entity1_name, entity1_type) in enumerate(entities):
            session.write_transaction(create_node, sanitize_label(entity1_type), entity1_name)

            for j, (entity2_name, entity2_type) in enumerate(entities):
                if i == j:
                    continue

                # Define relationships for Legal Ontology
                if entity1_type == 'Case' and entity2_type == 'Court':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'HEARD_BY')
                elif entity1_type == 'Case' and entity2_type == 'Law':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'INTERPRETS')
                elif entity1_type == 'Case' and entity2_type == 'Verdict':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'RESULTED_IN')
                elif entity1_type == 'Case' and entity2_type == 'Party':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'INVOLVES')
                elif entity1_type == 'Crime' and entity2_type == 'Law':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'DEFINED_BY')
                elif entity1_type == 'Party' and entity2_type == 'Crime':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'CHARGED_WITH')
                elif entity1_type == 'Evidence' and entity2_type == 'Case':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'SUPPORTS')
                elif entity1_type == 'Court' and entity2_type == 'Verdict':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'ISSUED')
                elif entity1_type == 'Case' and entity2_type == 'Date':
                    session.write_transaction(create_relationship, entity1_name, entity2_name, 'DECIDED_ON')


def extract_entities(text: str) -> str:
    """Extract entities and their types from text using Gemini."""
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
                    "enum": [
                        "Case",
                        "Court",
                        "Law",
                        "Crime",
                        "Party",
                        "Evidence",
                        "Verdict",
                        "Date",
                    ],
                },
            },
            "required": ["entity", "type"],
        },
    }

    prompt = f"""
    You are a legal expert creating a Legal Knowledge Graph.
    Extract all relevant entities and their types from the text below.
    Use only these types: Case, Court, Law, Crime, Party, Evidence, Verdict, Date.
    Return valid JSON that matches this schema:
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