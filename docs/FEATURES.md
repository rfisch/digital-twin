# Feature Ideas

Use cases for Jacq's digital twin that add value to her business. The fine-tuned model is only worth training if it powers features she'll actually use.

## Analytics Deep Dive (Jan 30 – Feb 28, 2026)

Source: GA4 API (`scripts/analytics.py`) — Property: Jacqueline Fisch (359976766)

### Site Overview
| Metric | Value |
|--------|------:|
| Active users | 7,713 |
| New users | 7,575 (98%) |
| Sessions | 9,216 |
| Pages/session | 1.06 |
| Avg session | 2:24 |
| Bounce rate | 54.9% |
| Engaged sessions | 4,155 (45.1%) |
| Bounced sessions | 5,061 (54.9%) |

### Traffic Sources
| Channel | Sessions | % | Bounce | Avg Time |
|---------|----------|---|--------|----------|
| Organic Search | 7,249 | 79% | 48.7% | 2:10 |
| Direct | 1,462 | 16% | 82.1% | 3:57 |
| Organic Social | 232 | 2.5% | 57.8% | 0:30 |
| Referral | 96 | 1% | 50.0% | 4:02 |
| Email | 32 | 0.3% | 59.4% | 2:05 |

**Source detail:**
- google / organic: 7,108 sessions (dominates)
- MissingLettr-facebook: 114 sessions (auto-posting tool does most social work)
- Substack email: 32 sessions
- LinkedIn: 10 sessions
- ChatGPT referral: 11 sessions (people asking AI about writing, landing on her site)
- Instagram: negligible

### Top Landing Pages
| Page | Sessions | Bounce | Avg Time |
|------|----------|--------|----------|
| /blog/42-unfussy-quotes-on-creativity | 2,016 | 46.7% | 2:42 |
| /blog/15-powerful-writing-prompts | 1,056 | 40.6% | 1:54 |
| /blog/instead-of-scrolling | 717 | 47.0% | 1:51 |
| /blog/linkedin-headline | 648 | 42.9% | 2:33 |
| /blog/announce-your-business | 435 | 42.1% | 1:23 |
| / (homepage) | 287 | 78.4% | 4:25 |
| /blog/days-of-the-week-and-their-planets | 260 | 56.9% | 2:33 |
| /blog/how-to-write-a-shtty-first-draft | 224 | 46.0% | 4:27 |
| /blog/30things | 139 | 51.1% | 1:31 |
| /blog/20-prompts-find-your-writing-voice | 133 | 46.6% | 2:08 |

### What's Working (Low Bounce)
These pages hold attention — visitors who land here explore further:

| Page | Views | Bounce |
|------|------:|-------:|
| Coaching page | 66 | 8.2% |
| Memoir/Nonfiction Coaching | 28 | 13.8% |
| Contact page | 38 | 13.9% |
| Community (Intuitive Writing Flow) | 56 | 20.4% |
| Living Draft Container | 42 | 20.5% |
| Morning Pages / Manifesting | 47 | 22.9% |
| Book page | 28 | 25.0% |
| Shop | 43 | 26.2% |
| Writing Studio | 78 | 28.4% |

### What's Leaking (High Traffic, High Bounce)
These pages bring massive traffic but lose users immediately:

| Page | Views | Bounce | Lost Users/mo |
|------|------:|-------:|-------------:|
| 42 Quotes on Creativity | 2,145 | 50.9% | ~1,091 |
| 26 Alternatives to Scrolling | 753 | 48.5% | ~365 |
| LinkedIn Headline | 678 | 49.7% | ~337 |
| Homepage | 444 | 70.0% | ~310 |
| Days of the Week / Planets | 283 | 59.1% | ~167 |
| Mercury Retrograde prompts | 72 | 64.4% | ~46 |
| Anti-AI post | 70 | 76.6% | ~53 |

**Total lost users across top 15 leaky pages: ~2,900/month**

### User Segments
| Segment | Users | Sessions | Bounce | Avg Time |
|---------|------:|----------|--------|----------|
| New | 7,664 | 7,721 | 49.2% | 2:04 |
| Returning | 791 | 962 | 74.3% | 6:21 |
| Desktop | 4,284 | 5,237 | 52.2% | — |
| Mobile | 3,345 | 3,891 | 57.2% | — |

