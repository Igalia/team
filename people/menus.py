# This is the only `menus.py` that has `NAV_MENU_1ST_LEVEL`.  In all other apps only the `NAV_MENU_2ND_LEVEL` is needed.

def in_app(request):
    """Returns whether `request` would be handled by this app.

    This is a validator for the menu.  It hides the People second level menu when views from other apps are rendered.
    """
    return 'people' in request.resolver_match.app_names or 'root' in request.resolver_match.app_names


MENUS = {
    'NAV_MENU_1ST_LEVEL': [
        {
            "is_people_app": True,  # This is part of a hack to force "active" state for the root:person view.
            "name": "People",
            "url": "people:home",
            'root': True,
        },
        {
            "name": "Skills",
            "url": "skills:home",
            "root": True,
        },
    ],
    "NAV_MENU_2ND_LEVEL": [
        {
            "is_person_view": True,  # This is part of a hack to force "active" state for the root:person view.
            "name": "Home",
            "url": "people:home",
            "root": False,
            "validators": ["people.menus.in_app"],
        },
        {
            "name": "Teams",
            "url": "people:teams",
            "root": False,
            "validators": ["people.menus.in_app"],
        },
        {
            "name": "People picker",
            "url": "people:picker",
            "root": False,
            "validators": ["people.menus.in_app"],
        },
    ],
}
