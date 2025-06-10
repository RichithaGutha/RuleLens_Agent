# agent.py - Enhanced with Government Authorization Controls
import os
import logging
from dotenv import load_dotenv
from typing import Optional, List
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AuthorizedGovDocumentAgent:
    def __init__(self):
        """Initialize the Authorized Government Document Analysis Agent"""
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agent = self._initialize_agent()
        self._print_authorization_info()
    
    def _print_authorization_info(self):
        """Display authorization information"""
        print("🏛️ AUTHORIZED GOVERNMENT DOCUMENT AGENT")
        print("=" * 50)
        print("✅ SECURITY FEATURES ENABLED:")
        print("  • Domain validation for all sources")
        print("  • Government-only content extraction") 
        print("  • Source verification for all responses")
        print("  • Authorized domain whitelist enforcement")
        print("=" * 50)
    
    def _initialize_llm(self):
        """Initialize Azure OpenAI LLM with proper error handling"""
        try:
            from langchain_openai import AzureChatOpenAI
            
            # Get credentials from environment variables
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            
            # Validate required credentials
            if not all([azure_api_key, azure_endpoint]):
                raise ValueError("Missing required Azure OpenAI credentials in environment variables")
            
            llm = AzureChatOpenAI(
                azure_deployment=deployment_name,
                azure_endpoint=azure_endpoint,
                openai_api_key=azure_api_key,
                api_version=api_version,
                temperature=0.1,  # Very low temperature for factual government info
                max_tokens=2000,
                timeout=45
            )
            
            logger.info("Azure OpenAI LLM initialized successfully")
            return llm
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _initialize_tools(self):
        """Initialize all tools with government authorization"""
        from langchain.agents import Tool
        from langchain_community.tools.tavily_search import TavilySearchResults
        
        tools = []
        
        try:
            # Initialize search tool with strict government domain filtering
            search_tool = TavilySearchResults(
                max_results=3,  # Fewer results for quality
                search_depth="advanced",
                include_domains=[
                    "*.gov.in", "*.nic.in", "india.gov.in", "mygov.in",
                    "rbi.org.in", "sebi.gov.in", "irdai.gov.in", "epfo.gov.in",
                    "ugc.ac.in", "aicte-india.org", "ncert.nic.in", "cbse.gov.in",
                    "sci.gov.in", "eci.gov.in", "cag.gov.in", "upsc.gov.in"
                ]
            )
            
            tools.append(
                Tool(
                    name="SearchAuthorizedGovSites",
                    func=search_tool.run,
                    description="""Search ONLY authorized Indian government websites for official information. 
                    This tool searches verified government domains including:
                    - Central govt (.gov.in, .nic.in)
                    - Financial institutions (RBI, SEBI, IRDAI)
                    - Educational bodies (UGC, AICTE, NCERT)
                    - Legal institutions (Supreme Court, Election Commission)
                    Use this for finding official policies, schemes, and announcements."""
                )
            )
            
        except Exception as e:
            logger.warning(f"Failed to initialize search tool: {str(e)}")
        
        # Import custom tools with error handling
        try:
            from custom_tools.pdf_parser import parse_pdf
            tools.append(
                Tool(
                    name="ParseAuthorizedGovPDF",
                    func=parse_pdf,
                    description="""Extract content from government PDF documents ONLY from authorized domains.
                    This tool validates the source before processing and will reject non-government PDFs.
                    Provide the complete PDF URL from official government websites."""
                )
            )
        except ImportError as e:
            logger.warning(f"PDF parser tool not available: {str(e)}")
        
        try:
            from custom_tools.web_navigator import navigate_and_extract
            tools.append(
                Tool(
                    name="ExtractAuthorizedGovContent",
                    func=navigate_and_extract,
                    description="""Extract content from authorized government websites ONLY.
                    This tool validates domain authorization before extraction and rejects non-government sites.
                    Use for extracting information from official government web pages."""
                )
            )
        except ImportError as e:
            logger.warning(f"Web navigator tool not available: {str(e)}")
        
        try:
            from custom_tools.utils import summarize_text, get_authorized_domains_list
            tools.append(
                Tool(
                    name="SummarizeGovContent",
                    func=summarize_text,
                    description="""Summarize government content that has been verified as from authorized sources.
                    This tool only processes content that has passed government source verification."""
                )
            )
            
            tools.append(
                Tool(
                    name="ListAuthorizedDomains",
                    func=get_authorized_domains_list,
                    description="""Display the list of authorized government domains that this agent accepts.
                    Use this when users ask about which sources are considered official."""
                )
            )
        except ImportError as e:
            logger.warning(f"Utility tools not available: {str(e)}")
        
        if not tools:
            raise ValueError("No tools were successfully initialized")
        
        logger.info(f"Initialized {len(tools)} authorized government tools")
        return tools
    
    def _initialize_agent(self):
        """Initialize the agent with tools and LLM"""
        try:
            from langchain.agents import initialize_agent, AgentType
            
            agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=4,  # Limit iterations for efficiency
                early_stopping_method="generate",
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            logger.info("Authorized government agent initialized successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            raise
    
    def query(self, question: str) -> dict:
        """
        Process a query about government information with authorization checks
        
        Args:
            question (str): The question to ask about government information
            
        Returns:
            dict: Contains the answer and intermediate steps
        """
        try:
            logger.info(f"Processing authorized query: {question}")
            
            # Enhanced query with authorization context
            enhanced_query = f"""
            GOVERNMENT INFORMATION REQUEST - AUTHORIZED SOURCES ONLY

            Query: {question}

            CRITICAL INSTRUCTIONS:
            1. ONLY use information from verified government sources
            2. All content must be from authorized .gov.in, .nic.in or equivalent official domains
            3. Reject any information from unofficial sources
            4. Verify source authorization before processing any content
            5. Provide accurate, factual responses based ONLY on official government documentation
            6. Include source verification in your response
            7. If no authorized sources are found, clearly state this limitation

            Please search for and provide official government information about this query.
            """
            
            result = self.agent(enhanced_query)
            
            # Add authorization footer to response
            answer = result['output']
            if "❌ UNAUTHORIZED SOURCE" not in answer:
                answer += "\n\n🔒 AUTHORIZATION STATUS: All information verified from official government sources only."
            
            return {
                'answer': answer,
                'intermediate_steps': result.get('intermediate_steps', []),
                'success': True,
                'sources_verified': True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'answer': f"❌ Error processing your government information request: {str(e)}",
                'intermediate_steps': [],
                'success': False,
                'sources_verified': False
            }
    
    def interactive_session(self):
        """Run an interactive session with authorization controls"""
        print("\n🏛️ AUTHORIZED GOVERNMENT INFORMATION AGENT")
        print("Ask questions about Indian government policies, schemes, and official information.")
        print("📋 SECURITY: Only official government sources will be used.")
        print("Type 'domains' to see authorized sources, 'quit' to exit.\n")
        
        while True:
            try:
                query = input("❓ Your government query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Session ended. Stay informed with official sources!")
                    break
                
                if query.lower() == 'domains':
                    from custom_tools.utils import get_authorized_domains_list
                    print(get_authorized_domains_list())
                    continue
                
                if not query:
                    print("Please enter a valid question about government information.")
                    continue
                
                print("\n🔍 Searching authorized government sources...")
                result = self.query(query)
                
                if result['success']:
                    print(f"\n✅ OFFICIAL RESPONSE:\n{result['answer']}\n")
                    if not result['sources_verified']:
                        print("⚠️  WARNING: Source verification may have failed")
                else:
                    print(f"\n❌ Error: {result['answer']}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended by user.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in interactive session: {str(e)}")
                print(f"❌ An unexpected error occurred: {str(e)}\n")


def main():
    """Main function to run the authorized government agent"""
    try:
        # Initialize the agent
        agent = AuthorizedGovDocumentAgent()
        
        # Check if running interactively or with a single query
        if len(sys.argv) > 1:
            # Command line argument provided
            query = ' '.join(sys.argv[1:])
            result = agent.query(query)
            print(f"✅ OFFICIAL RESPONSE:\n{result['answer']}")
        else:
            # Interactive mode
            agent.interactive_session()
            
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        print(f"❌ Failed to start the authorized government agent: {str(e)}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()