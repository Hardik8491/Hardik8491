import requests
import json
import os
from github import Github
from datetime import datetime

def get_leetcode_stats(username):
    url = f"https://leetcode-stats-api.herokuapp.com/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['totalSolved'], data['rating']
    return None, None

def get_github_stats(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['public_repos'], data['followers'], data['following']
    return None, None, None

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
        content = content.replace("💻 DSA Questions Solved</td>\n      <td>500+", f"💻 DSA Questions Solved</td>\n      <td>{solved}+")

    # Update GitHub stats
    repos, followers, following = get_github_stats("Hardik8491")
    if repos and followers and following:
        content = content.replace("https://github-readme-stats.vercel.app/api?username=Hardik8491&show_icons=true&theme=midnight-purple", 
                                  f"https://github-readme-stats.vercel.app/api?username=Hardik8491&show_icons=true&theme=midnight-purple&count_private=true&include_all_commits=true")

    # Update current projects and learning
    current_projects = "Full-stack web application with AI integration"
    learning = "Advanced Machine Learning techniques and Cloud Architecture"
    content = content.replace("Network programming and ML projects", current_projects)
    content = content.replace("Machine Learning with Python & Network Programming", learning)

    # Update portfolio link
    portfolio_link = "https://hardikbhammar.dev"
    content = content.replace("https://hardik-dev.tech", portfolio_link)

    # Update fun fact
    fun_fact = "I can solve a Rubik's cube in under 2 minutes!"
    content = content.replace("I can't lie to others!", fun_fact)

    # Update last updated date
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    if "Last updated:" in content:
        content = content.replace("Last updated:.*", f"Last updated: {last_updated}")
    else:
        content += f"\n\n<p align='center'>Last updated: {last_updated}</p>"

    # Commit changes
    repo.update_file(readme.path, f"Update README stats - {last_updated}", content, readme.sha)

if __name__ == "__main__":
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name = "Hardik8491/Hardik8491"
    update_readme(github_token, repo_name)