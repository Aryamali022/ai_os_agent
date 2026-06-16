from actions.open_app import open_app
from actions.close_app import close_app
from actions.search_web import search_web
from actions.open_website import open_website
from actions.system_control import system_control

# Registry mapping action names to their handler functions
ACTION_REGISTRY = {
    "OPEN_APP": open_app,
    "CLOSE_APP": close_app,
    "SEARCH_WEB": search_web,
    "OPEN_WEBSITE": open_website,
    "SYSTEM_CONTROL": system_control,
}
