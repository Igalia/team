from people.models import Team

# noinspection PyUnresolvedReferences
MENUS = {
    "NAV_MENU_1ST_LEVEL": [],
    "NAV_MENU_2ND_LEVEL": [
        {
            "name": "Interest vs. Knowledge",
            "url": "skills:interest-vs-knowledge",
            "root": True,
        },
        {
            "name": "Projects",
            "url": "skills:projects",
            "root": True,
            "validators": ["skills.views.enable_projects"],
        },
        {
            "name": "Demand vs. Knowledge",
            "url": "skills:demand-vs-knowledge",
            "root": True,
            "validators": ["skills.views.enable_projects"],
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
