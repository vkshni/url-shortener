# CLI Interface

import argparse
import sys

from url_service import URLService

service = URLService()

def cmd_shorten(args):

    existing = service.db.find_by_url(args.long_url)
    if existing:
        print(f"✓ Already shortened: short.ly/{existing.short_code}")
    else:
        short_code = service.shorten(args.long_url)
        print(f"✓ Created: short.ly/{short_code}")

def cmd_resolve(args):

    long_url = service.resolve(args.short_code)
    print(f"✓ URL resolved: {long_url}")


def main():

    parser = argparse.ArgumentParser(
        prog= "main",
        description="URL Shortener CLI",
        add_help=True
    )

    sub = parser.add_subparsers(dest="command")
    sub.required = True

    #shorten
    p_shorten = sub.add_parser("shorten", help="Shorten a long url", description="Create a short code for a long URL")
    p_shorten.add_argument("long_url", help="URL to shorten (must start with http:// or https://)")
    p_shorten.set_defaults(func=cmd_shorten)

    #resolve
    p_resolve = sub.add_parser("resolve", help="Resolve a short code", description="Resolve a long URL for a short code")
    p_resolve.add_argument("short_code", help="Code to resolve (6 characters with base 62 (a-z,A-Z,0-9))")
    p_resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args()

    try:
        args.func(args)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 System Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()