#!/usr/bin/env python3

import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
PARTIALS_DIR = ROOT / "partials"
TOP_PATH = PARTIALS_DIR / "top-section.html"
BOTTOM_PATH = PARTIALS_DIR / "bottom-section.html"

SITE_URL = "https://taskme.sh"
START_MARKER = "<!-- taskmesh top section -->"
END_MARKER = "<!-- taskmesh bottom section -->"
SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    ".cache",
    ".vercel",
    "partials",
}
NAV_ITEMS = ("home", "product", "security", "integrations", "use-cases", "blog")
REQUIRED_TOKENS = (
    "taskmesh-page-title",
    "taskmesh-page-description",
    "taskmesh-canonical-url",
    "taskmesh-page-class",
    "taskmesh-og-type",
    "taskmesh-article-meta",
    "taskmesh-structured-data",
    "taskmesh-nav-home",
    "taskmesh-nav-product",
    "taskmesh-nav-security",
    "taskmesh-nav-integrations",
    "taskmesh-nav-use-cases",
    "taskmesh-nav-blog",
)


def fail(message: str) -> None:
    print(f"\nTaskmesh site build failed.\n\n{message}\n", file=sys.stderr)
    raise SystemExit(1)


def assert_project_root() -> None:
    missing = [path for path in (TOP_PATH, BOTTOM_PATH) if not path.exists()]
    if not missing:
        return

    fail(
        "\n".join(
            (
                "The generator must be run from the html-site project root.",
                "",
                f"Current directory: {ROOT}",
                "",
                "Missing:",
                *(f"  {path}" for path in missing),
                "",
                "Run:",
                "  cd /path/to/taskmesh/html-site",
                "  python3 html.py",
            )
        )
    )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def walk(root: Path) -> list[Path]:
    output: list[Path] = []
    for dir_path, dir_names, file_names in os.walk(root):
        dir_names[:] = sorted(name for name in dir_names if name not in SKIP_DIRS)
        for file_name in sorted(file_names):
            if file_name.endswith(".htm"):
                output.append(Path(dir_path) / file_name)
    return sorted(output)


def extract_meta(source: str, key: str) -> str | None:
    match = re.search(rf"<!--\s*{re.escape(key)}:\s*(.*?)\s*-->", source)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def replace_token(source: str, token: str, value: str) -> str:
    return source.replace(f"<!-- {token} -->", value)


def route_for(file_path: Path) -> str:
    relative_path = file_path.relative_to(ROOT).as_posix()
    html_path = f"{relative_path[:-4]}.html"
    if html_path == "index.html":
        return "/"
    if html_path.endswith("/index.html"):
        return f"/{html_path[:-10]}"
    return f"/{html_path}"


def build_structured_data(page: dict) -> str:
    graph = [
        {
            "@type": "Organization",
            "@id": f"{SITE_URL}/#organization",
            "name": "Taskmesh",
            "url": f"{SITE_URL}/",
            "description": (
                "Taskmesh is a platform for building, running, and governing "
                "AI agents and business workflows."
            ),
        },
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "url": f"{SITE_URL}/",
            "name": "Taskmesh",
            "publisher": {"@id": f"{SITE_URL}/#organization"},
        },
        {
            "@type": "WebPage",
            "@id": f"{page['canonical']}#webpage",
            "url": page["canonical"],
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
            "about": {"@id": f"{SITE_URL}/#software"},
        },
    ]

    if page["nav"] in {"home", "product"}:
        graph.append(
            {
                "@type": "SoftwareApplication",
                "@id": f"{SITE_URL}/#software",
                "name": "Taskmesh",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "url": f"{SITE_URL}/",
                "description": (
                    "A governed platform for designing, approving, running, and "
                    "monitoring AI-powered workflows."
                ),
                "provider": {"@id": f"{SITE_URL}/#organization"},
            }
        )

    if page["type"] == "article":
        graph.append(
            {
                "@type": "Article",
                "@id": f"{page['canonical']}#article",
                "headline": page["title"],
                "description": page["description"],
                "datePublished": page["published"],
                "dateModified": page["updated"],
                "author": {
                    "@type": "Organization",
                    "name": page["author"],
                    "url": f"{SITE_URL}/",
                },
                "publisher": {"@id": f"{SITE_URL}/#organization"},
                "mainEntityOfPage": {"@id": f"{page['canonical']}#webpage"},
            }
        )

    value = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False,
        indent=2,
    )
    return value.replace("<", "\\u003c")


