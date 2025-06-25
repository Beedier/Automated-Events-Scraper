import argparse
from controllers import run_scraper, get_all_targets


def main():
    """
    Parse command-line arguments and run the appropriate scraper.

    Usage:
      python main.py <category> <target> [--include-existing]

    - category: The scraper category (e.g., 'event-url', 'event-web-content')
    - target: The specific target within the category or 'all'
    - --include-existing: If set, process events even if web content exists
    """

    parser = argparse.ArgumentParser(description="Run event scrapers by category and target")

    # Get all unique categories from available targets
    categories = sorted(set(c for c, _ in get_all_targets()))
    parser.add_argument(
        "category",
        choices=categories,
        help="Category of scraper to run"
    )

    # Parse only 'category' first to know valid targets for that category
    args, remaining_argv = parser.parse_known_args()

    # Collect valid targets for the selected category plus 'all'
    valid_targets = [t for c, t in get_all_targets() if c == args.category] + ["all"]

    # Now add 'target' and 'include-existing' arguments
    parser.add_argument(
        "target",
        choices=valid_targets,
        help="Target within the category to scrape or 'all' for all targets"
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="Include events that already have web content (process all)"
    )

    # Parse full args again including the new args
    args = parser.parse_args()

    # Run scraper with parsed arguments
    run_scraper(args.category, args.target, include_existing=args.include_existing)


if __name__ == "__main__":
    main()
