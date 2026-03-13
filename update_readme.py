import requests
import os
import sys
import re
from github import Github
from datetime import datetime


NEXT_GEN_ROTATIONS = {
    "current-focus": [
        "Shipping AI-native full-stack products with secure APIs and strong observability.",
        "Building production-ready GenAI workflows that create real user and business value.",
        "Designing scalable web platforms that combine modern UX with intelligent automation.",
        "Engineering reliable backend systems that power LLM-driven product experiences.",
    ],
    "currently-building": [
        "RAG applications with vector search, caching, and evaluation-driven iteration.",
        "Agent-enabled tools that call APIs, automate workflows, and improve productivity.",
        "Full-stack dashboards with AI copilots, role-based access, and analytics.",
        "Intelligent assistants that connect product logic, knowledge bases, and user actions.",
    ],
    "learning-next": [
        "Multi-agent orchestration patterns and robust tool-routing strategies.",
        "Cloud-native MLOps pipelines for model lifecycle and deployment reliability.",
        "Inference optimization, latency reduction, and cost-aware LLM architecture.",
        "Evaluation frameworks for quality, safety, and grounded AI responses.",
    ],
    "availability": [
        "Open to high-impact Full-Stack and GenAI engineering opportunities.",
        "Open for internships, freelance builds, and product-focused collaborations.",
        "Open to teams building serious AI products beyond proof-of-concept demos.",
        "Available for projects where end-to-end ownership and execution speed matter.",
    ],
    "fun-fact": [
        "I can move from idea to production MVP across frontend, backend, and AI layers.",
        "I enjoy turning complex AI concepts into simple user experiences.",
        "I treat prompt design and API design with the same engineering discipline.",
        "I optimize for both shipping speed and long-term maintainability.",
    ],
    "ai-mission": [
        "Turn complex workflows into intelligent, user-friendly products powered by practical GenAI.",
        "Use AI to remove friction in real workflows, not just generate flashy demos.",
        "Bridge product thinking and LLM capability into scalable, reliable applications.",
        "Build assistive systems that help users decide faster and execute better.",
    ],
    "architecture-theme": [
        "Agent-ready services with clean API contracts and retrieval-first design.",
        "Event-aware backend architecture with modular AI inference layers.",
        "Composable microservices that integrate tools, memory, and model context.",
        "Scalable service boundaries for rapid iteration across AI and product teams.",
    ],
    "shipping-rhythm": [
        "Rapid prototyping, measurable validation, and production hardening.",
        "Small release cycles with telemetry-driven improvements.",
        "Build fast, test deeply, and ship with confidence.",
        "Prototype quickly, evaluate outcomes, then scale what works.",
    ],
    "focus-track": [
        "AI copilots, internal automation tools, and data-rich product platforms.",
        "LLM-powered workflow assistants for business and developer productivity.",
        "Smart interfaces that combine retrieval, reasoning, and action.",
        "Full-stack AI systems focused on measurable outcomes in production.",
    ],
}


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
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        user_data = data.get("data", {}).get("matchedUser", {})
        ranking = user_data.get("profile", {}).get("ranking", "N/A")
        total_solved = next(
            (
                item.get("count")
                for item in user_data.get("submitStats", {}).get("acSubmissionNum", [])
                if item.get("difficulty") == "All"
            ),
            "N/A",
        )
        return str(total_solved), str(ranking)
    except Exception as e:
        print(f"Error fetching LeetCode stats: {e}", file=sys.stderr)
        return "N/A", "N/A"


def get_github_stats(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        return (
            str(data.get("public_repos", "N/A")),
            str(data.get("followers", "N/A")),
            str(data.get("following", "N/A")),
        )
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}", file=sys.stderr)
        return "N/A", "N/A", "N/A"


def get_total_github_stars(username):
    url = f"https://api.github.com/users/{username}/repos"
    page = 1
    total_stars = 0

    try:
        while True:
            response = requests.get(
                url,
                params={"per_page": 100, "page": page},
                timeout=20,
            )
            response.raise_for_status()
            repos = response.json()
            if not repos:
                break

            total_stars += sum(repo.get("stargazers_count", 0) for repo in repos)
            page += 1

        return str(total_stars)
    except Exception as e:
        print(f"Error fetching total stars: {e}", file=sys.stderr)
        return "N/A"


def replace_by_id(content, element_id, value):
    pattern = rf'(<[^>]+id="{re.escape(element_id)}"[^>]*>)(.*?)(</[^>]+>)'
    return re.sub(pattern, rf"\1{value}\3", content, flags=re.DOTALL)


def get_rotation_text(field_name, now):
    options = NEXT_GEN_ROTATIONS.get(field_name, [])
    if not options:
        return ""

    # Rotate profile messaging monthly so the profile stays fresh through the year.
    index = (now.month - 1) % len(options)
    return options[index]


def update_readme(github_token, repo_name):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        readme = repo.get_contents("README.md")
        content = readme.decoded_content.decode()
        now = datetime.now()

        # Update LeetCode stats
        solved, rating = get_leetcode_stats("Hardik_8491")
        content = replace_by_id(content, "leetcode-ranking", rating)
        content = replace_by_id(content, "leetcode-solved", solved)

        # Update GitHub stats
        repos, followers, _following = get_github_stats("Hardik8491")
        stars = get_total_github_stars("Hardik8491")
        content = replace_by_id(content, "github-repos", repos)
        content = replace_by_id(content, "github-followers", followers)
        content = replace_by_id(content, "github-stars", stars)

        # Keep profile highlights and next-gen dashboard fresh with monthly rotations.
        rotating_ids = [
            "current-focus",
            "currently-building",
            "learning-next",
            "availability",
            "fun-fact",
            "ai-mission",
            "architecture-theme",
            "shipping-rhythm",
            "focus-track",
        ]
        for field_id in rotating_ids:
            rotated_value = get_rotation_text(field_id, now)
            if rotated_value:
                content = replace_by_id(content, field_id, rotated_value)

        # Update last updated date
        last_updated = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        content = re.sub(
            r'(<p align="center" id="last-updated"><i>Last updated: )(.*?)(</i></p>)',
            rf"\1{last_updated}\3",
            content,
            flags=re.DOTALL,
        )

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
