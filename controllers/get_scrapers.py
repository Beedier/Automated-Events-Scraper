from riba import get_event_urls_from_riba
from nla_london import get_event_urls_from_nla_london
from bco_org import get_event_urls_from_bco_org
from event_bright import get_event_urls_from_event_bright

def get_scraper_function(category: str, target: str):
    mapping = {
        ("event-url", "riba"): get_event_urls_from_riba,
        ("event-url", "nla-london"): get_event_urls_from_nla_london,
        ("event-url", "bco-org"): get_event_urls_from_bco_org,
        ("event-url", "event-bright"): get_event_urls_from_event_bright,
    }
    return mapping[(category, target)]
