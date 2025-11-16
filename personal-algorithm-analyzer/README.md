# Personal Algorithm Analyzer

**Reverse-engineering the Twitter algorithm to analyze YOUR behavior**

## Overview

This tool applies the insights from Twitter's recommendation algorithm to analyze your personal X/Twitter data export. Instead of optimizing for engagement, it measures the metrics that actually matter for human flourishing.

## What It Analyzes

### 1. Creation:Consumption Ratio
- **Original tweets** vs **retweets/likes**
- Quality metrics (length, media, links, threads)
- Trend over time: Are you creating more or consuming more?

### 2. Regret Score Estimator
- **Late-night doom scrolling** (11pm-2am activity spikes)
- **Rage engagement** (quote tweets with negative sentiment)
- **Parasocial addiction** (one-way engagement with celebrities)
- **Session length** clustering (how long do you scroll?)

### 3. Time Pattern Analysis
- **Hourly/daily/weekly** usage patterns
- **Sleep displacement** detection (posts after midnight)
- **Productivity correlation** (morning vs evening patterns)
- **Compulsive check patterns** (frequency clustering)

### 4. Relationship Quality Matrix
- **Reciprocal relationships** (mutual follows + engagement)
- **Parasocial relationships** (you engage, they don't respond)
- **Network depth** (DMs, lengthy replies, sustained conversations)
- **Digital→Real conversion** (mentions of IRL meetings)

### 5. Knowledge Retention Proxy
- **Thread depth** (replies to your own tweets = building ideas)
- **Topic persistence** (themes that recur over months)
- **Return-to content** (replying to old tweets = retention)
- **URL patterns** (learning sources vs entertainment)

### 6. Content Value Decay
- **Viral vs sustained** (engagement spike vs steady)
- **Evergreen content** (tweets referenced later)
- **Regret content** (deleted tweets, if available)

### 7. Personal SimClusters
- **Auto-detect your tribes** (hashtag co-occurrence, @mention clustering)
- **Interest drift** over time
- **Echo chamber score** (diversity of sources)

### 8. Flourishing Score (Composite Metric)
Weighted combination of:
- High creation ratio (33%)
- Low regret score (25%)
- High relationship quality (20%)
- Knowledge retention (12%)
- Healthy time patterns (10%)

**Score range: 0-100**
- 0-30: Exploitation mode (algorithm has you)
- 31-60: Mixed (some value, some waste)
- 61-85: Thriving (mostly positive usage)
- 86-100: Optimal (creating, connecting, learning)

---

## X Data Export Files Required

Place your X data export in `data/` folder:

```
data/
  ├── tweets.js          # All your tweets (required)
  ├── like.js            # Liked tweets (required)
  ├── follower.js        # Followers list (optional)
  ├── following.js       # Following list (optional)
  ├── direct-messages.js # DMs (optional)
  └── profile.js         # Profile info (optional)
```

**How to get your data:**
1. X.com → Settings → Your Account → Download an archive of your data
2. Wait for email (can take 24-48 hours)
3. Download ZIP, extract to `data/` folder

---

## Data Structure (What We Extract)

From `tweets.js`:
```json
{
  "tweet": {
    "created_at": "Wed Mar 15 12:34:56 +0000 2023",
    "id_str": "1234567890",
    "full_text": "Your tweet content here",
    "entities": {
      "hashtags": [],
      "user_mentions": [],
      "urls": []
    },
    "in_reply_to_status_id_str": null,  # null = original tweet
    "in_reply_to_user_id_str": null,
    "retweet_count": 5,
    "favorite_count": 12
  }
}
```

From `like.js`:
```json
{
  "like": {
    "tweetId": "9876543210",
    "fullText": "Tweet you liked",
    "expandedUrl": "https://twitter.com/..."
  }
}
```

---

## Metrics Explained

### Creation:Consumption Ratio
```
Creation Score = (Original Tweets × 3 + Replies × 1) / (Retweets × 1 + Likes × 0.5)

> 2.0 = High creator
1.0-2.0 = Balanced
< 1.0 = High consumer
```

### Regret Score (0-100, lower is better)
```
Regret = (
  Late Night Posts (11pm-2am) × 2.0 +
  Quote Tweet Ratio × 1.5 +
  Deleted Tweets × 3.0 +
  Session Length > 2hrs × 1.0
) / Total Activity × 100
```

### Relationship Quality (0-100)
```
Quality = (
  Reciprocal Engagements × 3.0 +
  DM Conversations × 2.0 +
  Thread Depth (avg) × 1.5
) / (
  One-Way Engagements × 1.0 +
  Parasocial Follows × 0.5
) × 100
```

---

## Usage

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your X data export in data/ folder

# 3. Run analysis
python analyze.py

# 4. View interactive dashboard
python dashboard.py
# Open http://localhost:8050

# 5. Get AI-powered deep insights (optional)
export GEMINI_API_KEY='your-gemini-api-key'
python gemini_insights.py
```

---

## 🧠 AI-Powered Deep Insights (Gemini 2.5 Pro)

After running the basic analysis, you can get **personalized, expert-level insights** using Google's Gemini 2.5 Pro with deep thinking mode.

### What Gemini Provides

Unlike the basic metrics, Gemini acts as your **personal psychologist + behavioral scientist**, analyzing your patterns to provide:

1. **Behavioral Pattern Analysis** - What your metrics reveal about your psychology
2. **Red Flags & Concerns** - Unhealthy patterns and algorithmic exploitation
3. **Strengths & Positive Patterns** - What you're doing right
4. **Root Cause Hypothesis** - Why you use X the way you do (validation? procrastination? belonging?)
5. **Personalized Recommendations** - 5-7 specific interventions tailored to YOUR data
6. **30-Day Transformation Plan** - Week-by-week concrete action plan
7. **Deeper Questions** - What to reflect on about your usage

### Setup

1. **Get Gemini API Key** (free tier available):
   ```bash
   # Visit: https://aistudio.google.com/apikey
   export GEMINI_API_KEY='your-api-key-here'
   ```

2. **Run the analysis first**:
   ```bash
   python analyze.py  # Generate analysis_results.json
   ```

3. **Optional: Add personal context** for deeper insights:
   ```bash
   cp personal_notes.template.txt personal_notes.txt
   # Edit personal_notes.txt with your situation, goals, struggles
   ```

4. **Generate insights**:
   ```bash
   python gemini_insights.py
   # Streams analysis to console and saves to gemini_insights.txt
   ```

### Personal Context Template

The more context you provide, the more personalized the insights:

```txt
## YOUR CURRENT SITUATION
I'm a remote software engineer. Lonely during the day. X is my "water cooler".

## YOUR GOALS
Launch my own product in 6 months. Need deep focus time.

## YOUR STRUGGLES
I refresh X constantly when stuck on hard problems. Losing ability to think deeply.

## SPECIFIC QUESTIONS
Why do I keep checking even when I have work to do? How to use X intentionally?
```

### Example Output

```
🌟 GEMINI 2.5 PRO DEEP ANALYSIS
═══════════════════════════════════════════════════════════════════

## BEHAVIORAL PATTERN ANALYSIS

Your metrics paint a picture of someone caught in the "productive procrastination"
trap. Your Creation:Consumption ratio of 0.87 is revealing - you're consuming
significantly more than creating, yet you likely feel like you're "learning" or
"staying informed." This is the algorithm's most sophisticated deception...

[Continues with deep analysis based on YOUR specific data]

## PERSONALIZED RECOMMENDATIONS

1. **Hard Stop Protocol**: Given your 34% late-night usage and 47-min average
   sessions, implement a physical phone lockbox at 10pm. Not willpower -
   environmental design.

2. **Creation Sprints**: Every morning, write ONE original tweet before you're
   allowed to scroll. This rewires the creation:consumption ratio...

[5-7 specific recommendations based on your patterns]

## 30-DAY TRANSFORMATION PLAN

Week 1: Awareness Phase
- Track every X session in a note
- Notice triggers (stuck on problem? anxious? bored?)
- Goal: Just observe, don't change yet

Week 2: Environmental Design
...
```

### Why Gemini?

- **Deep Thinking Mode**: Uses unlimited compute to really understand your patterns
- **Personalized**: References YOUR specific metrics, not generic advice
- **Expert-Level**: Combines psychology, behavioral science, digital wellness
- **Actionable**: Concrete plans, not vague suggestions
- **Private**: All processing through Google's API, but you control what you share

---

## Output

### 1. Terminal Summary
```
=== PERSONAL ALGORITHM ANALYSIS ===

Creation:Consumption Ratio: 0.87 (High Consumer ⚠️)
  - Original Tweets: 234
  - Retweets: 1,245
  - Likes: 8,932
  - Recommendation: Create 2x more original content

Regret Score: 34/100 (Moderate 🟡)
  - Late-night posts: 23% of activity
  - Avg session length: 47 minutes
  - Recommendation: Set hard stop at 11pm

Relationship Quality: 68/100 (Good ✅)
  - Reciprocal relationships: 47
  - Parasocial follows: 312
  - DM conversations: 18 active
  - Recommendation: Nurture top 10 relationships

Flourishing Score: 62/100 (Thriving ✅)
```

### 2. Interactive Dashboard
- **Timeline view**: Metrics over time (daily/weekly/monthly)
- **Heatmap**: Activity by hour/day of week
- **Network graph**: Your relationship clusters
- **Topic clouds**: Your interest evolution
- **Regret patterns**: What to avoid

### 3. JSON Export
```json
{
  "summary": {
    "total_tweets": 234,
    "total_likes": 8932,
    "creation_ratio": 0.87,
    "regret_score": 34,
    "flourishing_score": 62
  },
  "time_patterns": {...},
  "relationships": {...},
  "topics": {...}
}
```

---

## Philosophical Foundation

This tool reverses the algorithm's logic:

| Twitter Algorithm | Your Analyzer |
|-------------------|---------------|
| Maximize engagement | Minimize regret |
| Addiction loops | Flourishing patterns |
| Time on platform | Value per minute |
| Viral spread | Deep connections |
| React to others | Create original |
| Algorithm knows you | You know yourself |

**The algorithm treats you as a product to optimize.**
**This tool treats you as a person to flourish.**

---

## Future Enhancements

- [x] **Gemini 2.5 Pro AI insights** - Deep personalized analysis with thinking mode
- [ ] Sentiment analysis for regret detection (enhanced version)
- [ ] Predictive model: "Will I regret this tweet?" (real-time warning)
- [ ] Accountability features: Weekly report card via email
- [ ] Goal setting: "Create 3 original tweets/week" with tracking
- [ ] Integration with time-tracking apps (RescueTime, etc.)
- [ ] Export to personal knowledge base (Obsidian, Notion)
- [ ] Browser extension for real-time flourishing score
- [ ] Comparison mode: Your metrics vs optimal patterns

---

## Technical Stack

- **Python 3.9+**: Core analysis
- **Pandas**: Data processing
- **Plotly/Dash**: Interactive dashboard
- **Google Gemini 2.5 Pro**: AI-powered insights with deep thinking
- **NetworkX**: Relationship graphs
- **NLTK/spaCy**: Text analysis (optional)

---

## Privacy

**All analysis happens locally on your machine.**
No data is sent to any server. Your X archive stays private.

---

## License

MIT - Use this to understand yourself better.

---

## Acknowledgments

Inspired by comprehensive analysis of Twitter's open-source recommendation algorithm. This tool applies those insights to help individuals, not platforms, optimize for flourishing.
