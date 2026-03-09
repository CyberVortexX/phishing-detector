import re
import math
from urllib.parse import urlparse
TRUSTED_DOMAINS = [

    # ===== Global Tech =====
    "google.com",
    "accounts.google.com",
    "mail.google.com",
    "microsoft.com",
    "login.microsoftonline.com",
    "apple.com",
    "icloud.com",
    "github.com",
    "stackoverflow.com",
    "wikipedia.org",
    "mozilla.org",
    "youtube.com",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",

    # ===== Global Services =====
    "amazon.com",
    "aws.amazon.com",
    "cloudflare.com",
    "openai.com",
    "netflix.com",
    "spotify.com",
    "dropbox.com",

    # ===== Global Payments =====
    "paypal.com",
    "stripe.com",
    "wise.com",
    "squareup.com",

    # ===== Indian Banks =====
    "hdfcbank.com",
    "netbanking.hdfcbank.com",
    "icicibank.com",
    "infinity.icicibank.com",
    "axisbank.com",
    "axisbank.co.in",
    "onlinesbi.sbi",
    "retail.onlinesbi.sbi",
    "bankofbaroda.in",
    "kotak.com",
    "indusind.com",
    "yesbank.in",
    "federalbank.co.in",
    "unionbankofindia.co.in",
    "bankofindia.co.in",
    "canarabank.com",

    # ===== Indian Payments =====
    "paytm.com",
    "phonepe.com",
    "gpay.google.com",
    "bharatpe.com",

    # ===== Indian Platforms =====
    "flipkart.com",
    "myntra.com",
    "zomato.com",
    "swiggy.com",
    "ola.com",
    "irctc.co.in",

    # ===== Indian Government =====
    "gov.in",
    "nic.in",
    "uidai.gov.in",
    "incometax.gov.in",
    "passportindia.gov.in"
]
# -----------------------------
# Suspicious keywords
# -----------------------------
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "secure",
    "account", "bank", "signin", "confirm",
    "password", "paypal", "ebay", "crypto"
]

# -----------------------------
# Suspicious TLDs
# -----------------------------
SUSPICIOUS_TLDS = [
    ".xyz",".top",".tk",".ml",".ga",".cf",
    ".gq",".work",".support",".click",".zip",".review"
]

# -----------------------------
# URL shorteners
# -----------------------------
SHORTENERS = [
    "bit.ly","tinyurl","goo.gl","t.co",
    "ow.ly","is.gd","buff.ly"
]

# -----------------------------
# Indian + Global Brands
# -----------------------------
BRANDS = [
"sbi","icici","hdfc","axis","kotak",
"paytm","phonepe","gpay",
"amazon","flipkart","google","microsoft",
"apple","netflix","instagram","facebook",
"whatsapp","linkedin","yahoo",
"irctc","ola","zomato","swiggy"
]

def is_trusted_domain(url):

    domain = urlparse(url).netloc.replace("www.", "")

    for trusted in TRUSTED_DOMAINS:
        if domain.endswith(trusted):
            return 1

    return 0
# -----------------------------
# Helper functions
# -----------------------------

def has_ip(url):
    return 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0


def count_digits(url):
    return sum(c.isdigit() for c in url)


def count_letters(url):
    return sum(c.isalpha() for c in url)


def entropy(url):

    if len(url) == 0:
        return 0

    prob = [float(url.count(c)) / len(url) for c in set(url)]

    return -sum(p * math.log2(p) for p in prob)


def count_suspicious_keywords(url):

    url_lower = url.lower()

    return sum(keyword in url_lower for keyword in SUSPICIOUS_KEYWORDS)


def suspicious_tld(domain):

    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            return 1

    return 0


def brand_impersonation(url):

    url = url.lower()

    for brand in BRANDS:
        if brand in url:
            return 1

    return 0


# -----------------------------
# Main feature extractor
# -----------------------------

def extract_features(url):

    parsed = urlparse(url)

    domain = parsed.netloc
    path = parsed.path

    features = {}

    # -------------------------
    # Length features
    # -------------------------

    features["url_length"] = len(url)
    features["domain_length"] = len(domain)
    features["path_length"] = len(path)

    # -------------------------
    # Character counts
    # -------------------------

    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_slashes"] = url.count("/")
    features["num_at"] = url.count("@")
    features["num_question"] = url.count("?")
    features["num_equal"] = url.count("=")
    features["num_and"] = url.count("&")

    # -------------------------
    # Digit / letter stats
    # -------------------------

    features["num_digits"] = count_digits(url)
    features["num_letters"] = count_letters(url)

    length = len(url) if len(url) > 0 else 1

    features["digit_ratio"] = features["num_digits"] / length

    special_chars = sum(not c.isalnum() for c in url)

    features["special_char_ratio"] = special_chars / length

    # -------------------------
    # Security indicators
    # -------------------------

    features["has_ip"] = has_ip(url)

    features["uses_https"] = 1 if parsed.scheme == "https" else 0

    # -------------------------
    # Subdomain analysis
    # -------------------------

    dot_count = domain.count(".")

    features["subdomain_count"] = dot_count - 1 if dot_count > 1 else 0

    features["long_subdomain"] = 1 if features["subdomain_count"] > 2 else 0

    # -------------------------
    # Phishing indicators
    # -------------------------

    features["suspicious_keywords"] = count_suspicious_keywords(url)

    features["entropy"] = entropy(url)

    features["trusted_domain"] = is_trusted_domain(url)
    
    features["suspicious_tld"] = suspicious_tld(domain)

    features["is_shortened"] = int(any(short in url for short in SHORTENERS))

    features["brand_impersonation"] = brand_impersonation(url)

    # -------------------------
    # Return features
    # -------------------------
    
    return list(features.values())