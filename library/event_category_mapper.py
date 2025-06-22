def get_event_category(event_type: str) -> str | None:
    """
    Returns the category name based on the given event type.

    Args:
        event_type (str): Event type to classify.

    Returns:
        str | None: Matched category name, or None if no match found.
    """
    category_map = {
        "Conferences and Networking Events": [
            "Industry conferences",
            "Networking socials",
            "Places to meet clients and collaborators"
        ],
        "Education, Training and CPD": [
            "Seminars for exchanging knowledge",
            "CPD accredited training events",
            "Day courses",
            "Academic conferences",
            "Creative workshops"
        ],
        "Cultural Events and Exhibitions": [
            "Design festivals",
            "Talks by architects",
            "Walking tours",
            "Architectural films",
            "Exhibitions",
            "Talks and lectures"
        ]
    }

    for category, keywords in category_map.items():
        if event_type.strip() in keywords:
            return category

    return None
