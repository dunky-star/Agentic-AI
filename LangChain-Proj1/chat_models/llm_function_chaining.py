from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# First chain generates questions
question_prompt = PromptTemplate(
    input_variables=["topic"],
    template="Generate 3 questions about {topic}:"
)

# Second chain generates answers based on questions
answer_prompt = PromptTemplate(
    input_variables=["questions"],
    template="Answer the following questions:\n{questions}\n You response should contain the question and the answer to it."
)

# Create the model
llm = ChatOpenAI(temperature=0.0)

# Output parser to convert model output to string
output_parser = StrOutputParser()

# Build the question generation chain
question_chain = question_prompt | llm | output_parser

# Build the answer generation chain
answer_chain = answer_prompt | llm | output_parser

# Define a function to create the combined input for the answer chain
def create_answer_input(output):
    return {"questions": output}

# Chain everything together
qa_chain = question_chain | create_answer_input | answer_chain

# Run the chain
result = qa_chain.invoke({"topic": "artificial intelligence"})

# Example of a template designed for production use:
'''
customer_support_template = PromptTemplate(
    input_variables=["customer_name", "product_name", "issue_description", "previous_interactions", "tone"],
    template="""
    You are a customer support specialist for {product_name}.

    Customer: {customer_name}
    Issue: {issue_description}
    Previous interactions: {previous_interactions}

    Respond to the customer in a {tone} tone. If you don't have enough information to resolve their issue,
    ask clarifying questions. Always prioritize customer satisfaction and accurate information.
    """
)

# This can now handle all types of customer inquiries with appropriate context
customer_support_response = model.invoke({
    "customer_name": "Alex Smith",
    "product_name": "SmartHome Hub",
    "issue_description": "Device won't connect to WiFi after power outage",
    "previous_interactions": "Customer has already tried resetting the device twice.",
    "tone": "empathetic but technical"
})
'''