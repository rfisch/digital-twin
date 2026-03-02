# Jacq's Writing Assistant — User Manual

Your AI writing assistant, fine-tuned on your books and blog posts. It writes in your voice so you can draft blog posts, emails, LinkedIn content, and marketing copy faster — without sounding like a robot.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Writing Types](#writing-types)
   - [Blog Post](#blog-post)
   - [Email (Outbound)](#email-outbound)
   - [Email Reply](#email-reply)
   - [Copywriting](#copywriting)
   - [LinkedIn Post](#linkedin-post)
   - [Freeform](#freeform)
3. [Working with Generated Text](#working-with-generated-text)
4. [LinkedIn Workflow](#linkedin-workflow)
5. [Scheduling Posts](#scheduling-posts)
6. [Model Settings](#model-settings)
7. [Integrations](#integrations)
   - [LinkedIn](#linkedin-integration)
   - [Gmail](#gmail-integration)
   - [Google Analytics](#google-analytics-integration)
8. [Tips for Best Results](#tips-for-best-results)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Opening the App

1. Open your terminal
2. Navigate to the project folder: `cd /Volumes/Code/jacq/digital-twin`
3. Launch: `make dev`
4. Open your browser to **https://localhost:7860**

The app handles everything else automatically — it starts the AI model when you generate and shuts it down when you're done, so it doesn't eat up your Mac's memory in the background.

### What You'll See

The interface has two sides:

```
┌─────────────────────┬───────────────────────────────────────┐
│                     │                                       │
│  CONTROLS (left)    │  OUTPUT (right)                       │
│                     │                                       │
│  Writing Type ▼     │  Your generated writing appears here. │
│                     │  You can edit it directly in the box. │
│  Topic / inputs     │                                       │
│                     │  [Save Edits] [Send] [Post]           │
│  [Model Settings]   │                                       │
│                     │                                       │
│  [ Generate ]       │                                       │
│                     │                                       │
└─────────────────────┴───────────────────────────────────────┘
```

### Quick Start — Your First Generation

1. **Writing Type** is set to "Blog Post" by default — leave it
2. Type a topic: `morning routines and why I stopped forcing them`
3. Click **Generate**
4. Wait a few seconds — your draft appears on the right
5. Edit it directly in the text box if needed
6. Click **Save Edits** to store your changes

That's it. The model writes in your voice — dashes, fragments, rhetorical questions, the occasional profanity, all of it.

---

## Writing Types

Select the writing type from the dropdown on the left. The form changes to show only the fields relevant to that type.

### Blog Post

**What it does:** Generates a full blog post in your voice.

**How to use it:**
1. Select **Blog Post** from the dropdown
2. Enter your topic or a brief description of what you want to write about
3. Click **Generate**

**Tips:**
- Be specific: "morning routines" is okay, but "why I stopped forcing morning routines and what I do instead" gives a much better draft
- The model opens with a hook, uses your signature rhythm (dashes, fragments, rhetorical Qs), and writes like you talk
- Generated posts are typically 500-800 words — edit to taste

---

### Email (Outbound)

**What it does:** Drafts a new email you're sending to someone.

**How to use it:**
1. Select **Email (Outbound)**
2. Fill in:
   - **Topic / Request** — what the email is about
   - **Recipient** — who you're writing to (e.g., "Sarah")
   - **Purpose** — what you need (e.g., "Follow up on retreat proposal")
   - **Email Type** — professional, personal, or newsletter
3. Click **Generate**

**Tips:**
- Keep the purpose clear and specific — the model writes better when it knows the goal
- Professional emails come out warm but focused; personal ones are looser
- The output is plain text — copy and paste into your email client

---

### Email Reply

**What it does:** Generates a reply to an email you received, written in your voice and formatted as HTML (ready to send from Gmail if connected).

**How to use it:**
1. Select **Email Reply**
2. Fill in:
   - **Paste the email you received** — copy the full email text
   - **Sender Name** — who sent it (e.g., "Tejal Misra")
   - **Sender Email** — their email address
   - **Subject** — the email subject line
   - **Reply Goal** — what you want to accomplish (e.g., "Secure a meeting," "Politely decline," "Express interest and ask for details")
   - **Tone Notes** (optional) — any extra guidance (e.g., "Keep it short," "Be extra warm")
3. Click **Generate**

**What you get:**
- An HTML-formatted email preview (shown at the top of the output area)
- The raw text version below it
- If Gmail is connected, you can click **Send Email** to send it directly

**Behind the scenes:** If the sender name and email are provided, the app automatically researches them online (via Gemini) to add context — so your reply feels personalized, not generic.

---

### Copywriting

**What it does:** Generates marketing copy for various platforms.

**How to use it:**
1. Select **Copywriting**
2. Fill in:
   - **Topic / Request** — what you're promoting
   - **Medium** — where it's going (e.g., "Instagram caption," "Facebook ad," "website headline")
   - **Target Audience** — who you're speaking to (e.g., "Women 25-45 interested in self-development")
   - **Key Message** — the core point (e.g., "New workshop launch")
   - **Tone Notes** — mood guidance (e.g., "Excited but grounded")
3. Click **Generate**

**Tips:**
- The medium matters — an Instagram caption will be punchy and short; a website headline will be tighter
- Be specific about your audience — "Women 25-45" generates differently than "therapists looking for CEU credits"

---

### LinkedIn Post

**What it does:** Generates 1-5 LinkedIn posts from one of your existing blog posts. This is the most full-featured writing mode.

**How to use it:**
1. Select **LinkedIn Post**
2. **Choose a blog post** — two ways:
   - **If Google Analytics is connected:** Select from the dropdown (ranked by performance — views, engagement, sessions)
   - **If not:** Paste a blog post URL directly into the dropdown field
3. Set **Number of Posts** (1-5) using the slider — more posts = more angle variety
4. Set **Time Range** to filter the analytics dropdown (30/60/90 days)
5. Click **Generate**

**What you get:**
- Multiple posts appear as tabs (Post 1, Post 2, etc.)
- Each takes a different angle on the same blog content
- Each post is 150-300 words with a hook opening, no external links, and hashtags
- A word counter shows live count as you edit

**After generating:**
- Click the radio buttons to switch between posts
- Edit any post directly in the text box
- **Save Edits** — stores your edits for future model improvement
- **Post Now** — publishes immediately to LinkedIn (if connected)
- **Schedule** — queue it for a future date/time

**Tips:**
- The model deliberately avoids linking to the blog in the post — LinkedIn penalizes external links
- Each post variation takes a different angle (personal story, practical takeaway, provocative question, etc.)
- Temperature is automatically set to 0.6 for LinkedIn (less creative risk in short-form content)
- Hit **Refresh Posts** to re-fetch the latest GA4 data

---

### Freeform

**What it does:** Lets you write any prompt and get a response in your voice. No template, no constraints — just you and the model.

**How to use it:**
1. Select **Freeform**
2. Type anything in the Topic / Request box
3. Click **Generate**

**Use cases:**
- Quick brainstorming: "Give me 5 opening hooks for a post about imposter syndrome"
- Rewriting: "Rewrite this paragraph in a punchier way: [paste text]"
- Outlines: "Outline a blog post about leaving corporate for coaching"
- Anything that doesn't fit the other categories

---

## Working with Generated Text

### Editing

Every output is **editable directly in the text box**. Just click into it and type. The model gives you a strong first draft — your job is to make it yours.

### Saving

Click **Save Edits** after any generation (whether you changed it or not). This saves:
- The original model output
- Your edited version
- The prompt and settings used

This data helps improve the model over time — the original-vs-edited pairs teach it what you liked and what you changed.

### Action Buttons

Different buttons appear depending on the writing type and which integrations are connected:

| Button | When it appears | What it does |
|--------|----------------|-------------|
| **Save Edits** | Always | Stores the generation + your edits |
| **Send Email** | Email Reply (Gmail connected) | Sends the HTML email via Gmail |
| **Post to LinkedIn** | Blog/Freeform (LinkedIn connected) | Publishes to LinkedIn |
| **Post Now** | LinkedIn Post mode | Publishes the selected post immediately |
| **Schedule** | LinkedIn Post mode | Queues the post for a future date/time |

If an integration isn't connected, the button shows "(not connected)" and is grayed out.

---

## LinkedIn Workflow

Here's the recommended workflow for turning blog posts into LinkedIn content:

### Step-by-step

1. **Select "LinkedIn Post"** from the Writing Type dropdown
2. **Pick a blog post** from the dropdown (or paste a URL)
   - The dropdown ranks posts by engagement if GA4 is connected
3. **Set post count to 3-5** — gives you options
4. **Generate** — wait ~10-20 seconds (it generates each post sequentially)
5. **Review each post** — click the radio buttons to switch between them
6. **Edit your favorite** — tighten the hook, adjust the ending, add/remove hashtags
7. **Choose your action:**
   - **Post Now** — goes live immediately
   - **Schedule** — pick a date/time and queue it
   - **Save Edits** — store it and copy-paste later

### Scheduling

To schedule a post for later:
1. Generate and edit your post
2. Enter a date and time in the **Schedule** field (format: `YYYY-MM-DD HH:MM`, e.g., `2026-03-15 09:00`)
3. Click **Schedule**
4. The post is queued — you'll see a confirmation with a short ID

### Managing Scheduled Posts

Open the **Scheduled Posts** section (collapsed at the bottom of the LinkedIn output area):

- **View pending posts** — a table showing ID, scheduled time, and preview
- **Cancel a post** — enter the ID prefix (first 8 characters) and click Cancel
- **Reschedule** — enter the ID and a new time, click Reschedule
- **Refresh** — update the table to see current status

Scheduled posts are checked and published automatically every 15 minutes (if the cron job is set up — see [Integrations](#integrations)).

---

## Model Settings

Click **Model Settings** (collapsed accordion on the left) to access advanced controls. You usually don't need to change these.

### Model

Which AI model to use for generation.

| Model | What it is | When to use it |
|-------|-----------|---------------|
| **jacq-v6:8b** (default) | Your fine-tuned model, version 6 | Almost always — this is your voice |
| jacq:8b | An older fine-tuned version | Only if v6 is having issues |
| llama3.1:8b | The base model (no fine-tuning) | For comparison or if you want generic AI output |
| Custom | Type any Ollama model name | If you train a new version (e.g., jacq-v7:8b) |

### Temperature

Controls how creative vs. predictable the output is.

| Value | Behavior | Best for |
|-------|----------|---------|
| 0.3-0.5 | Safe, predictable, can sound flat | When you need precision (rare) |
| **0.6** | Warm, controlled | **LinkedIn posts** (auto-set) |
| **0.7** | Natural, balanced | **Blog posts, emails** (default) |
| 0.8+ | Creative but unpredictable | Brainstorming only |

The app automatically adjusts temperature when you switch writing types (0.6 for LinkedIn, 0.7 for everything else). You can override it.

### Max Tokens

How long the output can be. 1 token is roughly 0.75 words.

| Value | Approximate length | Good for |
|-------|-------------------|---------|
| 512 | ~350 words | LinkedIn posts (set automatically) |
| 1024 | ~700 words | Short blog posts, emails |
| **2048** (default) | ~1,400 words | Full blog posts |
| 4096 | ~2,800 words | Long-form content |

### Use RAG Context

**Leave this OFF** (it's off by default for a reason).

RAG pulls in chunks of your past writing and feeds them to the model alongside the prompt. This sounds helpful but actually **hurts your voice** — the model starts stitching in raw corpus phrases instead of generating naturally. We tested it extensively:

- Buzzwords doubled
- Writing sounded less like you, not more
- Output became repetitive and "Frankenstein-like"

The only time to turn RAG on: when you need the model to reference **specific facts** from your past writing (names, dates, event details) that it wouldn't know from fine-tuning alone.

---

## Integrations

### LinkedIn Integration

**Status:** Check if the "Post to LinkedIn" / "Post Now" buttons are active (not grayed out).

**What it does:** Publishes posts directly to your LinkedIn profile from the app.

**Setup (one-time):**
1. Run: `python scripts/linkedin_auth.py`
2. A browser window opens — log in to LinkedIn and authorize the app
3. Credentials are saved to `credentials/linkedin_token.json`
4. Restart the app

**If posting fails with a 403 error:** This occasionally happens when LinkedIn's permissions need time to propagate. The workaround: copy the post text from the app and paste it directly into LinkedIn. Your edits are still saved.

**Token expiration:** If the token expires, re-run `python scripts/linkedin_auth.py`.

---

### Gmail Integration

**Status:** Check if the "Send Email" button is active (not grayed out).

**What it does:** Sends HTML-formatted email replies directly from the app via your Gmail account.

**Setup (one-time):**
1. Set up a Google Cloud project with Gmail API enabled
2. Download your OAuth credentials to `credentials/gmail_credentials.json`
3. The first time you click "Send Email," a browser window opens for authorization
4. Token is cached to `credentials/gmail_token.json`

---

### Google Analytics Integration

**Status:** Check if the LinkedIn blog post dropdown shows real posts (not "GA4 not configured").

**What it does:** Pulls your top-performing blog posts from Google Analytics so you can pick the best ones to repurpose for LinkedIn.

**What you see in the dropdown:**
- Blog post title
- View count and session count
- Posts ranked by a composite engagement score

**Setup:**
1. Place your GA4 service account JSON at `credentials/ga_service_account.json`
2. The app auto-detects it on startup

**Not configured?** No problem — just paste blog post URLs directly into the dropdown field. The app fetches the content either way.

---

## Tips for Best Results

### Writing Better Prompts

The model responds to how you ask, not just what you ask.

**Weak prompt:**
> morning routines

**Strong prompt:**
> why I stopped forcing morning routines and what actually works when you're not a 5am person

**The difference:** Specificity gives the model a direction, a point of view, and emotional texture to work with.

### When to Edit vs. Regenerate

- **Edit** when the draft is 70%+ there and just needs tightening — fix the hook, cut a paragraph, add a specific example
- **Regenerate** when the angle is wrong or the tone is off — click Generate again for a completely different take (the model is non-deterministic; each generation is unique)

### LinkedIn-Specific Tips

- **Don't add links in the post** — the model is trained not to, and LinkedIn's algorithm penalizes external links
- **Hook matters most** — the first 2-3 lines are what people see before "see more." Make them count.
- **Generate 3-5 variations** and pick the best — it's fast and gives you real options
- **Edit hashtags** — the model adds them but you know your audience best

### What the Model Is Good At

- First drafts that sound like you (not like ChatGPT)
- Hooks and openings
- Maintaining your rhythm and voice across different topics
- Short-form content (LinkedIn, emails)

### What Still Needs Your Touch

- Specific personal anecdotes (the model knows your style but not what happened to you last Tuesday)
- Technical accuracy (it may get details wrong — always fact-check)
- Very long blog posts (quality can drift after 800+ words)
- Anything requiring information newer than its training data

---

## Troubleshooting

### "Error: Could not start Ollama server"

The AI model server couldn't launch.

**Fix:**
1. Make sure Ollama is installed: `which ollama`
2. Try starting it manually: `ollama serve`
3. If it's already running, restart it: kill the process and try again
4. Check that the model exists: `ollama list` — you should see `jacq-v6:8b`

### Model not found

**Fix:** Pull the model: `ollama pull jacq-v6:8b`

If you've trained a new version, import it:
```
ollama create jacq-v7:8b -f models/fused/Modelfile
```

### LinkedIn "Post to LinkedIn (not connected)"

LinkedIn credentials aren't set up.

**Fix:** Run the auth flow: `python scripts/linkedin_auth.py`

### LinkedIn post returns 403

LinkedIn permissions sometimes take time to propagate after initial setup.

**Workaround:** Copy the post text and paste it into LinkedIn manually. Your edits are still saved in the app.

### Gmail "Send Email (not connected)"

Gmail credentials aren't configured.

**Fix:** See [Gmail Integration](#gmail-integration) setup steps.

### Generation is slow or stuck

- First generation after app launch takes longer (the model needs to load into memory)
- Subsequent generations are faster (~534 tokens/sec)
- If it hangs for more than 60 seconds, check the terminal for errors

### Output doesn't sound like me

- Make sure you're using **jacq-v6:8b** (check Model Settings)
- Make sure **Use RAG Context** is OFF
- Try regenerating — each generation is unique
- If it's consistently off, the temperature might be too low (robotic) or too high (chaotic)

### GA4 dropdown shows "not configured"

Google Analytics isn't set up. You can still use LinkedIn mode — just paste the blog URL directly into the dropdown field.

---

## Quick Reference Card

| I want to... | Writing Type | Key fields |
|--------------|-------------|------------|
| Draft a blog post | Blog Post | Topic |
| Send a new email | Email (Outbound) | Topic, Recipient, Purpose, Email Type |
| Reply to an email | Email Reply | Paste email, Sender, Goal |
| Write marketing copy | Copywriting | Topic, Medium, Audience, Message |
| Create LinkedIn posts from a blog | LinkedIn Post | Blog URL or dropdown, Post count |
| Do something custom | Freeform | Whatever you want |

| Keyboard shortcut | What it does |
|-------------------|-------------|
| Ctrl+Cmd+Space | Open emoji picker (macOS) |
