import json
from dbcore import Event


def export_fine_tuning_events_to_json(events: list[Event], file_path: str) -> None:
    """
    Export a list of events to a JSON file in the following structure:
    [
        {
            "input": "<web_content>",
            "output": {
                "Title": "<title>",
                "Dates": "<dates>"
                "IndexIntro": "<index_intro>",
                "Intro": "<intro>",
                "Content": "<content>",
                "DateOrder": "<date_order>"
                "Location": "<location>",
                "Cost": "<cost>",
                "Categories": ["Category1", "Category2", ...]
            }
        },
        ...
    ]

    Args:
        events (List[Event]): List of Event objects.
        file_path (str): Output JSON file path.
    """
    output_data = []
    for event in events:
        output_data.append({
            "input": event.web_content,
            "output": {
                "Title": event.title,
                "Dates": event.dates,
                "IndexIntro": event.index_intro,

                "Intro": event.intro,
                "Content": event.content,
                "DateOrder": event.date_order,

                "Location": event.location,
                "Cost": event.cost,
                "Categories": [cat.name for cat in event.categories]
            }
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4, sort_keys=False)
