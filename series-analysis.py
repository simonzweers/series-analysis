#!/usr/bin/env python3
"""
Display episode ratings for a TV show using the TVMaze API.

Usage:
    python tvmaze_ratings.py "Breaking Bad"
    python tvmaze_ratings.py "The Office"
"""

import sys
import requests


def get_show_id(show_name: str) -> tuple[int, str]:
    """Search TVMaze for a show and return its ID and official name."""
    resp = requests.get(
        "https://api.tvmaze.com/singlesearch/shows",
        params={"q": show_name},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["id"], data["name"]


def get_episodes(show_id: int) -> list[dict]:
    """Fetch all episodes for a given show ID."""
    resp = requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodes")
    resp.raise_for_status()
    return resp.json()


def print_ratings(show_name: str, episodes: list[dict]) -> None:
    print(f"\nEpisode ratings for: {show_name}\n" + "-" * 50)

    current_season = None
    for ep in episodes:
        season = ep["season"]
        number = ep["number"]
        title = ep["name"]
        rating = ep["rating"]["average"]

        if season != current_season:
            current_season = season
            print(f"\nSeason {season}")

        rating_str = f"{rating:.1f}" if rating is not None else "N/A"
        print(f"  S{season:02d}E{number:02d}  {rating_str:>4}  {title}")

    # Simple summary: average rating and top episode
    rated = [ep for ep in episodes if ep["rating"]["average"] is not None]
    if rated:
        avg = sum(ep["rating"]["average"] for ep in rated) / len(rated)
        best = max(rated, key=lambda ep: ep["rating"]["average"])
        print("\n" + "-" * 50)
        print(f"Average rating: {avg:.2f}")
        print(
            f"Top episode:    S{best['season']:02d}E{best['number']:02d} "
            f"\"{best['name']}\" ({best['rating']['average']})"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python tvmaze_ratings.py \"<show name>\"")
        sys.exit(1)

    show_name = " ".join(sys.argv[1:])

    try:
        show_id, official_name = get_show_id(show_name)
        episodes = get_episodes(show_id)
    except requests.exceptions.HTTPError:
        print(f"Could not find a show matching: {show_name}")
        sys.exit(1)

    print_ratings(official_name, episodes)


if __name__ == "__main__":
    main()
