# CLI Interface

import argparse
import sys
import os

from url_service import URLService
from storage import URLDB

DATE_FORMAT = "%d-%m-%YT%H:%M:%S"

# Allow overriding DB file for testing
DB_FILE = os.environ.get('URL_DB_FILE', 'urls.json')
service = URLService(URLDB(DB_FILE))



def cmd_shorten(args):
    """Handle shorten command"""
    existing = service.db.find_by_url(args.long_url)
    if existing:
        print(f"✓ Already shortened: short.ly/{existing.short_code}")
    else:
        short_code = service.shorten(args.long_url)
        print(f"✓ Created: short.ly/{short_code}")


def cmd_resolve(args):
    """Handle resolve command"""
    long_url = service.resolve(args.short_code)
    print(f"→ {long_url}")


def cmd_list(args):
    """Handle list command"""
    urls = service.list_all()
    
    if not urls:
        print("\nNo URLs shortened yet.")
        print("Get started: python main.py shorten \"https://example.com\"\n")
        return
    
    print(f"\n{'#':<5} {'LONG URL':<50} {'SHORT CODE':<15} {'CREATED AT':<25} {'VISIT COUNT':<15}")
    print("-" * 110)
    
    for i, url in enumerate(urls, 1):
        print(f"{i:<5} {url.long_url:<50} {url.short_code:<15} {url.created_at.strftime(DATE_FORMAT):<25} {url.visit_count:<15}")
    
    print()


def main():
    # Main parser
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="URL Shortener CLI - Shorten and manage URLs",
        epilog="""Examples:
  python main.py shorten "https://example.com/very/long/path"
  python main.py resolve aB3x9Z
  python main.py list

For detailed help on a specific command:
  python main.py <command> --help""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")
    sub.required = True

    # ========== SHORTEN COMMAND ==========
    p_shorten = sub.add_parser(
        "shorten",
        help="Create a short code for a long URL",
        description="Create a short code for a long URL",
        epilog="""Examples:
  Shorten a URL:
    python main.py shorten "https://github.com/user/repo"
    → ✓ Created: short.ly/aB3x9Z

  Shorten with query parameters:
    python main.py shorten "https://example.com/page?id=123&ref=home"
    → ✓ Created: short.ly/xY7mN2

  Get existing short code:
    python main.py shorten "https://github.com/user/repo"
    → ✓ Already shortened: short.ly/aB3x9Z

Notes:
  - URLs must include http:// or https://
  - Maximum URL length: 2000 characters
  - Short codes are case-sensitive
  - Duplicate URLs return the same short code""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_shorten.add_argument(
        "long_url",
        help="The long URL to shorten (must start with http:// or https://)"
    )
    p_shorten.set_defaults(func=cmd_shorten)

    # ========== RESOLVE COMMAND ==========
    p_resolve = sub.add_parser(
        "resolve",
        help="Retrieve the original URL from a short code",
        description="Retrieve the original URL from a short code",
        epilog="""Examples:
  Resolve a short code:
    python main.py resolve aB3x9Z
    → https://github.com/user/repo

  Use the resolved URL (Unix/macOS):
    python main.py resolve aB3x9Z | xargs open

  Use the resolved URL (Windows):
    python main.py resolve aB3x9Z | xargs start

Notes:
  - Short codes are exactly 6 characters
  - Short codes are case-sensitive (a-z, A-Z, 0-9)
  - Each resolve increments the visit counter
  - Use 'list' command to see all available short codes""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_resolve.add_argument(
        "short_code",
        help="The 6-character short code to resolve"
    )
    p_resolve.set_defaults(func=cmd_resolve)

    # ========== LIST COMMAND ==========
    p_list = sub.add_parser(
        "list",
        help="Display all shortened URLs with statistics",
        description="Display all shortened URLs with statistics",
        epilog="""Examples:
  View all URLs:
    python main.py list

  Output:
    #     LONG URL                                         SHORT CODE      CREATED AT                VISIT COUNT    
    --------------------------------------------------------------------------------------------------------------
    1     https://example.com/long/path                    aB3x9Z          14-03-2026T10:30:45       5              
    2     https://github.com/user/repo                     xY7mN2          14-03-2026T11:15:20       0              
    3     https://google.com                               kL9pQ1          14-03-2026T12:00:00       23             

Notes:
  - Sorted by creation date (newest first)
  - Visit count increments each time 'resolve' is called
  - Empty list shows "No URLs shortened yet" """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_list.set_defaults(func=cmd_list)

    # Parse arguments
    args = parser.parse_args()

    # Execute command with error handling
    try:
        args.func(args)
    except ValueError as e:
        # User input errors (validation failures)
        print(f"❌ {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        # File access errors
        print(f"❌ File error: {e}")
        print("Tip: Check if the data file exists or has correct permissions")
        sys.exit(1)
    except PermissionError as e:
        # Permission errors
        print(f"❌ Permission denied: {e}")
        print("Solution: Check file permissions or run with appropriate access")
        sys.exit(1)
    except KeyboardInterrupt:
        # User cancelled (Ctrl+C)
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        # Unexpected system errors
        print(f"💥 Unexpected error: {e}")
        print("This shouldn't happen. Please report this issue.")
        sys.exit(2)


if __name__ == "__main__":
    main()