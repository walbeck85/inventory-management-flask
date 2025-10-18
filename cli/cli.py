import argparse
import os
import sys
import json
import requests

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")

def _print(obj):
    print(json.dumps(obj, indent=2))

def cmd_list(args):
    r = requests.get(f"{API_URL}/inventory", timeout=5)
    r.raise_for_status()
    _print(r.json())

def cmd_get(args):
    r = requests.get(f"{API_URL}/inventory/{args.id}", timeout=5)
    if r.status_code == 404:
        print("Error: Item not found"); sys.exit(1)
    r.raise_for_status()
    _print(r.json())

def cmd_add(args):
    payload = {
        "product_name": args.name,
        "price": float(args.price or 0),
        "stock": int(args.stock or 0),
        "brands": args.brands or "",
        "barcode": args.barcode or "",
        "ingredients_text": args.ingredients or "",
    }
    r = requests.post(f"{API_URL}/inventory", json=payload, timeout=5)
    if r.status_code == 400:
        print(r.json().get("error")); sys.exit(1)
    r.raise_for_status()
    _print(r.json())

def cmd_update(args):
    payload = {}
    if args.name is not None: payload["product_name"] = args.name
    if args.price is not None: payload["price"] = float(args.price)
    if args.stock is not None: payload["stock"] = int(args.stock)
    if args.brands is not None: payload["brands"] = args.brands
    if args.barcode is not None: payload["barcode"] = args.barcode
    if args.ingredients is not None: payload["ingredients_text"] = args.ingredients

    r = requests.patch(f"{API_URL}/inventory/{args.id}", json=payload, timeout=5)
    if r.status_code == 404:
        print("Error: Item not found"); sys.exit(1)
    r.raise_for_status()
    _print(r.json())

def cmd_delete(args):
    r = requests.delete(f"{API_URL}/inventory/{args.id}", timeout=5)
    if r.status_code == 404:
        print("Error: Item not found"); sys.exit(1)
    if r.status_code != 204:
        r.raise_for_status()
    print("Deleted")

def cmd_search(args):
    r = requests.get(f"{API_URL}/inventory/search", params={"barcode": args.barcode}, timeout=5)
    if r.status_code == 404:
        print("Error: Product not found"); sys.exit(1)
    if r.status_code == 400:
        print(r.json().get("error")); sys.exit(1)
    r.raise_for_status()
    _print(r.json())

def cmd_import(args):
    payload = {
        "barcode": args.barcode,
        "price": float(args.price or 0),
        "stock": int(args.stock or 0),
    }
    r = requests.post(f"{API_URL}/inventory/import", json=payload, timeout=5)
    if r.status_code == 404:
        print("Error: Product not found"); sys.exit(1)
    if r.status_code == 400:
        print(r.json().get("error")); sys.exit(1)
    r.raise_for_status()
    _print(r.json())

def build_parser():
    p = argparse.ArgumentParser(prog="inventory", description="Inventory CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("list")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("get")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_get)

    s = sub.add_parser("add")
    s.add_argument("--name", required=True)
    s.add_argument("--price", required=False)
    s.add_argument("--stock", required=False)
    s.add_argument("--brands", required=False)
    s.add_argument("--barcode", required=False)
    s.add_argument("--ingredients", required=False)
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("update")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--price")
    s.add_argument("--stock")
    s.add_argument("--brands")
    s.add_argument("--barcode")
    s.add_argument("--ingredients")
    s.set_defaults(func=cmd_update)

    s = sub.add_parser("delete")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_delete)

    s = sub.add_parser("search")
    s.add_argument("--barcode", required=True)
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("import")
    s.add_argument("--barcode", required=True)
    s.add_argument("--price", required=False)
    s.add_argument("--stock", required=False)
    s.set_defaults(func=cmd_import)

    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()