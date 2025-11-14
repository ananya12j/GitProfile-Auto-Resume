import requests
import datetime
import os

USERNAME = os.getenv("GITHUB_USERNAME")

def get_user_stats(username):
    print(f"Fetching GitHub stats for: {username}")

    user = requests.get(f"https://api.github.com/users/{username}").json()
    repos = requests.get(f"https://api.github.com/users/{username}/repos").json()

    total_stars = sum([repo.get("stargazers_count", 0) for repo in repos])

    language_counts = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1

    top_languages = ", ".join(sorted(language_counts, key=language_counts.get, reverse=True)[:5])

    return {
        "name": user.get("name", username),
        "public_repos": user.get("public_repos"),
        "followers": user.get("followers"),
        "following": user.get("following"),
        "stars": total_stars,
        "languages": top_languages,
        "updated_date": datetime.datetime.now().strftime("%d %b %Y")
    }

def generate_resume(data):
    with open("templates/resume_template.md", "r") as f:
        template = f.read()

    for key, value in data.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))

    with open("Resume.md", "w") as f:
        f.write(template)

    print("Resume.md updated successfully!")

if __name__ == "__main__":
    if not USERNAME:
        raise Exception("GITHUB_USERNAME environment variable not set!")

    stats = get_user_stats(USERNAME)
    generate_resume(stats)
