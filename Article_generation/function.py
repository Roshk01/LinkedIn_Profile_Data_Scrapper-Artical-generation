# function.py
import os
from typing import List, Dict
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = genai.GenerativeModel("models/gemini-2.5-flash")


#Your system & article prompt (UNTOUCHED)
SYSTEM_STYLE = (
    "You are an expert technical writer for software engineers. "
    "Write clear, accurate, well-structured articles with examples and code snippets when appropriate. "
    "Prefer practical guidance over fluff. Use Markdown with headings, lists, and code blocks."
)

_ARTICLE_PROMPT = """{system}

Write a {length}-word technical article for software engineers.

Title: {title}
Brief/Notes: {brief}

Audience level: {level}
Must include:
- An engaging intro (2–3 sentences) with context and why it matters
- A concise TL;DR
- 3–6 section headings with clear progression
- At least one short code example if relevant
- A "Common pitfalls" or "Gotchas" section when applicable
- A final "Key takeaways" list (3–6 bullets)
- Use clean Markdown. Avoid HTML. No images or external links.

Output strictly as Markdown, starting with '# {title}'.
"""


# Parse user block: "title | brief"
def parse_input(block: str) -> List[Dict[str, str]]:
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        if "|" in s:
            title, brief = s.split("|", 1)
            rows.append({"title": title.strip(), "brief": brief.strip()})
        else:
            rows.append({"title": s.strip(), "brief": ""})
    return rows


# Single article generator
def generate_one_article(title: str, brief: str, length: int = 800, level: str = "intermediate"):
    prompt = _ARTICLE_PROMPT.format(
        system=SYSTEM_STYLE,
        length=length,
        title=title,
        brief=brief,
        level=level,
    )

    response = MODEL.generate_content(prompt)
    md = (response.text or "").strip()

    return {
        "title": title,
        "brief": brief,
        "markdown": md
    }


# Batch generator
def generate_articles(input_text: str, limit: int = 10, length: int = 800, level: str = "intermediate"):
    rows = parse_input(input_text)
    rows = rows[:limit]

    results = []
    for item in rows:
        article = generate_one_article(item["title"], item["brief"], length, level)
        results.append(article)
    return results
