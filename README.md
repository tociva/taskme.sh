# Taskmesh HTML site

Static marketing website for [taskme.sh](https://taskme.sh). The site uses
plain HTML and CSS in the browser. A dependency-free Python script combines
page source files with the shared header and footer.

## How the site works

Each page has two files:

- `.htm` is the editable source file.
- `.html` is the generated file deployed by Cloudflare Pages.

For example:

```text
product.htm   ← edit this file
product.html  ← generated output; do not edit directly
```

The generator intentionally does not overwrite an existing `.html` file. To
regenerate a page, remove only its generated `.html` file and run the generator
again.

```sh
cd html-site
python3 html.py
```

## Current structure

```text
html-site/
├── index.htm                    # Homepage source
├── index.html                   # Generated homepage
├── product.htm                  # Product page source
├── product.html                 # Generated product page
├── security.htm                 # Security page source
├── security.html                # Generated security page
├── integrations.htm             # Integrations page source
├── integrations.html            # Generated integrations page
├── use-cases.htm                # Use-cases page source
├── use-cases.html               # Generated use-cases page
├── blog/
│   ├── index.htm                # Blog listing source; add every new article here
│   ├── index.html               # Generated Blog listing
│   └── 2026/
│       ├── governed-bank-reconciliation.htm
│       ├── human-approval-ai-workflows.htm
│       └── agents-vs-deterministic-tools.htm
├── 404.htm                      # Not-found page source
├── 404.html                     # Generated not-found page
├── assets/
│   ├── taskmesh-logo-large.svg
│   └── taskmesh-small.svg
├── partials/
│   ├── top-section.html         # Document head and shared header/navigation
│   └── bottom-section.html      # Shared footer and closing document tags
├── html.py                      # Static-page generator and validation
├── styles.css                   # Styles shared by every page
├── sitemap.xml                  # Search-engine URL index
├── robots.txt                   # Crawler rules and sitemap location
├── llms.txt                     # Concise product information for AI systems
└── _headers                     # Cloudflare Pages response headers
```

The Python generator searches the entire `html-site` tree for `.htm` files,
including nested folders. This means sections such as `blog/2026/` do not need
separate build configuration.

## Anatomy of a page source file

Every `.htm` source begins with required metadata:

```html
<!-- title: Product | Taskmesh AI Workflow Platform -->
<!-- description: A concise and unique description of this page. -->
<!-- nav: product -->

<!-- taskmesh top section -->
    <main id="main-content">
      <!-- Page-specific content -->
    </main>
<!-- taskmesh bottom section -->
```

Article sources also include publication metadata:

```html
<!-- type: article -->
<!-- published: 2026-09-25 -->
<!-- updated: 2026-09-25 -->
<!-- author: Taskmesh -->
```

The generator validates that:

- `title`, `description`, and `nav` are present;
- page titles and descriptions are unique;
- the top and bottom markers occur exactly once and in the correct order;
- the page contains content between the markers; and
- the `nav` value is supported.

The generator inserts the shared document head, navigation, footer, canonical
URL, social metadata, structured data, active navigation state, and current
copyright year. Article metadata automatically produces `Article` JSON-LD,
Open Graph article fields, and the correct canonical URL.

## Linking pages

Use root-relative links everywhere. A root-relative link works from the
homepage and from any nested folder.

```html
<a href="/product.html">Product</a>
<a href="/security.html#approvals">Human approvals</a>
<a href="/blog/2026/governed-bank-reconciliation.html">Read article</a>
```

Do not link to `.htm` files. Browsers and search engines must receive the
generated `.html` files.

### Which file owns a link?

Links are organized according to their scope:

| Link scope | File to update |
| --- | --- |
| Appears in the header on every page | `partials/top-section.html` |
| Appears in the footer on every page | `partials/bottom-section.html` |
| Appears only on the homepage | `index.htm` |
| Appears on a section listing page | The section's `index.htm`, such as `blog/index.htm` |
| Appears only inside one article | That article's `.htm` source |
| Must be discoverable by search engines | `sitemap.xml` |
| Important product/reference content for AI systems | `llms.txt` |

This ownership rule avoids maintaining the same article link in every page.
The global navigation links to the Blog parent; the Blog parent links to every
article.

## Adding a normal inner page

For a new root-level page such as `architecture.html`:

1. Create `architecture.htm` beside `index.htm`.
2. Add the required metadata and section markers.
3. Link to it from the page that owns the relationship.
4. Add `https://taskme.sh/architecture.html` to `sitemap.xml`.
5. Run `python3 html.py` to create `architecture.html`.

If it must appear in the global navigation, also update the shared-navigation
files described below.

## Blog organization

Use one parent Blog index and organize article source files by publication
year:

```text
html-site/
└── blog/
    ├── index.htm
    ├── index.html
    ├── 2026/
    │   ├── governed-bank-reconciliation.htm
    │   └── governed-bank-reconciliation.html
    └── 2027/
        ├── another-article.htm
        └── another-article.html
```

The public URLs are:

```text
https://taskme.sh/blog/
https://taskme.sh/blog/2026/governed-bank-reconciliation.html
```

Use lowercase, descriptive, hyphen-separated filenames. Do not put dates in
the filename because the year folder already supplies chronological context.

Place article-specific images under a matching asset folder:

```text
assets/blog/governed-bank-reconciliation/
├── workflow-overview.svg
└── reconciliation-screen.webp
```

Reference them with root-relative paths:

```html
<img
  src="/assets/blog/governed-bank-reconciliation/workflow-overview.svg"
  alt="Bank reconciliation workflow in Taskmesh"
  width="1200"
  height="675"
>
```

## Blog section

The Blog section is already configured in the shared navigation, footer, and
Python generator. `blog/index.htm` is the parent listing and is the single
place where every published article must be indexed. Adding an article does
not require changing the global header, footer, or generator.

## Adding a new blog article

Example article:

```text
blog/2026/governed-bank-reconciliation.htm
```

Start with:

```html
<!-- title: Governed Bank Reconciliation with AI | Taskmesh -->
<!-- description: Learn how to reconcile bank transactions with controlled AI analysis, human review, and auditable accounting actions. -->
<!-- nav: blog -->
<!-- type: article -->
<!-- published: 2026-09-25 -->
<!-- updated: 2026-09-25 -->
<!-- author: Taskmesh -->

<!-- taskmesh top section -->
    <main id="main-content">
      <article>
        <header>
          <p class="eyebrow">Finance operations</p>
          <h1>Governed bank reconciliation with AI</h1>
          <p>Article introduction.</p>
        </header>

        <!-- Article sections -->
      </article>
    </main>
<!-- taskmesh bottom section -->
```

Then update the following files:

1. **Create the article source**

   ```text
   blog/2026/governed-bank-reconciliation.htm
   ```

2. **Add the article to its parent index**

   Edit `blog/index.htm` and add a card or list item linking to:

   ```html
   <a href="/blog/2026/governed-bank-reconciliation.html">
     Governed bank reconciliation with AI
   </a>
   ```

3. **Add the canonical URL to the sitemap**

   Edit `sitemap.xml`:

   ```xml
   <url>
     <loc>https://taskme.sh/blog/2026/governed-bank-reconciliation.html</loc>
     <lastmod>2026-09-25</lastmod>
   </url>
   ```

4. **Optionally promote the article**

   - Add it to `index.htm` only when it should be featured on the homepage.
   - Add it to `llms.txt` only when it is an important evergreen reference.
   - Add links from related articles when they genuinely help the reader.

5. **Regenerate the changed pages**

   - The new article has no `.html` file yet, so it is generated automatically.
   - Remove `blog/index.html` because its source listing was changed.
   - Remove `index.html` only if the homepage was updated.
   - Run `python3 html.py`.

The generator creates:

```text
blog/2026/governed-bank-reconciliation.html
blog/index.html
```

## Blog publishing checklist

Before publishing a new article, confirm:

- [ ] The source is inside `blog/<year>/`.
- [ ] The filename is lowercase and hyphen-separated.
- [ ] The title and description are unique.
- [ ] `type`, `published`, `updated`, and `author` metadata are present.
- [ ] The article contains one clear `<h1>`.
- [ ] The article is linked from `blog/index.htm`.
- [ ] All internal links are root-relative and target `.html` files.
- [ ] Images have useful alternative text, width, and height.
- [ ] The canonical URL is listed in `sitemap.xml`.
- [ ] Changed generated pages were removed before regeneration.
- [ ] `python3 html.py` completed successfully.

## Changing the shared header or footer

Edit:

- `partials/top-section.html` for document metadata, logo, or global navigation;
- `partials/bottom-section.html` for the shared footer; and
- `styles.css` for shared presentation.

A partial change affects every page. Because the generator does not overwrite
existing output, all generated `.html` counterparts must be removed before
running `python3 html.py` again. Never remove the `.htm` source files.

## Files that usually do not change for a new article

These files normally remain unchanged when publishing an individual post:

- `partials/top-section.html`
- `partials/bottom-section.html`
- `html.py`
- `robots.txt`
- `_headers`

They change only when the shared framework, navigation, crawler policy, or
deployment behavior changes.
