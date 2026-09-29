# Latest journal publishing contract

Approved by owner on 2026-09-30: create and publish a Persian/Turkish journal of current dentistry, medicine and health research, with daily morning publishing. Commits, pushes and uploads authorized for both public repositories.

## Repositories and pages
- Persian: `drumitoz/fa-omidkheirkhah`, main, https://fa.omidkheirkhah.com/latest.html
- Turkish: `drumitoz/drumitoz.github.io`, main, https://omidkheirkhah.com/latest.html
- Matching article IDs and relative paths in both languages. Each site has its own localized `content/latest.json`.
- Do not merge the journal into the older articles, personal writing, inventions or trading sections. Keep existing content intact.

## Editorial workflow
1. Read current HEAD, AGENTS.md (if present), this document and existing `content/latest.json` in BOTH repositories. Read the Persian editorial policy too. Compare IDs, DOI and topic to prevent duplicates. Repair a previous partial bilingual publication before adding a new article.
2. Search newly published authoritative primary research and official guidance. Prioritize the last 72 hours; widen to 7 days, then 30 days when necessary, stating the actual date. Never present older research as today's discovery. Alternate dentistry, medicine and health across runs when quality permits.
3. Choose one meaningful new topic per run. No publication when no new credible topic qualifies. No recycled rewrite, fabricated paper, publication date, DOI, author, statistic or image. Do not use a preprint as settled clinical evidence. Prefer peer-reviewed work; label preprints explicitly.
4. Read the original source, not just a search snippet. State whether full text or only abstract was reviewed. Explain study design, findings, limitations, generalizability and practical significance; separate interpretation from reported results. Support medical claims with primary/official references. Retraction/correction checks matter before relying on a study.
5. Write roughly 500–900 words per language when available evidence supports that length; prioritize accuracy and substance over word count. Persian must have correct نیم‌فاصله and native phrasing. Turkish must be authored naturally with correct clinical terms; no Persian leakage. Preserve equivalent meaning, claims, references and caveats. Never claim human expert review or original research without it occurring.
6. Use an accurate, topic-specific, lawful photograph or scientific image. Inspect it visually; record source, license/rights, descriptive localized alt and caption. A contextual photograph must not be labeled as a study participant or study result. Do not use a generated image as clinical evidence. Do not enlarge tiny source photos into blurry hero images. No endorsement implication or patient identifiers.
7. Sources are numbered in paragraphs and linked at the end; include real DOI and researcher names where available. Add 2–4 relevant internal articles already present in that locale. No forced, repetitive or irrelevant links. Never revive disabled trading.
8. Dates: `published` is actual publication date in Europe/Istanbul; `studyDate` is the primary study publication date. Keep existing dates unchanged unless substantively corrected and documented. The launch article is a September 20 study reported September 30, not a claim that it is the newest paper worldwide.

## Technical workflow
- Each article matches the schema of the existing localized entry in `content/latest.json`; unique ID `YYYY-MM-DD-short-ascii-slug` and same ID for both languages. Category is dentistry, medicine or health. Paragraphs contain plain text; numeric references `[1]` or `[۱]` are rendered as anchor links.
- Save a local licensed image under `assets/latest/`. Add the full article entry in each locale. Prepare BOTH locales before publishing either.
- Run `python scripts/build-latest.py` in each fresh checkout. It generates static article pages, `latest.html`, `latest.xml`, journal URLs in `sitemap.xml`, and only the bounded `<!-- LATEST:START -->` / `<!-- LATEST:END -->` home section. All pages are crawlable without JS.
- Daily changes allowed: `content/latest.json`, new article HTML under `latest/`, new images under `assets/latest/`, generated `latest.html`, `latest.xml`, journal additions in `sitemap.xml` and the bounded homepage journal fragment ONLY.
- Do not change CSS, JS, navigation, contact information, older articles, generators, or other homepage content as part of a routine run. If maintenance is needed, report separately.
- Run `python scripts/validate-latest.py`, `node --check latest.js`; inspect the actual diff and images. Validate translation completeness, references, local links, canonical/hreflang, uniqueness, RSS and sitemap XML. Preserve existing article history.
- Publish one atomic commit per repository based on a freshly checked HEAD; fast-forward only, no force push. Both payloads must validate first. GitHub has no cross-repository atomic commit: record both commit SHAs, verify both HEADs and published pages; if second publication fails, report partial publication explicitly and finish the missing locale next run. Never claim bilingual success after only one repo succeeds.
- The scheduled task runs in ChatGPT, not a newly installed GitHub Actions workflow. Hosting remains GitHub Pages. Do not create CI/cron workflows or paid services.
- After publication give a short Persian report with subject, both live links and both commit SHAs, or the concrete blocker. Do not claim a page is live until verified.

## Launch
- One substantive bilingual article on enamel remineralization, with study findings clearly labeled in vitro and abstract-only access disclosed.
- Primary study: Nebu George Thomas et al., Odontology, 2026-09-20, DOI 10.1007/s10266-026-01551-9; PMID 42763368.
- Context image downloaded from NIDCR's The Tooth Decay Process. It illustrates white-spot lesions, not this study. Source policy https://www.nidcr.nih.gov/about-us/web-policies permits reuse unless otherwise noted; no separate credit or restriction observed on the image. Image deliberately displayed at its native 236×118 pixels.
