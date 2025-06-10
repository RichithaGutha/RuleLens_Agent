# utils.py - Keep as is, just add error handling
from langchain_openai import AzureChatOpenAI
import os
import logging

logger = logging.getLogger(__name__)

try:
    llm = AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    )
except Exception as e:
    logger.error(f"Failed to initialize LLM: {str(e)}")
    llm = None

def summarize_text(text: str) -> str:
    if not llm:
        return "❌ Error: LLM not initialized properly"
    
    try:
        prompt = f"Summarize the following government content into clear bullet points:\n\n{text}"
        response = llm.invoke(prompt)
        
        # Handle different response formats
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        return f"❌ Error summarizing content: {str(e)}"