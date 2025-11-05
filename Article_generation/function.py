import pandas as pd
import google.generativeai as genai
import os


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]  # supply via Streamlit Secrets -> env in app

_SYSTEM_STYLE = (
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

_GEN_MODEL = None

def _get_gemini_model():
    global _GEN_MODEL
    if _GEN_MODEL is None:
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in environment.")
        genai.configure(api_key=api_key)
        _GEN_MODEL = genai.GenerativeModel("gemini-1.5-flash")
    return _GEN_MODEL

# -------- API fetching & normalization --------

def _normalize_titles_payload(payload: Union[Dict, List]) -> List[Dict[str, str]]:
    """
    Accepts flexible API payloads and returns a list of {title, brief}.
    Supported shapes:
      1) ["Title A", "Title B", ...]
      2) [{"title": "...", "brief": "..."}, ...]
      3) {"titles": ["..."]} or {"titles": [{"title": "..."}]}
      4) {"items": [{"title": "...", "brief": "..."}], ...}
      5) {"data": [{"title": "...", "brief": "..."}], ...}
    """
    rows: List[Dict[str, str]] = []

    def push(title, brief=""):
        title = (str(title) if title is not None else "").strip()
        brief = (str(brief) if brief is not None else "").strip()
        if title:
            rows.append({"title": title, "brief": brief})

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, str):
                push(item)
            elif isinstance(item, dict):
                push(item.get("title") or item.get("name") or item.get("heading"), item.get("brief", ""))
    elif isinstance(payload, dict):
        for key in ("titles", "items", "data", "results"):
            if key in payload and isinstance(payload[key], list):
                for item in payload[key]:
                    if isinstance(item, str):
                        push(item)
                    elif isinstance(item, dict):
                        push(item.get("title") or item.get("name") or item.get("heading"), item.get("brief", ""))
                break
        # fallback single fields
        if not rows and "title" in payload:
            push(payload.get("title"), payload.get("brief", ""))

    # de-dup by title
    seen = set()
    out = []
    for r in rows:
        t = r["title"]
        if t and t not in seen:
            seen.add(t)
            out.append(r)
    return out

def fetch_titles_from_api(endpoint: str, timeout: int = 30) -> List[Dict[str, str]]:
    """
    GETs your endpoint and normalizes into [{title, brief}, ...].
    """
    resp = requests.get(endpoint, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    titles = _normalize_titles_payload(payload)
    if not titles:
        raise RuntimeError("No titles found in API response.")
    return titles

# -------- Gemini generation --------

def generate_article_gemini(
    title: str,
    brief: str = "",
    length_words: int = 900,
    level: str = "intermediate",
    retries: int = 2,
    sleep_between: float = 0.5,
) -> Dict[str, str]:
    model = _get_gemini_model()
    prompt = _ARTICLE_PROMPT.format(
        system=_SYSTEM_STYLE,
        length=length_words,
        title=title.strip(),
        brief=(brief or "").strip(),
        level=level.strip(),
    )
    last_err = None
    for _ in range(retries + 1):
        try:
            resp = model.generate_content(prompt)
            md = (resp.text or "").strip()
            if not md:
                raise RuntimeError("Empty response from model.")
            return {
                "title": title.strip(),
                "brief": (brief or "").strip(),
                "slug": slugify(title)[:80] or f"article-{int(time.time())}",
                "markdown": md,
            }
        except Exception as e:
            last_err = e
            time.sleep(sleep_between)
    raise RuntimeError(f"Gemini generation failed for '{title}': {last_err}")

def generate_articles_batch(
    titles_and_briefs: List[Dict[str, str]],
    length_words: int = 900,
    level: str = "intermediate",
) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for tb in titles_and_briefs:
        results.append(
            generate_article_gemini(
                title=tb["title"],
                brief=tb.get("brief", ""),
                length_words=length_words,
                level=level,
            )
        )
    return results

def generate_articles_from_api(
    api_url: str,
    limit: int = 10,
    length_words: int = 900,
    level: str = "intermediate",
) -> List[Dict[str, str]]:
    """
    One call that:
      - fetches titles from your API,
      - takes the first `limit`,
      - generates articles with Gemini,
      - returns list of dicts {title, brief, slug, markdown}.
    """
    titles = fetch_titles_from_api(api_url)
    if limit and limit > 0:
        titles = titles[:limit]
    return generate_articles_batch(titles, length_words=length_words, level=level)

def articles_to_dataframe(articles: List[Dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(articles, columns=["title", "brief", "slug", "markdown"])

