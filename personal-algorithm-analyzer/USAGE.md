# Personal Algorithm Analyzer - Usage Guide

## Quick Start (3 Steps)

### Step 1: Get Your X Data Export

1. Go to [X.com](https://x.com)
2. Click **Settings and Privacy** → **Your Account** → **Download an archive of your data**
3. Confirm your password
4. Wait for email (24-48 hours typically)
5. Download the ZIP file

### Step 2: Extract to Data Folder

```bash
# Create data directory
mkdir -p data/

# Extract your X archive
unzip twitter-YYYY-MM-DD-xxxxxxxx.zip -d temp/
cp temp/data/*.js data/
rm -rf temp/

# You should now have:
# data/tweets.js
# data/like.js
# data/following.js
# data/follower.js
```

### Step 3: Run Analysis

```bash
# Install dependencies
pip install -r requirements.txt

# Run analysis
python analyze.py

# View results
cat analysis_results.json
```

---

## Understanding Your Results

### Creation:Consumption Ratio

**What it measures:** Are you creating original content or just consuming?

**Score interpretation:**
- **> 2.0** - High Creator 🌟: You create 2x more than you consume
- **1.0-2.0** - Balanced ⚖️: Good mix of creation and consumption
- **0.5-1.0** - High Consumer ⚠️: You consume 2x more than you create
- **< 0.5** - Passive Scroller 🚨: Primarily consuming, minimal creation

**Components:**
- **Original Tweets** (weight: 3x): Your unique thoughts, not RTs or replies
- **Replies** (weight: 1x): Conversations (some creation value)
- **Retweets** (weight: 1x): Amplifying others (consumption)
- **Likes** (weight: 0.5x): Pure consumption

**Example:**
```
Original Tweets: 50 → 50 × 3 = 150
Replies: 30 → 30 × 1 = 30
Creation Score: 180

Retweets: 100 → 100 × 1 = 100
Likes: 500 → 500 × 0.5 = 250
Consumption Score: 350

Ratio: 180 / 350 = 0.51 (High Consumer ⚠️)
```

**Recommendation:** Aim for ratio ≥ 1.0. If you're at 0.51, post 1 original tweet per day.

---

### Regret Score

**What it measures:** How much of your X usage do you likely regret?

**Score interpretation:**
- **0-20** - Low ✅: Intentional usage, minimal regret
- **21-40** - Moderate 🟡: Some problematic patterns
- **41-60** - High ⚠️: Significant regret patterns
- **61-100** - Very High 🚨: Algorithm has captured you

**Contributing factors:**
- **Late-night posts** (11pm-2am, weight: 2.0x): Doom scrolling indicator
- **Early morning posts** (2am-6am, weight: 4.0x): Sleep displacement
- **Quote tweets** (weight: 1.5x): Often rage engagement
- **Long sessions** (>10 posts, weight: 1.0x): Compulsive scrolling

**Example:**
```
Late-night posts: 50 → 50 × 2.0 = 100
Quote tweets: 20 → 20 × 1.5 = 30
Long sessions: 10 → 10 × 1.0 = 10
Total activity: 500 posts

Regret = (100 + 30 + 10) / 500 × 100 = 28 (Moderate 🟡)
```

**Recommendation:** If > 40, set hard time limits. Use Screen Time on iOS or Digital Wellbeing on Android.

---

### Time Pattern Analysis

**What it measures:** When and how often you use X

**Key metrics:**
- **Hourly distribution**: Shows your usage by hour of day
- **Peak hour**: When you're most active
- **Late-night percentage**: % of posts after 11pm
- **Sleep displacement**: Posts between 2am-6am
- **Session clustering**: How many distinct usage sessions
- **Long sessions**: Sessions with >10 posts (compulsive usage indicator)

**Healthy patterns:**
- Peak hours during productive times (morning, lunch, evening)
- <10% late-night usage
- <2% early morning usage (sleep displacement)
- Short sessions (1-3 posts average)
- Few long sessions

**Problematic patterns:**
- Peak hour is late night (11pm-2am)
- >20% late-night usage
- >5% early morning usage
- Long average session length (>5 posts)
- Many sessions (>20 per day = compulsive checking)

**Recommendations:**
- **If late-night is high:** Phone in another room after 10pm
- **If many sessions:** Disable notifications, check 3x/day max
- **If long sessions:** Set timer, hard stop at 30 minutes

---

### Relationship Quality

**What it measures:** Depth of your X relationships

**Score interpretation:**
- **70-100** - Excellent ✅: Strong reciprocal network
- **50-69** - Good 🟢: Healthy mix
- **30-49** - Moderate 🟡: Too parasocial
- **0-29** - Poor ⚠️: Heavily one-sided

**Components:**
- **Reciprocal relationships** (mutual follows, weight: 3.0x): High value
- **Top mentions** (frequent interactions, weight: 2.0x): Engagement depth
- **Parasocial relationships** (you follow, they don't, weight: -1.0x): Low value

**Example:**
```
Following: 500
Followers: 200
Reciprocal (mutual): 150

Quality = (150 × 3.0 + 20 mentions × 2.0) / 500 × 20
Quality = (450 + 40) / 500 × 20 = 19.6

Too low! Need more mutual relationships.
```

**Recommendations:**
- **If < 30:** Unfollow accounts that don't engage back
- **If many parasocial:** Focus on people who respond to you
- **Optimize:** Direct message your top 10 connections monthly

---

### Flourishing Score (Composite)

**What it measures:** Overall health of your X usage

**Formula:**
```
Flourishing =
  (Creation Ratio × 33) +          # 33% weight
  ((100 - Regret Score) × 0.25) +  # 25% weight
  (Relationship Quality × 0.20)    # 20% weight
  # Future: + Knowledge Retention (12%) + Time Patterns (10%)
```

**Score interpretation:**
- **86-100** - Optimal 🌟: Using X to create, connect, thrive
- **61-85** - Thriving ✅: Mostly positive, minor improvements possible
- **31-60** - Mixed 🟡: Some value, some waste
- **0-30** - Exploitation 🚨: Algorithm has you, take a break

**Example:**
```
Creation Ratio: 1.2 → 1.2 × 33 = 33 (capped)
Regret Score: 35 → (100 - 35) × 0.25 = 16.25
Relationship Quality: 55 → 55 × 0.20 = 11

Flourishing = 33 + 16.25 + 11 = 60.25 (Mixed 🟡)
```

**What each level means:**
- **Optimal (86+):** X enhances your life. Creating valuable content, maintaining deep relationships, learning. Keep it up!
- **Thriving (61-85):** Positive usage overall. Small optimizations (create more, consume less) can get you to optimal.
- **Mixed (31-60):** Getting some value but also wasting time. Need intentional changes. Set weekly creation goals.
- **Exploitation (0-30):** The algorithm is optimizing you, not the other way around. Consider a 1-week digital detox, then rebuild with strict limits.

---

## Actionable Improvements

### If Creation:Consumption < 1.0
**Goal:** Shift from consumer to creator

Actions:
1. **Daily:** Post 1 original thought before checking timeline
2. **Weekly:** Write 1 thread (3+ tweets) on something you learned
3. **Monthly:** Review: Are you creating 2x more than last month?

Unfollow 10% of accounts that don't inspire you to create.

### If Regret Score > 40
**Goal:** Minimize time-wasting patterns

Actions:
1. **Immediate:** Enable Screen Time limits (1 hour/day max)
2. **Daily:** No X after 10pm (phone in another room)
3. **Weekly:** Delete app on weekends, use web only

Track: Did you scroll and think "that was a waste" this week?

### If Relationship Quality < 50
**Goal:** Deepen reciprocal connections

Actions:
1. **This week:** Unfollow 50 parasocial accounts (celebrities you'll never interact with)
2. **Monthly:** DM your top 10 most-engaged connections with something valuable
3. **Quarterly:** Propose IRL meetup or video call with 3 X friends

Measure: How many reciprocal relationships did you add?

### If Flourishing < 60
**Goal:** Comprehensive reset

Actions:
1. **Week 1:** Digital detox (delete app, emergency use only)
2. **Week 2:** Reinstall, but ONLY for creation (post original content, no timeline scrolling)
3. **Week 3:** Add back consumption, but 10 minutes max per session
4. **Week 4:** Measure again. Repeat detox if score hasn't improved.

---

## Advanced: Setting Personal Goals

Edit your personal goals in `personal_goals.json`:

```json
{
  "creation_ratio_target": 1.5,
  "regret_score_target": 25,
  "relationship_quality_target": 70,
  "flourishing_target": 75,
  "weekly_original_tweets": 5,
  "max_daily_minutes": 60,
  "sleep_time_cutoff": "23:00"
}
```

Re-run analysis monthly to track progress:
```bash
python analyze.py --compare-to-goals
```

---

## Privacy & Data

**All analysis happens locally.** Your data never leaves your machine.

- Data is read from `data/` folder
- Results saved to `analysis_results.json`
- No network requests
- No third-party services
- Open source - inspect the code yourself

---

## Next Steps

1. **Run initial analysis** to establish baseline
2. **Set goals** based on your scores
3. **Implement one improvement** from recommendations
4. **Re-analyze monthly** to track progress
5. **Iterate** - what gets measured gets managed

**The algorithm optimized you for engagement.**
**Now you're optimizing yourself for flourishing.**
