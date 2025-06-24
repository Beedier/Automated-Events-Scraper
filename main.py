import argparse
from controllers import run_scraper, get_all_targets


def main():
    parser = argparse.ArgumentParser()
    categories = sorted(set(c for c, _ in get_all_targets()))
    parser.add_argument("category", choices=categories)

    # Collect targets based on chosen category for validation
    args, remaining = parser.parse_known_args()
    valid_targets = [t for c, t in get_all_targets() if c == args.category] + ["all"]

    parser.add_argument("target", choices=valid_targets)
    args = parser.parse_args()

    run_scraper(args.category, args.target)


if __name__ == "__main__":
    main()