Returning visitors bounce MORE (74%) than new ones (49%) — they come back looking for something specific and don't find it, or there's no new content for them.

### Top Countries
| Country | Users | Sessions |
|---------|------:|----------|
| United States | 3,718 | 4,582 |
| India | 588 | 666 |
| United Kingdom | 414 | 492 |
| Canada | 405 | 470 |
| Australia | 257 | 303 |
| Singapore | 244 | 251 |

48% US, 52% international. Her paying customers are likely US/UK/Canada/Australia.

### Key Gaps
1. **No conversion tracking** — GA4 Key Events section is empty. Zero visibility into email signups, course purchases, or any business goals.
2. **1.06 pages/session** — visitors read exactly one page and leave. No internal linking or next-step CTAs are working.
3. **5,061 bounced sessions/month** — over half of all traffic is wasted.
4. **Returning visitors bounce at 74%** — worse than new visitors. No reason to come back.
5. **Social drives 2.5% of traffic** — LinkedIn sends 10 sessions/month despite her writing about LinkedIn headlines. Massive missed audience.
6. **Homepage bounces at 78%** — visitors who land on the homepage don't know where to go.
7. **Coaching page converts but nobody finds it** — 8% bounce rate but only 66 views. It's buried.
8. **Email sends 32 sessions/month** — either her list is tiny or her emails aren't driving clicks.

## The Problem

Jacq has excellent SEO — listicle/prompt posts rank well and bring 7K+ organic visitors/month. But the business has no system to:

1. **Capture** visitors → turn readers into email subscribers (no lead magnets on top pages)
2. **Nurture** subscribers → stay in their inbox with consistent content (32 email sessions = tiny list or low engagement)
3. **Convert** subscribers → move them toward coaching/courses/community (coaching page gets 66 views but 8% bounce — they're ready to buy, they just can't find it)
4. **Distribute** content → social drives 2.5% of traffic; her audience is on LinkedIn but LinkedIn sends 10 sessions/month
5. **Retain** visitors → 1.06 pages/session, 74% returning bounce — no reason to come back, no content journey

The digital twin should power features that close these gaps. Every feature below maps to a specific gap with measurable impact.

## Feature Ideas (Prioritized by Business Impact)

