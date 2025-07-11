import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_llm(provider: str = "groq", api_key: str = None, model: str=None):
    if not api_key:
        raise ValueError(f"`api_key` is required for {provider}.")
    
    provider = provider.lower()
    if provider == "groq":
        return ChatGroq(
            model=model or "llama3-70b-8192",
            api_key=api_key,
            streaming=True
        )
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model=model or "models/chat-bison-001",
            api_key=api_key,
            streaming=True,
        )
    elif provider == "openai":
        return ChatOpenAI(
            model_name=model or "gpt-3.5-turbo",
            openai_api_key=api_key,
            streaming=True,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def create_chat_chain(llm, system_prompt: str = "You are a helpful AI assistant."):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    return prompt | llm | StrOutputParser()
