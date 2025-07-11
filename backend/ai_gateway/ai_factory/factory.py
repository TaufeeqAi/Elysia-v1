import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_llm(provider: str = "groq", api_key: str = None, model: str=None):
    
    if provider == "groq":
        if not api_key:
            raise ValueError("`api_key` is required for Groq.")
        return ChatGroq(
                model=model or "llama3-70b-8192",
                api_key=api_key,
                streaming=True
            )
    elif provider == "google":
        if not api_key:
            raise ValueError("`api_key` is required for google.")
        return ChatGoogleGenerativeAI(
                model=model,
                api_key=api_key,
                streaming=True,
            )
    elif provider == "openai":
        if not api_key:
            raise ValueError("`api_key` is required for openai.")
        return ChatGoogleGenerativeAI(
                model=model,
                api_key=api_key,
                streaming=True,
            )
    # Add other providers here, e.g., 'gemini', 'anthropic'
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    

def create_chat_chain(llm, system_prompt: str = "You are a helpful AI assistant."):
    """Create a LangChain pipeline for chat interactions."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    return prompt | llm | StrOutputParser()