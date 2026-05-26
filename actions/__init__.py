from actions.open_app import open_app
from actions.search_web import search_web

# Registry mapping action names to their handler functions
ACTION_REGISTRY = {
    "OPEN_APP": open_app,
    "SEARCH_WEB": search_web,
}
