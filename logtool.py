import sys
import json
import argparse
from collections import defaultdict

def analyze(path: str) -> dict | None:
    level_counter = defaultdict(int)
    service_counter = defaultdict(int)
    skipped = 0
    skipped_reasons = defaultdict(int)

    try:
        f=open(path)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        return None
    
    with f:
        for line in f:
            try:
                record = json.loads(line)
                level_counter[record["level"]] += 1
                service_counter[record["service"]] += 1
            except json.JSONDecodeError:
                skipped += 1
                skipped_reasons["bad json"] += 1
            except KeyError as e:
                skipped += 1
                skipped_reasons[f"missing key {e}"] += 1
                    
    return {
             "levels": dict(level_counter),
             "services": dict(service_counter),
             "skipped": skipped,
             "reasons": dict(skipped_reasons),
         }

def print_report(result, show_reasons):
    print(f"Levels:   {result['levels']}")
    print(f"Services: {result['services']}")
    print(f"Skipped:  {result['skipped']}")
    if show_reasons:
        print("Reasons:")
        for reason, count in result["reasons"].items():
            print(f"  {reason}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Analyze JSON-per-line logs")
    parser.add_argument("path", help="Path to the log file to analyze")
    parser.add_argument("--show-reasons", action="store_true",
                        help="Show why lines were skipped")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted text")
    args = parser.parse_args()

    result = analyze(args.path)
    if result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_report(result, args.show_reasons)

if __name__ == "__main__":
    main()
    

# End of logtool.py