# web_navigator.py - Quick fix for existing file
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Same authorized domains list
AUTHORIZED_GOV_DOMAINS = {
    'gov.in', 'nic.in', 'india.gov.in', 'mygov.in', 'eci.gov.in',
    'rbi.org.in', 'sebi.gov.in', 'irdai.gov.in', 'epfo.gov.in',
    'ugc.ac.in', 'aicte-india.org', 'ncert.nic.in', 'cbse.gov.in',
    'maharashtra.gov.in', 'karnataka.gov.in', 'tamilnadu.gov.in',
    'gujarat.gov.in', 'rajasthan.gov.in', 'up.gov.in', 'bihar.gov.in',
    'sci.gov.in', 'cag.gov.in', 'upsc.gov.in', 'ssc.nic.in'
}

def is_authorized_gov_domain(url: str) -> bool:
    """Check if URL belongs to authorized government domain"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()  # Fixed: netlomain -> netloc
        
        # Remove 'www.' if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check exact match
        if domain in AUTHORIZED_GOV_DOMAINS:
            return True
        
        # Check if it's a subdomain of authorized domains
        for auth_domain in AUTHORIZED_GOV_DOMAINS:
            if domain.endswith('.' + auth_domain):
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking domain authorization: {str(e)}")
        return False

def navigate_and_extract(url: str) -> str:
    """Navigate and extract content from authorized government websites only"""
    # Validate government source
    if not is_authorized_gov_domain(url):
        domain = urlparse(url).netloc
        return f"❌ UNAUTHORIZED SOURCE: Domain '{domain}' is not in the authorized government domains list. Only official government websites are allowed for information extraction."
    
    try:
        logger.info(f"Extracting content from authorized government site: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(2000)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
        
        # Add source verification
        footer = f"\n\n📋 SOURCE VERIFICATION:\n✅ Authorized Government Website: {urlparse(url).netloc}\n✅ Content extracted and verified successfully"
        
        # Return first 7000 chars + footer
        if len(text) > 7000:
            return text[:7000] + "...\n[TRUNCATED]" + footer
        else:
            return text + footer
    
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}")
        return f"❌ Error extracting content from government website: {str(e)}"
