import requests
import json
import os
from github import Github

def get_leetcode_stats(username):
    url = f"https://leetcode-stats-api.herokuapp.com/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['totalSolved'], data['rating']
    return None, None

def update_readme(github_token, repo_name):
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    
    # Get the current README content
    readme = repo.get_contents("README.md")
    content = readme.decoded_content.decode()

    # Update LeetCode stats
    solved, rating = get_leetcode_stats("Hardik_8491")
    if solved and rating:
        content = content.replace("🎯 LeetCode Rating</td>\n      <td>1241", f"🎯 LeetCode Rating</td>\n      <td>{rating}")
        content = content.replace("💻 DSA Questions Solved</td>\n      <td>500+", f"💻 DSA Questions Solved</td>\n      <td>{solved}")

    # Update GitHub stats (you'll need to implement this part)
    # ...

    # Commit changes
    repo.update_file(readme.path, "Update README stats", content, readme.sha)

if __name__ == "__main__":
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name = "Hardik8491/Hardik8491"
    update_readme(github_token, repo_name)