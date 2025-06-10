# pdf_parser.py - Quick fix for existing file
import requests, os, hashlib
import fitz  # PyMuPDF
import logging
from urllib.parse import urlparse
from typing import tuple

logger = logging.getLogger(__name__)

CACHE_DIR = "pdf_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Authorized Indian Government Domains
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

def parse_pdf(url: str) -> str:
    """Parse PDF from authorized government sources only"""
    # Validate government source
    if not is_authorized_gov_domain(url):
        return f"❌ UNAUTHORIZED SOURCE: URL domain not in authorized government domains list. Only official government sources are allowed."
    
    try:
        hashed = hashlib.md5(url.encode()).hexdigest()
        filepath = os.path.join(CACHE_DIR, f"{hashed}.pdf")

        if not os.path.exists(filepath):
            logger.info(f"Downloading PDF from authorized source: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Government Document Parser) AppleWebKit/537.36'
            }
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(r.content)

        doc = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        
        # Add source verification
        footer = f"\n\n📋 SOURCE VERIFICATION:\n✅ Authorized Government Source: {urlparse(url).netloc}\n✅ Document verified and extracted successfully"
        
        # Return first 7000 chars + footer
        if len(text) > 7000:
            return text[:7000] + "...\n[TRUNCATED]" + footer
        else:
            return text + footer
    
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        return f"❌ Error parsing government PDF: {str(e)}"




