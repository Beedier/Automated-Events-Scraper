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

        ("generate-content", "riba"),
        ("generate-content", "nla"),
        ("generate-content", "bco-org"),
        ("generate-content", "event-bright"),

        ("upload-media", "riba"),
        ("upload-media", "nla"),
        ("upload-media", "bco-org"),
        ("upload-media", "event-bright"),

        ("create-event", "riba"),
        ("create-event", "nla"),
        ("create-event", "bco-org"),
        ("create-event", "event-bright"),

        ("update-event", "riba"),
        ("update-event", "nla"),
        ("update-event", "bco-org"),
        ("update-event", "event-bright"),

        ("update-event-category", "riba"),
        ("update-event-category", "nla"),
        ("update-event-category", "bco-org"),
        ("update-event-category", "event-bright"),

        ("update-event-status", "riba"),
        ("update-event-status", "nla"),
        ("update-event-status", "bco-org"),
        ("update-event-status", "event-bright"),

        ("delete-media", "riba"),
        ("delete-media", "nla"),
        ("delete-media", "bco-org"),
        ("delete-media", "event-bright"),

        ("delete-event", "riba"),
        ("delete-event", "nla"),
        ("delete-event", "bco-org"),
        ("delete-event", "event-bright"),
        # add more pairs here as needed
    ]
