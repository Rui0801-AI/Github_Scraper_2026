import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import aiohttp
import csv
import re
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://api.github.com"

# ------------------------ UTILS ------------------------

def build_headers(token):
    return {"Authorization": f"token {token}"} if token else {}


def build_query(location, created, repos_min, repos_max, followers_min, followers_max):
    query = f'location:"{location}"'

    if created:
        query += f' created:>{created}'

    if repos_min and repos_max:
        query += f' repos:{repos_min}..{repos_max}'
    elif repos_min:
        query += f' repos:>{repos_min}'
    elif repos_max:
        query += f' repos:<{repos_max}'

    if followers_min and followers_max:
        query += f' followers:{followers_min}..{followers_max}'
    elif followers_min:
        query += f' followers:>{followers_min}'
    elif followers_max:
        query += f' followers:<{followers_max}'

    return query


async def fetch(session, url, headers, params=None):
    for _ in range(3):
        try:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 403:
                    raise Exception("Rate limit exceeded")
                return await response.json()
        except:
            await asyncio.sleep(1)
    return {}


async def search_users_all(session, query, headers, max_pages=10):
    url = f"{BASE_URL}/search/users"
    all_users = []

    for page in range(1, max_pages + 1):
        params = {"q": query, "per_page": 100, "page": page}
        data = await fetch(session, url, headers, params)
        users = data.get("items", [])

        if not users:
            break

        all_users.extend(users)

    return all_users


async def get_user_detail(session, username, headers):
    url = f"{BASE_URL}/users/{username}"
    return await fetch(session, url, headers)


async def fetch_all_details(users, headers, progress_callback=None):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in users:
            tasks.append(get_user_detail(session, user["login"], headers))

        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, len(tasks))

        return results


def extract_email(text):
    if not text:
        return ""
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""


def extract_linkedin(blog, bio):
    for text in [blog, bio]:
        if text and "linkedin.com/in/" in text.lower():
            return text
    return ""


# ------------------------ MAIN LOGIC ------------------------

def run_scraper():
    token = token_entry.get().strip()
    location = location_entry.get().strip()
    created = created_entry.get().strip()
    repos_min = repos_min_entry.get().strip()
    repos_max = repos_max_entry.get().strip()
    followers_min = followers_min_entry.get().strip()
    followers_max = followers_max_entry.get().strip()

    if not location:
        messagebox.showerror("Error", "Location required")
        return

    headers = build_headers(token)
    query = build_query(location, created, repos_min, repos_max, followers_min, followers_max)

    file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if not file_path:
        return

    async def main():
        async with aiohttp.ClientSession() as session:
            users = await search_users_all(session, query, headers)

        details = await fetch_all_details(users, headers, update_progress)

        seen = set()

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "url", "location", "email", "linkedin"])

            for d in details:
                username = d.get("login")
                if username in seen:
                    continue
                seen.add(username)

                email = d.get("email") or extract_email(d.get("bio"))
                linkedin = extract_linkedin(d.get("blog"), d.get("bio"))

                writer.writerow([
                    username,
                    d.get("html_url"),
                    d.get("location"),
                    email,
                    linkedin
                ])

        messagebox.showinfo("Done", "Export completed!")

    asyncio.run(main())


def update_progress(current, total):
    progress["maximum"] = total
    progress["value"] = current
    root.update_idletasks()


# ------------------------ GUI ------------------------

root = tk.Tk()
root.title("Advanced GitHub Scraper")
root.geometry("800x600")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="x")

# Inputs
fields = [
    ("GitHub Token", "token_entry"),
    ("Location", "location_entry"),
    ("Created After", "created_entry"),
    ("Min Repos", "repos_min_entry"),
    ("Max Repos", "repos_max_entry"),
    ("Min Followers", "followers_min_entry"),
    ("Max Followers", "followers_max_entry"),
]

entries = {}

for i, (label, var) in enumerate(fields):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
    entry = ttk.Entry(frame, width=50, show="*" if "Token" in label else None)
    entry.grid(row=i, column=1, pady=5)
    entries[var] = entry

# Assign variables
token_entry = entries["token_entry"]
location_entry = entries["location_entry"]
created_entry = entries["created_entry"]
repos_min_entry = entries["repos_min_entry"]
repos_max_entry = entries["repos_max_entry"]
followers_min_entry = entries["followers_min_entry"]
followers_max_entry = entries["followers_max_entry"]

# Progress bar
progress = ttk.Progressbar(root, length=500)
progress.pack(pady=20)

# Button
btn = ttk.Button(root, text="Start Scraping", command=run_scraper)
btn.pack(pady=10)

root.mainloop()
