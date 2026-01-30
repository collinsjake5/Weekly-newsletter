# Weekly Newsletter Builder - Instructions

## Quick Start (If Already Set Up)

```bash
cd "C:\Users\jcollins\OneDrive - Armstrong World Industries\Desktop\Weekly-newsletter"
python -X utf8 newsletter.py
```

Then open the HTML file from the `output` folder and email it to your team.

---

## Setup From Scratch

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation: open Command Prompt and type `python --version`

### Step 2: Clone the Repository
```bash
git clone https://github.com/collinsjake5/Weekly-newsletter.git
cd Weekly-newsletter
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Newsletter Generator
```bash
python -X utf8 newsletter.py
```

---

## Usage Options

| Command | Description |
|---------|-------------|
| `python -X utf8 newsletter.py` | Generate both AI and Robotics newsletters |
| `python -X utf8 newsletter.py --type ai` | Generate AI newsletter only |
| `python -X utf8 newsletter.py --type robotics` | Generate Robotics newsletter only |
| `python -X utf8 newsletter.py --days 14` | Look back 14 days instead of 7 |
| `python -X utf8 newsletter.py --dry-run` | Test without saving files |

---

## Output Files

After running, you'll find these files in the `output` folder:

| File | Description |
|------|-------------|
| `ai_YYYY-MM-DD.html` | AI newsletter (for email) |
| `ai_YYYY-MM-DD.md` | AI newsletter (Markdown) |
| `ai_YYYY-MM-DD.json` | AI newsletter data |
| `robotics_YYYY-MM-DD.html` | Robotics newsletter (for email) |
| `robotics_YYYY-MM-DD.md` | Robotics newsletter (Markdown) |
| `robotics_YYYY-MM-DD.json` | Robotics newsletter data |

---

## How to Email the Newsletter

### Option 1: Copy/Paste into Outlook (Recommended)

1. Open the `.html` file in your browser (double-click it)
2. Press `Ctrl+A` to select all content
3. Press `Ctrl+C` to copy
4. Open Outlook and create a new email
5. Press `Ctrl+V` to paste
6. The formatting and links will be preserved
7. Add recipients and send

### Option 2: Insert HTML into Outlook

1. Open Outlook and create a new email
2. Click **Insert** > **Attach File**
3. Navigate to the `.html` file
4. Click the dropdown arrow next to "Insert" and select **"Insert as Text"**
5. The newsletter will appear in the email body with formatting

### Option 3: Attach the HTML File

1. Create a new email in Outlook
2. Attach the `.html` file
3. Recipients can download and open it in their browser

---

## Customizing the Newsletter

### Tuning Content Relevance

Edit `guidelines.yaml` to improve content filtering:

**Add priority keywords** (boosts articles containing these):
```yaml
robotics:
  priority_keywords:
    - "deployment"
    - "warehouse"
    - "FANUC"
```

**Add exclude keywords** (filters out articles containing these):
```yaml
robotics:
  exclude_keywords:
    - "toy robot"
    - "hobby"
```

**Add good examples** (helps train the system):
```yaml
robotics:
  good_examples:
    - title: "Figure AI deploys robots to BMW factory"
      why: "Real commercial deployment news"
```

### Adding/Removing Sources

Edit `config.yaml` to modify RSS feeds, subreddits, or ArXiv categories.

**Add a new RSS feed:**
```yaml
rss:
  - name: "New Source Name"
    url: "https://example.com/feed.xml"
```

**Add a new subreddit:**
```yaml
reddit:
  - "NewSubredditName"
```

### Adjusting Scoring Weights

Edit `config.yaml` under the `scoring` section:

```yaml
scoring:
  recency_weight: 0.15      # How much to favor recent articles
  engagement_weight: 0.45   # How much to favor popular articles
  relevance_weight: 0.40    # How much to favor on-topic articles
  min_relevance_score: 0.03 # Minimum score to include (higher = stricter)
