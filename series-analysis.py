#!/usr/bin/env python3
"""
Display episode ratings for a TV show using the TVMaze API.

Usage:
    python tvmaze_ratings.py "Breaking Bad"
    python tvmaze_ratings.py "The Office"
"""

import sys
import requests
import matplotlib.pyplot as plt
import numpy as np
import json

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
    print(json.dumps(resp.json(), indent=4))
    return resp.json()


def get_number_of_seasons(episodes: list[dict]) -> int:
    num_seasons = 0
    current_season = None
    for ep in episodes:
        season = ep["season"]
        if season != current_season:
            current_season = season
            num_seasons += 1
    return num_seasons


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


def plot_ratings(show_name: str, episodes: list[dict]) -> None:

    # Get the number of seasons and grouped episodes
    grouped_episodes = group_episodes(episodes)
    num_seasons = get_number_of_seasons(episodes)

    # create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    positions = list(range(1, num_seasons + 1))
    ratings_per_season = [
            [d["rating"]["average"] for d in season]
            for season in grouped_episodes
            ]
    # print(json.dumps(ratings_per_season, indent=4))

    # Create boxplot
    VP = ax1.boxplot(ratings_per_season, positions=positions, widths=1, patch_artist=True,
                    showmeans=False, showfliers=False,
                    medianprops={"color": "white", "linewidth": 0.5},
                    boxprops={"facecolor": "C0", "edgecolor": "white",
                              "linewidth": 0.5},
                    whiskerprops={"color": "C0", "linewidth": 1.5},
                    capprops={"color": "C0", "linewidth": 1.5})

    ax1.set(xlim=(0, num_seasons + 1), xticks=np.arange(1, num_seasons + 1),
           xticklabels=[f"S{i:02d}" for i in range(1, num_seasons + 1)],
           ylim=(0, 11), yticks=np.arange(1, 11),
           xlabel="Season", ylabel="Rating",
           title=f"Episode Rating Distribution — {show_name}")

    plt.show()


def group_episodes(episodes: list[dict]) -> list[list[dict]]:
    grouped = []
    current_season = 1
    num_seasons = get_number_of_seasons(episodes)
    filtered = [
            {k: v for k, v in d.items() if k in {"season", "number", "name", "rating"} }
            for d in episodes
            ]
    print(json.dumps(filtered, indent=4))
    for i in range(1, num_seasons + 1):
        grouped.append([ep for ep in filtered if ep["season"] == i])

    print(json.dumps(grouped, indent=4))
    return grouped


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
    plot_ratings(official_name, episodes)


if __name__ == "__main__":
    main()
