from llm import get_llm
from textwrap import dedent


def print_section(title: str, body: str) -> None:
    """Render a titled block of text for console output."""
    separator = '-' * len(title)
    print(title)
    print(separator)
    print(body)
    print()


def extract_entities(text: str) -> str:
    """Extract entities and their types from text using the configured LLM."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return ''

    prompt = dedent(
        f"""Extract entities and their types from the following text:

{cleaned_text}

Format: Entity - Type (e.g., Geoffrey Duncan Opiyo - Person)"""
    ).strip()

    llm = get_llm('gemini-2.5-flash', temperature=0.0)
    response = llm.invoke(prompt)
    content = getattr(response, 'content', response)

    if isinstance(content, list):
        content = ''.join(
            str(part.get('text', part)) if isinstance(part, dict) else str(part)
            for part in content
        )

    return str(content).strip()
