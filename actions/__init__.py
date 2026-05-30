from actions.open_app import open_app
from actions.search_web import search_web
from actions.search_file import search_file
from actions.open_website import open_website

# Registry mapping action names to their handler functions
ACTION_REGISTRY = {
    "OPEN_APP": open_app,
    "SEARCH_WEB": search_web,
    "SEARCH_FILE": search_file,
    "OPEN_WEBSITE": open_website,
}
