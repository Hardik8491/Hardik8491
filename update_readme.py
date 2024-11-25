import requests
import json
import os
import sys
import re
from github import Github
from datetime import datetime


def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile {
          ranking
        }
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    variables = {"username": username}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {}).get("matchedUser", {})
            rating = user_data.get("profile", {}).get("ranking", "N/A")
            total_solved = next(
                (item["count"] for item in user_data.get("submitStats", {}).get("acSubmissionNum", []) if item["difficulty"] == "All"),
                "N/A"
            )
            return total_solved, rating
        else:
            print(f"LeetCode API returned an error: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error fetching LeetCode stats: {e}", file=sys.stderr)
        return None, None


def get_github_stats(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("public_repos", "N/A"), data.get("followers", "N/A"), data.get("following", "N/A")
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}", file=sys.stderr)
        return None, None, None


def update_readme(github_token, repo_name):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        readme = repo.get_contents("README.md")
        content = readme.decoded_content.decode()

        # Update LeetCode stats
        solved, rating = get_leetcode_stats("Hardik_8491")
        if solved != "N/A" and rating != "N/A":
            content = re.sub(r'<td id="leetcode-rating">.*?</td>', f'<td id="leetcode-rating">{rating}</td>', content)
            content = re.sub(r'<td id="dsa-solved">.*?</td>', f'<td id="dsa-solved">{solved}+</td>', content)

        # Update GitHub stats
        repos, followers, following = get_github_stats("Hardik8491")
        if repos != "N/A":
            content = re.sub(
                r"https://github-readme-stats\.vercel\.app/api\?username=Hardik8491.*",
                f"https://github-readme-stats.vercel.app/api?username=Hardik8491&show_icons=true&theme=midnight-purple&count_private=true&include_all_commits=true",
                content,
            )

        # Update current projects and learning
        content = content.replace("Network programming and ML projects", "Full-stack web application with AI integration")
        content = content.replace("Machine Learning with Python & Network Programming", "Advanced Machine Learning techniques and Cloud Architecture")

        # Update portfolio link
        content = content.replace("https://hardik-dev.tech", "https://hardikbhammar.dev")

        # Update fun fact
        content = content.replace("I can't lie to others!", "I can solve a Rubik's cube in under 2 minutes!")

        # Update last updated date
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        if "Last updated:" in content:
            content = re.sub(r"Last updated:.*", f"Last updated: {last_updated}", content)
        else:
            content += f"\n\n<p align='center'>Last updated: {last_updated}</p>"

        # Commit changes
        repo.update_file(readme.path, f"Update README stats - {last_updated}", content, readme.sha)
        print("README updated successfully")

    except Exception as e:
        print(f"Error updating README: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        sys.exit(1)
    repo_name = "Hardik8491/Hardik8491"
    update_readme(github_token, repo_name)
