def get_all_targets():
    # Returns all valid (category, target) pairs
    return [
        ("event-url", "riba"),
        ("event-url", "nla"),
        ("event-url", "bco-org"),
        ("event-url", "event-bright"),

        ("event-web-content", "riba"),
        ("event-web-content", "nla"),
        ("event-web-content", "bco-org"),
        ("event-web-content", "event-bright"),

        ("process-image", "riba"),
        ("process-image", "nla"),
        ("process-image", "bco-org"),
        ("process-image", "event-bright"),
        # add more pairs here as needed
    ]