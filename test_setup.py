from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState
from config import OPENAI_API_KEY, MODEL_NAME

llm = ChatOpenAI(
    api_key = OPENAI_API_KEY,
    model = MODEL_NAME,
    temperature = 0.7
)

response = llm.invoke("Hello! Say 'Setup successful' if you can hear me.")
print(response)