```

### Changing Number of Items

Edit `config.yaml`:
```yaml
output:
  max_items: 20  # Change this number
```

---

## Troubleshooting

### "python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Or use the full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python313\python.exe`

### Unicode/Encoding Errors
- Always use `python -X utf8` when running the script

### RSS Feed Errors
- Some feeds may be down or have moved
- Check `config.yaml` and remove/update broken feeds
- 404 errors are logged but don't stop the newsletter

### No Items After Filtering
- Lower `min_relevance_score` in `config.yaml`
- Add more topics or priority keywords

---

## File Structure

```
Weekly-newsletter/
├── newsletter.py      # Main script
├── generator.py       # Newsletter generation
├── config.yaml        # Sources and settings
├── guidelines.yaml    # Content filtering rules
├── requirements.txt   # Python dependencies
├── INSTRUCTIONS.md    # This file
├── output/            # Generated newsletters
├── processors/        # Scoring and deduplication
├── sources/           # Data collectors
├── templates/         # (Future) Email templates
└── .github/workflows/ # GitHub Actions automation
```

---

## Weekly Workflow (Manual)

1. **Run the generator**: `python -X utf8 newsletter.py`
2. **Review the HTML**: Open `output/ai_YYYY-MM-DD.html` and `output/robotics_YYYY-MM-DD.html`
3. **Tune if needed**: Edit `guidelines.yaml` to add/remove keywords
4. **Send via email**: Copy/paste or insert into Outlook
5. **Save good examples**: When you see a perfect article, add it to `guidelines.yaml`

---

## Automatic Scheduling (Free with GitHub Actions)

Run the newsletter automatically every week without your computer being on.

### Step 1: Push to GitHub

```bash
cd "C:\Users\jcollins\OneDrive - Armstrong World Industries\Desktop\Weekly-newsletter"
git add .
git commit -m "Add GitHub Actions automation"
git push
```

### Step 2: Enable GitHub Actions

1. Go to your repository: https://github.com/collinsjake5/Weekly-newsletter
2. Click **Settings** > **Actions** > **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Click **Save**

### Step 3: Verify It's Working

1. Go to the **Actions** tab in your repository
2. Click **"Generate Weekly Newsletter"** on the left
3. Click **"Run workflow"** dropdown > **"Run workflow"** button
4. Wait ~2 minutes for it to complete
5. Click on the completed run to download the newsletters

### Schedule

The workflow runs automatically every **Monday at 8 AM EST**. You can change this by editing `.github/workflows/newsletter.yml`:

```yaml
schedule:
  - cron: '0 13 * * 1'  # Every Monday at 1 PM UTC (8 AM EST)
```

Common cron schedules:
| Schedule | Cron Expression |
|----------|-----------------|
| Monday 8 AM EST | `0 13 * * 1` |
| Monday 9 AM EST | `0 14 * * 1` |
| Friday 8 AM EST | `0 13 * * 5` |
| Daily 8 AM EST | `0 13 * * *` |

### Where to Find the Newsletters

**Option A: Download from GitHub Actions**
1. Go to **Actions** tab
2. Click on the latest run
3. Scroll down to **Artifacts**
4. Download `newsletters-XX`

**Option B: View in Repository**
The newsletters are automatically committed to the `output/` folder in your repository.

### Optional: Email Notifications

To receive an email when newsletters are ready:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Add these secrets:
   - `EMAIL_USERNAME`: Your Gmail address
   - `EMAIL_PASSWORD`: A Gmail App Password (not your regular password)
   - `EMAIL_TO`: Email address to send to
3. Go to **Variables** tab and add:
   - `SEND_EMAIL`: `true`

**To create a Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password for "Mail"
3. Use that 16-character password as `EMAIL_PASSWORD`

---

## Free Tier Limits

GitHub Actions free tier includes:
- **Public repos**: Unlimited minutes
- **Private repos**: 2,000 minutes/month

Each newsletter run takes ~2 minutes, so you can run it:
- **Daily** without hitting limits
- **Multiple times per week** easily