### P0: Content Repurposing Pipeline
- **Gap it closes**: Distribution (#4) — social drives only 2.5% of traffic
- **Problem**: Blog posts get 2K+ views from SEO but content stays siloed on the website. LinkedIn sends 10 sessions/month despite her audience being LinkedIn professionals who write.
- **Solution**: For each blog post, auto-generate a LinkedIn post, Instagram caption, email newsletter snippet, and Substack cross-post — all in Jacq's voice.
- **Impact**: LinkedIn alone could 10-50x from 10 sessions/month. Her top post "LinkedIn Headline" proves the audience overlap. MissingLettr auto-posts already drive 114 sessions — model-generated, voice-matched content would do much better.
- **Measurable target**: Social traffic from 232 → 1,000+ sessions/month; LinkedIn followers as leading indicator
- **Frequency**: 1-2x/week per blog post
- **Voice fidelity**: high
- **Build complexity**: medium

#### LinkedIn Strategy (Algorithm-Aware)

LinkedIn penalizes external links with ~60% reach reduction (as of 2026). The "link in comments" workaround is also penalized — LinkedIn now detects bridge behavior. This means the content repurposing strategy must be **native-first, not link-driven**.

**How it works:**
1. **Standalone value posts (4 out of 5 posts)** — The model takes a blog post and generates a complete, self-contained LinkedIn post that delivers the full insight/tip/prompt. No link needed. Goal is brand awareness + followers, not click-throughs.
2. **Profile link does the work** — Jacq's LinkedIn profile bio/featured section links to her site. Valuable posts → profile visits → click-through. This traffic appears as "direct" in GA4, not LinkedIn referral — so LinkedIn is likely already driving more than the 10 tracked sessions.
3. **Occasional link posts (1 out of 5)** — For high-value content like lead magnets or new offerings. The 60% penalty means a post reaching 1,000 people reaches ~400 with a link — still valuable if targeted at writers who need coaching.
4. **Newsletter bridge** — LinkedIn posts end with "I write about this weekly in my newsletter" → subscribers → owned relationship outside the platform.

**Why the digital twin is critical here:** Writing a standalone LinkedIn post that delivers full value from a blog post is harder than sharing a link with a caption. Jacq has to distill, reframe, and rewrite — the model does this work in her voice.

**What the model generates per blog post:**
- 1x LinkedIn post (standalone, no link, 150-300 words)
- 1x Instagram caption (shorter, hook-first, with hashtag suggestions)
- 1x Email newsletter snippet (personal reflection + the insight)
- 1x Substack cross-post (if the topic fits Energy-First Writing)

**Sources on LinkedIn algorithm:**
- [Buffer: How LinkedIn's Algorithm Works in 2026](https://buffer.com/resources/linkedin-algorithm/)
- [River Blog: 300 Posts Tested](https://rivereditor.com/blogs/2026-linkedin-algorithm-what-works-300-posts-tested)
- [Dataslayer: Document Posts Get 3x Engagement](https://www.dataslayer.ai/blog/linkedin-algorithm-february-2026-whats-working-now)

### P0: Email Lead Magnet Generator
- **Gap it closes**: Capture (#1) — 5,061 bounced sessions/month with no email capture
- **Problem**: Top 5 blog posts bring 4,872 sessions/month. ~2,400 bounce. Zero email capture on any of them.
- **Solution**: For top-performing posts, auto-generate a downloadable resource (expanded prompt pack, mini-guide, checklist) that serves as an email opt-in. "Loved these 15 prompts? Get 30 more delivered to your inbox."
- **Impact**: Even 5% capture rate on top 5 pages = 243 new email subscribers/month = 2,900/year.
- **Measurable target**: Email list growth from ~0 visible capture → 200+ new subscribers/month
- **Frequency**: 1-2x/month (create lead magnets for top posts)
- **Voice fidelity**: high
- **Build complexity**: medium

### P1: Newsletter Draft Generator
- **Gap it closes**: Nurture (#2) + Retention (#5) — email drives only 32 sessions/month, returning visitors bounce at 74%
- **Problem**: Returning visitors bounce worse than new ones. No ongoing relationship. Email channel is nearly dead (32 sessions).
- **Solution**: Weekly newsletter draft in her voice — personal reflection + link to latest/relevant blog post + a writing prompt. Model generates draft, she edits and sends.
- **Impact**: Consistent newsletter → returning visitors who engage → lower returning bounce rate → more coaching page views → revenue.
- **Measurable target**: Email sessions from 32 → 200+/month; returning visitor bounce from 74% → 50%
- **Frequency**: weekly
- **Voice fidelity**: high
- **Build complexity**: low

### P1: SEO Content Expansion
- **Gap it closes**: Discover (more top-of-funnel) — proven formats that rank well
- **Problem**: Her top 3 posts are all listicle/prompt format and dominate Google results. There's room for many more variations targeting different niches.
- **Solution**: Generate variations of proven formats: "15 Writing Prompts for [memoir writers / copywriters / coaches / burnout recovery]", "X Quotes on [topic]", "X Alternatives to [thing]".
- **Impact**: Each new listicle post could bring 100-500 sessions/month based on existing post performance. 10 new posts = 1,000-5,000 additional monthly sessions.
- **Measurable target**: Organic sessions from 7,249 → 10,000+/month within 6 months
- **Frequency**: 2-4x/month
- **Voice fidelity**: high
- **Build complexity**: low

### P1: Internal Linking / CTA Generator
- **Gap it closes**: Conversion (#3) + Retention (#5) — 1.06 pages/session, coaching page buried
- **Problem**: Coaching page has 8% bounce (visitors want to buy!) but only gets 66 views. Blog posts don't link to it. Pages/session is 1.06 — no content journey exists.
- **Solution**: For each blog post, generate contextual CTAs and internal links: "If this resonated, here's how I can help..." linking to coaching, community, or related posts. Model writes CTAs in Jacq's voice so they feel natural, not salesy.
- **Impact**: If even 2% of the 9,216 sessions reached the coaching page, it would go from 66 → 184 views. At 8% bounce (92% engagement), that's significant pipeline.
- **Measurable target**: Pages/session from 1.06 → 1.5+; coaching page views from 66 → 200+
- **Frequency**: one-time batch for existing posts + ongoing for new posts
- **Voice fidelity**: high
- **Build complexity**: low-medium

### P2: Blog Post First Drafts
- **Problem**: Blank page problem. Creating weekly content takes time.
- **Solution**: Generate first drafts from a topic or title in her voice. She edits and publishes.
- **Frequency**: 1-2x/week
- **Voice fidelity**: high
- **Build complexity**: low — already possible with current app

### P2: Course/Workshop Sales Copy
- **Problem**: Writing sales pages, workshop descriptions, and course outlines is time-consuming.
- **Solution**: Generate sales copy for Intuitive Writing School offerings in her voice.
- **Frequency**: quarterly
- **Voice fidelity**: medium-high
- **Build complexity**: low

### P3: Coaching Content
- **Problem**: Creating new writing prompts, exercises, and worksheets for students.
- **Solution**: Generate coaching materials aligned with her teaching philosophy.
- **Frequency**: weekly
- **Voice fidelity**: medium
- **Build complexity**: low

### P3: Book Writing Support
- **Problem**: Chapter drafts, brainstorming, expanding outlines during active book projects.
- **Frequency**: during active book projects
- **Voice fidelity**: very high
- **Build complexity**: medium

## The Funnel the Digital Twin Powers

```
DISCOVER (SEO)              → SEO Content Expansion (P1)
7,249 organic sessions/mo     generates more listicle posts that rank
        ↓
CAPTURE (Email)             → Lead Magnet Generator (P0)
5,061 bounced sessions/mo     creates opt-in incentives on top pages
        ↓
NURTURE (Newsletter)        → Newsletter Draft Generator (P1)
32 email sessions/mo          weekly emails keep subscribers engaged
        ↓
DISTRIBUTE (Social)         → Content Repurposing Pipeline (P0)
232 social sessions/mo        pushes content to LinkedIn/IG/Substack
        ↓
ENGAGE (Internal)           → CTA / Internal Link Generator (P1)
1.06 pages/session            connects blog readers to coaching/community
        ↓
CONVERT (Sales)             → Course/Workshop Copy (P2)
66 coaching page views/mo     moves subscribers toward paid offerings
```

## Status

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Content Repurposing | P0 | **LinkedIn done** | Blog URL → LinkedIn post → API posting. Implemented 2026-03-01 |
| Email Lead Magnets | P0 | idea | 5,061 bounced sessions/mo with zero capture |
| Newsletter Drafts | P1 | idea | Email = 32 sessions/mo; returning bounce = 74% |
| SEO Content Expansion | P1 | idea | Proven listicle format; room for niche variations |
| Internal Linking / CTAs | P1 | idea | 1.06 pages/session; coaching page buried (66 views) |
| Blog Post Drafts | P2 | idea | Already semi-possible with current app |
| Course/Workshop Copy | P2 | idea | Quarterly need |
| Coaching Content | P3 | idea | Lower urgency |
| Book Writing Support | P3 | idea | Project-based |

## Infrastructure

| Tool | Status | Purpose |
|------|--------|---------|
| `scripts/analytics.py` | working | Pull GA4 data on demand (any date range, any report) |
| `scripts/scrape_blog.py` | working | Scrape new blog/Substack posts for training data |
| GA4 service account | connected | Property 359976766, credentials in `credentials/ga_service_account.json` |
| Fine-tuned model (jacq-v6:8b) | deployed | Current production model in Ollama |

## Next Steps

- [ ] Decide which P0 feature to prototype first (Content Repurposing vs Lead Magnets)
- [ ] Prototype with current jacq-v6 model before committing to v7 retraining
- [ ] Set up GA4 key events (email signup, coaching page click) so we can measure impact
- [ ] Connect Google Search Console for keyword/query data (currently empty)
- [ ] Evaluate whether v6 output quality is good enough for the chosen feature
- [ ] Determine if the 199 new scraped blog posts improve v7 enough to justify retraining
