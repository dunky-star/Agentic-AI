import json
from textwrap import dedent
from neo4j import Driver
from llm import get_llm


class GraphRAG:
    """
    GraphRAG provides graph-augmented reasoning over
    customer–product–brand–payment data in Neo4j.
    """

    def __init__(self, driver: Driver):
        """Initialize with an existing Neo4j driver and prepare LLM."""
        self.driver = driver
        self.llm = get_llm("gemini-2.5-flash", temperature=0.0)

        # Ensure full-text index exists on startup
        self._ensure_fulltext_index()

    # STEP 0: Create fulltext index if missing
    def _ensure_fulltext_index(self):
        cypher = dedent("""
        CREATE FULLTEXT INDEX entityIndex
        IF NOT EXISTS
        FOR (n:Customer|Product|Brand|Category|Feature|PaymentMethod)
        ON EACH [n.name];
        """)
        with self.driver.session() as session:
            session.run(cypher)

    # STEP 1: Retrieve relevant graph context
    def retrieve_context(self, query: str, limit: int = 15) -> str:
        """Search Neo4j for nodes matching the query and return related context."""
        cypher = dedent("""
        CALL db.index.fulltext.queryNodes('entityIndex', $query)
        YIELD node, score
        WITH node, score
        OPTIONAL MATCH (node)-[r]-(neighbor)
        RETURN 
            node.name AS entity,
            labels(node)[0] AS type,
            collect(DISTINCT neighbor.name) AS related_entities,
            collect(DISTINCT type(r)) AS relationships,
            score
        ORDER BY score DESC
        LIMIT $limit;
        """)

        with self.driver.session() as session:
            records = session.run(cypher, {"query": query, "limit": limit}).data()

        if not records:
            return json.dumps(
                [{"message": f"No related entities found for '{query}'"}],
                indent=2
            )

        return json.dumps(records, indent=2)

    # STEP 2: Generate answer via Gemini
    def answer_question(self, user_query: str) -> str:
        """Use Gemini LLM to reason over retrieved subgraph."""
        graph_context = self.retrieve_context(user_query)

        prompt = dedent(f"""
        You are a market intelligence assistant analyzing
        customer–product–brand–payment relationships.

        Use the following graph context to answer the user's question:

        Context:
        {graph_context}

        Question:
        {user_query}

        Guidelines:
        - Be factual and concise.
        - Mention key entities: Customer, Product, Brand, Category, PaymentMethod.
        - Avoid speculation or repetition.
        """)

        response = self.llm.invoke(prompt)
        content = getattr(response, "content", response)
        if isinstance(content, list):
            content = "".join(
                str(part.get("text", part)) if isinstance(part, dict) else str(part)
                for part in content
            )
        return content.strip()
