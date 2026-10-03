# SBG Infratech Solutions – website

Pushing to `main` builds and publishes the site automatically (GitHub Actions).

## Where to edit what
| I want to change… | Edit this |
|---|---|
| Product text, titles, lists | `content.json` → `categories` |
| Phone, email, address, tagline | `content.json` → `company` |
| Social links (`""` hides an icon) | `content.json` → `social` |
| Hero heading / intro text | `content.json` → `hero` |
| Page title, description, website address | `content.json` → `site` |
| Add a photo | drop the original in `images/`, then use its name (no extension) in `content.json` |
| Colours, fonts, spacing | `static/style.css` |
| Dropdown / form behaviour | `static/script.js` |
| Page layout and HTML | `templates/` (see below) |
| Add a social platform | add its icon to `data/icons.json`, then a link in `content.json` |

## Templates (`templates/`)
    index.html              page skeleton – lists the sections in order
    partials/head.html      title, SEO tags, fonts, CSS
    partials/header.html    top bar, Services dropdown, WhatsApp button
    partials/hero.html      first screen
    partials/overview.html  quick product links
    partials/category.html  one category section (loops over products)
    partials/product.html   one product (text, lists, photos / gallery)
    partials/contact.html   address, social icons, enquiry form
    partials/footer.html    footer
    partials/macros.html    reusable pieces: responsive photo, icons
`{{ name }}` prints a value from `content.json`; `{% for %}` / `{% if %}` are loops and conditions.

## Preview on your computer
    pip install -r requirements.txt
    python build.py --serve       # then open http://localhost:8000
Stop with Ctrl+C. Re-run after every change.

## Publish
    git add . && git commit -m "Update" && git push
Watch the **Actions** tab; the site updates in 1–2 minutes. Do not edit `dist/` – it is generated.
