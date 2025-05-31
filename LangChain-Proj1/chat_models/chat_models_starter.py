from langchain_openai import ChatOpenAI
#from langchain_google_genai import ChatGoogleGenerativeAI
#from google.cloud import firestore
#from langchain_google_firestore import FirestoreChatMessageHistory
# SystemMessage is used to set the context for the conversation/ role of the AI
# HumanMessage is used to send a message from the user
# AIMessage is used to send a message from the AI model
#from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.schema.runnable import RunnableLambda, RunnableSequence
from langchain.prompts import ChatPromptTemplate
#from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

'''
Steps to replicate this example:
1. Create a Firebase account
2. Create a new Firebase project and Firestore Database
3. Retrieve the Project ID
4. Install the Google Cloud CLI on your computer
   – https://cloud.google.com/sdk/docs/install
   – Authenticate the Google Cloud CLI with your Google account
     – https://cloud.google.com/docs/authentication/
       provide-credentials-adc#local-dev
   – Set your default project to the new Firebase project you created
5. pip install langchain-google-firestore
6. Enable the Firestore API in the Google Cloud Console:
   – https://console.cloud.google.com/apis/enableflow?apid=firestore.googleapis.com&project=crewai-automation
'''


load_dotenv() # Load API key environment variables from .env file

llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Define prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a fact expert who knows fact about {animal}."),
        ("human", "Tell me {fact_count} facts."),
    ]
)

# Use a list to store messages
# chat_history =[
#     # SystemMessage(content="You are an expert in social media content strategy"),
#     # HumanMessage(content="Give a shirt tip to create engaging posts on Instagram"),
# ]

# Create the combined chain using Langchain Expression Langauge (LCEL
#chain = prompt_template | llm | StrOutputParser()

# Run the chain
#result = chain.invoke({"animal": "cat", "fact_count": 3})  # Output

# Create individual runnables (steps in the chain)
format_prompt = RunnableLambda(lambda x: prompt_template.format_prompt(**x))
invoke_llm = RunnableLambda(lambda x: llm.invoke(x.to_messages()))
parse_output = RunnableLambda(lambda x: x.content)

# Create the runnable sequence (Equivalent to the LCEL chain)
chain = RunnableSequence(first=format_prompt, middle=[invoke_llm], last=parse_output)
# Set an initial system message (optional).

response = chain.invoke({"animal": "cat", "fact_count": 3})
'''
system_message = SystemMessage(content="You are a helpful AI assistant.")
chat_history.append(system_message) # Add the system message to the chat history

# Chat loop
while True:
    query = input("You: ")
    if query.lower() in ["exit", "quit"]:
        print("Exiting the chat.")
        break

    chat_history.append(HumanMessage(content=query)) # Add the user's message to the chat history

    # Get AI response using history
    result = llm.invoke(chat_history)
    response = result.content  # Get the AI's response content
    chat_history.append(AIMessage(content=response)) # Add the AI's response to the chat history
    print(f"AI: {response}")  # Print the AI's response
'''


# --- Google Chat Model Example ---
# https://console.cloud.google.com/gen-app-builder/engines
# https://ai.google.dev/gemini-api/docs/models/gemini
#llm_google = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

#result_google_ai = llm_google.invoke(messages)
