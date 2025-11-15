import os
import requests
import datetime
import base64

USERNAME = os.getenv("GITHUB_USERNAME")

API_BASE = "https://api.github.com"


def get_user_stats(username):
    user = requests.get(f"{API_BASE}/users/{username}").json()
    repos = requests.get(f"{API_BASE}/users/{username}/repos?per_page=100").json()

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    # get top languages
    lang_count = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + 1

    top_langs = ", ".join(sorted(lang_count, key=lang_count.get, reverse=True)[:5])

    return {
        "name": user.get("name", username),
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "stars": total_stars,
        "languages": top_langs if top_langs else "—",
        "updated_date": datetime.datetime.now().strftime("%d %b %Y")
    }


def extract_readme_summary(username, repo_name):
    """Fetch README from GitHub API and extract first paragraph."""
    readme_url = f"{API_BASE}/repos/{username}/{repo_name}/readme"
    r = requests.get(readme_url)

    if r.status_code != 200:
        return None  # no readme found

    readme_json = r.json()
    content = readme_json.get("content", "")
    if not content:
        return None

    try:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
    except:
        return None

    # Extract first paragraph
    paragraphs = [p.strip() for p in decoded.split("\n\n") if p.strip()]
    if not paragraphs:
        return None

    summary = paragraphs[0].replace("\n", " ").strip()

    if len(summary) > 300:
        summary = summary[:300] + "..."

    return summary


def fetch_repositories(username):
    """Get all repos with description and readme summary."""
    url = f"{API_BASE}/users/{username}/repos?per_page=100&sort=updated"
    repos = requests.get(url).json()

    project_list = []

    for repo in repos:
        name = repo["name"]
        stars = repo["stargazers_count"]
        html_url = repo["html_url"]
        description = repo.get("description") or ""

        # get readme summary
        readme_summary = extract_readme_summary(username, name)

        summary = readme_summary or description or "No description available."

        project_list.append({
            "name": name,
            "stars": stars,
            "url": html_url,
            "summary": summary
        })

    # Sort by stars (descending)
    project_list = sorted(project_list, key=lambda x: x["stars"], reverse=True)

    return project_list


def generate_projects_md(projects):
    """Turn project info into Markdown."""
    if not projects:
        return "No public repositories found."

    lines = ["## 🧩 Projects (Auto-Generated)\n"]

    for p in projects:
        lines.append(
            f"- **[{p['name']}]({p['url']})** ⭐{p['stars']} — {p['summary']}"
        )

    return "\n".join(lines)


def generate_resume():
    if not USERNAME:
        raise Exception("GITHUB_USERNAME not set!")

    print(f"Fetching GitHub stats for {USERNAME}...")

    stats = get_user_stats(USERNAME)
    projects = fetch_repositories(USERNAME)
    projects_md = generate_projects_md(projects)

    with open("templates/resume_template.md") as f:
        template = f.read()

    # replace placeholders
    for key, val in stats.items():
        template = template.replace(f"{{{{{key}}}}}", str(val))

    template = template.replace("{{projects}}", projects_md)

    with open("Resume.md", "w") as f:
        f.write(template)

    print("Resume.md updated successfully!")


if __name__ == "__main__":
    generate_resume()