def validate_page(file_path: Path, source: str) -> dict:
    relative_path = file_path.relative_to(ROOT).as_posix()
    errors: list[str] = []
    top_count = source.count(START_MARKER)
    bottom_count = source.count(END_MARKER)

    if top_count != 1:
        errors.append(f"expected one top marker; found {top_count}")
    if bottom_count != 1:
        errors.append(f"expected one bottom marker; found {bottom_count}")

    start_index = source.find(START_MARKER)
    end_index = source.find(END_MARKER)
    if start_index >= 0 and end_index >= 0 and start_index >= end_index:
        errors.append("the top marker must appear before the bottom marker")

    title = extract_meta(source, "title")
    description = extract_meta(source, "description")
    nav = extract_meta(source, "nav")
    page_type = extract_meta(source, "type") or "webpage"
    published = extract_meta(source, "published")
    updated = extract_meta(source, "updated") or published
    author = extract_meta(source, "author")

    if not title:
        errors.append("missing required title metadata")
    if not description:
        errors.append("missing required description metadata")
    if not nav:
        errors.append("missing required nav metadata")
    if nav and nav not in NAV_ITEMS:
        errors.append(f"unknown nav value: {nav}")
    if page_type not in {"webpage", "article"}:
        errors.append(f"unknown page type: {page_type}")
    if page_type == "article":
        if not published:
            errors.append("article is missing required published metadata")
        if not author:
            errors.append("article is missing required author metadata")
        for label, value in (("published", published), ("updated", updated)):
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"article {label} date must use YYYY-MM-DD")

    if start_index >= 0 and end_index >= 0:
        body = source[start_index + len(START_MARKER) : end_index].strip()
        if not body:
            errors.append("page content between markers is empty")

    if errors:
        return {"relative_path": relative_path, "errors": errors}

    route = route_for(file_path)
    return {
        "relative_path": relative_path,
        "file_path": file_path,
        "out_path": file_path.with_suffix(".html"),
        "title": title,
        "description": description,
        "nav": nav,
        "type": page_type,
        "published": published,
        "updated": updated,
        "author": author,
        "route": route,
        "canonical": f"{SITE_URL}{route}",
        "body": source[start_index + len(START_MARKER) : end_index].strip(),
        "errors": [],
    }


def validate_unique_meta(pages: list[dict]) -> list[str]:
    errors: list[str] = []
    for field in ("title", "description"):
        seen: dict[str, str] = {}
        for page in pages:
            value = page[field]
            if value in seen:
                errors.append(
                    f"{page['relative_path']} duplicates {field} from {seen[value]}"
                )
            else:
                seen[value] = page["relative_path"]
    return errors


def render_page(page: dict, top_base: str, bottom_base: str) -> str:
    top = top_base
    page_classes = [f"page-{page['nav']}"]
    if page["type"] == "article":
        page_classes.append("page-article")

    article_meta = ""
    if page["type"] == "article":
        article_meta = "\n".join(
            (
                f'    <meta property="article:published_time" content="{escape_html(page["published"])}">',
                f'    <meta property="article:modified_time" content="{escape_html(page["updated"])}">',
                f'    <meta property="article:author" content="{escape_html(page["author"])}">',
            )
        )

    replacements = {
        "taskmesh-page-title": escape_html(page["title"]),
        "taskmesh-page-description": escape_html(page["description"]),
        "taskmesh-canonical-url": escape_html(page["canonical"]),
        "taskmesh-page-class": escape_html(" ".join(page_classes)),
        "taskmesh-og-type": "article" if page["type"] == "article" else "website",
        "taskmesh-article-meta": article_meta,
        "taskmesh-structured-data": build_structured_data(page),
    }

    for token, value in replacements.items():
        top = replace_token(top, token, value)

    for nav in NAV_ITEMS:
        attributes = ' aria-current="page"' if page["nav"] == nav else ""
        top = replace_token(top, f"taskmesh-nav-{nav}", attributes)

    footer = replace_token(
        bottom_base,
        "taskmesh-current-year",
        str(datetime.now(timezone.utc).year),
    )
    return f"{top.strip()}\n{page['body']}\n{footer.strip()}\n"


def main() -> None:
    assert_project_root()

    top_base = read(TOP_PATH)
    bottom_base = read(BOTTOM_PATH)
    missing_tokens = [
        token
        for token in REQUIRED_TOKENS
        if f"<!-- {token} -->" not in top_base
    ]
    if "<!-- taskmesh-current-year -->" not in bottom_base:
        missing_tokens.append("taskmesh-current-year")
    if missing_tokens:
        fail(
            "Missing partial token(s):\n"
            + "\n".join(f"  {token}" for token in missing_tokens)
        )

    results = [validate_page(path, read(path)) for path in walk(ROOT)]
    page_errors = [result for result in results if result["errors"]]
    if page_errors:
        fail(
            "\n\n".join(
                f"{result['relative_path']}:\n"
                + "\n".join(f"  - {error}" for error in result["errors"])
                for result in page_errors
            )
        )

    duplicate_errors = validate_unique_meta(results)
    if duplicate_errors:
        fail("\n".join(f"- {error}" for error in duplicate_errors))

    generated = 0
    skipped = 0
    for page in results:
        output_path = page["out_path"]
        relative_output = output_path.relative_to(ROOT).as_posix()
        if output_path.exists():
            print(f"Skipped existing: {relative_output}")
            skipped += 1
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            render_page(page, top_base, bottom_base),
            encoding="utf-8",
        )
        print(f"Generated: {relative_output}")
        generated += 1

    print(f"Done. {generated} generated, {skipped} skipped.")


if __name__ == "__main__":
    main()
