"""Constants for the Google Search Console Dashboard."""

# OAuth2 scopes
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
]

# API service names and versions
WEBMASTERS_API = "webmasters"
WEBMASTERS_VERSION = "v3"
SEARCHCONSOLE_API = "searchconsole"
SEARCHCONSOLE_VERSION = "v1"

# Search Analytics dimensions
DIMENSIONS = ["query", "page", "country", "device", "date", "searchAppearance"]

# Search types
SEARCH_TYPES = {
    "web": "Web",
    "image": "Image",
    "video": "Video",
    "news": "News",
    "discover": "Discover",
    "googleNews": "Google News",
}

# Device categories
DEVICES = {
    "DESKTOP": "Desktop",
    "MOBILE": "Mobile",
    "TABLET": "Tablet",
}

# API quotas and limits
MAX_ROWS_PER_REQUEST = 25000
URL_INSPECTION_DAILY_QUOTA = 2000
URL_INSPECTION_RATE_LIMIT_SECONDS = 0.1

# Cache TTL (seconds)
CACHE_TTL = 300

# Date range presets
DATE_RANGE_PRESETS = {
    "Last 7 days": 7,
    "Last 28 days": 28,
    "Last 3 months": 90,
    "Last 6 months": 180,
    "Last 12 months": 365,
    "Last 16 months": 480,
}

# Country code to name mapping (top countries)
COUNTRY_NAMES = {
    "usa": "United States",
    "gbr": "United Kingdom",
    "ind": "India",
    "deu": "Germany",
    "fra": "France",
    "can": "Canada",
    "aus": "Australia",
    "bra": "Brazil",
    "jpn": "Japan",
    "ita": "Italy",
    "esp": "Spain",
    "nld": "Netherlands",
    "mex": "Mexico",
    "kor": "South Korea",
    "rus": "Russia",
    "tur": "Turkey",
    "idn": "Indonesia",
    "phl": "Philippines",
    "pol": "Poland",
    "tha": "Thailand",
}

# Token file path
TOKEN_FILE = "tokens/token.json"
