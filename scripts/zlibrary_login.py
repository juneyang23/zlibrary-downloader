"""
Z-Library Login Helper

Opens a session to z-library.sk, prompts for manual login (email + password or token),
and saves cookies to ~/.zlibrary_cookies.json for reuse by zlibrary_download.py.

Usage:
    python3 zlibrary_login.py
"""

import os
import json
import sys
import requests

COOKIE_FILE = os.path.expanduser("~/.zlibrary_cookies.json")
BASE_URL = "https://z-library.sk"


def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    print("Z-Library Login")
    print("=" * 40)
    print(f"Base URL: {BASE_URL}")
    print()
    print("You have two options:")
    print("1. Log in with email + password")
    print("2. Use an existing remix user key (token) from your Z-Library account")
    print()

    choice = input("Choose (1 or 2): ").strip()

    if choice == "1":
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        payload = {"email": email, "password": password}
        resp = session.post(f"{BASE_URL}/eapi/user/login", json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text[:200]}")
            sys.exit(1)
        data = resp.json()
        if data.get("error"):
            print(f"Login error: {data['error']}")
            sys.exit(1)
        print("Login successful!")

    elif choice == "2":
        token = input("Remix user key (token): ").strip()
        session.cookies.set("remix_userkey", token)
        resp = session.get(f"{BASE_URL}/", timeout=30)
        resp.raise_for_status()
        print("Token set. Verifying...")
    else:
        print("Invalid choice.")
        sys.exit(1)

    cookie_jar = session.cookies.get_dict()
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookie_jar, f, indent=2)

    print(f"Cookies saved to {COOKIE_FILE}")
    print("You can now use zlibrary_download.py without logging in again.")


if __name__ == "__main__":
    main()
