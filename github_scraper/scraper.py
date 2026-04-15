from __future__ import annotations

import asyncio
from collections.abc import Callable

import aiohttp

from github_scraper.models import SearchFilters


BASE_URL = "https://api.github.com"
ProgressCallback = Callable[[int, int, str], None]


def build_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"token {token}"} if token else {}


def build_query(filters: SearchFilters) -> str:
    query = f'location:"{filters.location}"'

    if filters.created_after:
        query += f" created:>{filters.created_after}"

    if filters.min_repos and filters.max_repos:
        query += f" repos:{filters.min_repos}..{filters.max_repos}"
    elif filters.min_repos:
        query += f" repos:>{filters.min_repos}"
    elif filters.max_repos:
        query += f" repos:<{filters.max_repos}"

    if filters.min_followers and filters.max_followers:
        query += f" followers:{filters.min_followers}..{filters.max_followers}"
    elif filters.min_followers:
        query += f" followers:>{filters.min_followers}"
    elif filters.max_followers:
        query += f" followers:<{filters.max_followers}"

    return query


async def fetch(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict[str, str],
    params: dict[str, str | int] | None = None,
) -> dict:
    last_error = "Request failed."

    for _ in range(3):
        try:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 403:
                    raise RuntimeError("GitHub rate limit exceeded. Add a token or try again later.")
                if response.status >= 400:
                    text = await response.text()
                    raise RuntimeError(f"GitHub returned {response.status}: {text[:120]}")
                return await response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            await asyncio.sleep(1)

    raise RuntimeError(last_error)


async def search_users_all(
    session: aiohttp.ClientSession,
    query: str,
    headers: dict[str, str],
    max_pages: int = 10,
) -> list[dict]:
    url = f"{BASE_URL}/search/users"
    all_users: list[dict] = []

    for page in range(1, max_pages + 1):
        params = {"q": query, "per_page": 100, "page": page}
        data = await fetch(session, url, headers, params)
        users = data.get("items", [])

        if not users:
            break

        all_users.extend(users)

    return all_users


async def get_user_detail(
    session: aiohttp.ClientSession,
    username: str,
    headers: dict[str, str],
) -> dict:
    url = f"{BASE_URL}/users/{username}"
    return await fetch(session, url, headers)


async def fetch_all_details(
    users: list[dict],
    headers: dict[str, str],
    progress_callback: ProgressCallback | None = None,
) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [get_user_detail(session, user["login"], headers) for user in users]
        results: list[dict] = []

        for index, task in enumerate(asyncio.as_completed(tasks), start=1):
            result = await task
            results.append(result)
            if progress_callback:
                progress_callback(index, len(tasks), "Loading profile details...")

        return results


async def scrape_users(
    filters: SearchFilters,
    token: str,
    progress_callback: ProgressCallback | None = None,
) -> list[dict]:
    headers = build_headers(token)
    query = build_query(filters)

    async with aiohttp.ClientSession() as session:
        users = await search_users_all(session, query, headers)

    if not users:
        if progress_callback:
            progress_callback(0, 1, "No profiles matched this search.")
        return []

    if progress_callback:
        progress_callback(0, len(users), f"Found {len(users)} profiles. Loading details...")

    return await fetch_all_details(users, headers, progress_callback)
