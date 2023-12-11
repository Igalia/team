from people.models import Team


def in_app(request):
    """Returns whether `request` would be handled by this app.
    This is a validator for the menu.  It hides the Skills second level menu when views from other apps are rendered.
    """
    return 'skills' in request.resolver_match.app_names


# noinspection PyUnresolvedReferences
MENUS = {
    "NAV_MENU_1ST_LEVEL": [],
    "NAV_MENU_2ND_LEVEL": [
        {
            "name": "Interest vs. Knowledge",
            "url": "skills:interest-vs-knowledge",
            "root": False,
            "validators": ["skills.menus.in_app"],
        },
        {
            "name": "Projects",
            "url": "skills:projects",
            "root": False,
            "validators": ["skills.views.enable_projects", "skills.menus.in_app"],
        },
        {
            "name": "Demand vs. Knowledge",
            "url": "skills:demand-vs-knowledge",
            "root": True,
            "validators": ["skills.views.enable_projects", "skills.menus.in_app"],
        },
    ],
    "NAV_MENU_TEAM_SELECTOR": [
        {
            "name": team.name,
            "team_slug": team.slug,
            "url": {"viewname": "skills:set-current-team", "kwargs": {"team_slug": team.slug}},
        } for team in Team.objects.all()
    ]
}
