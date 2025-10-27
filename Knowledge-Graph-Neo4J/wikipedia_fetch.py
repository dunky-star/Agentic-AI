import wikipediaapi

def preview_wikipedia_page(page_title: str = "Customer_experience", preview_chars: int = 2000) -> str:
    """Return a preview snippet of a Wikipedia page or raise when the page is missing."""
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='my_bot (abc@example.com)'
    )
    page = wiki.page(page_title)

    if not page.exists():
        raise ValueError(f"The page '{page_title}' does not exist.")

    wiki_text = page.text
    return wiki_text[:preview_chars]
