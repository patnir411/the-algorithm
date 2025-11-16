#!/usr/bin/env python3
"""
Personal Algorithm Analyzer
Reverse-engineer Twitter's algorithm to analyze YOUR behavior
"""

import json
import re
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import statistics

class PersonalAlgorithmAnalyzer:
    """Analyzes your X/Twitter data export for flourishing metrics"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.tweets = []
        self.likes = []
        self.following = []
        self.followers = []

    def load_data(self):
        """Load X data export files"""
        print("📁 Loading X data export...")

        # Load tweets.js
        tweets_file = self.data_dir / "tweets.js"
        if tweets_file.exists():
            self.tweets = self._parse_js_file(tweets_file)
            print(f"  ✅ Loaded {len(self.tweets)} tweets")
        else:
            print(f"  ⚠️  tweets.js not found in {self.data_dir}")

        # Load like.js
        likes_file = self.data_dir / "like.js"
        if likes_file.exists():
            self.likes = self._parse_js_file(likes_file)
            print(f"  ✅ Loaded {len(self.likes)} likes")
        else:
            print(f"  ⚠️  like.js not found")

        # Load following.js (optional)
        following_file = self.data_dir / "following.js"
        if following_file.exists():
            self.following = self._parse_js_file(following_file)
            print(f"  ✅ Loaded {len(self.following)} following")

        # Load follower.js (optional)
        follower_file = self.data_dir / "follower.js"
        if follower_file.exists():
            self.followers = self._parse_js_file(follower_file)
            print(f"  ✅ Loaded {len(self.followers)} followers")

        print()

    def _parse_js_file(self, filepath):
        """Parse Twitter's JS file format (window.YTD.tweets.part0 = [...])"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove the JS variable assignment wrapper
        # Format: window.YTD.tweets.part0 = [{...}]
        json_match = re.search(r'=\s*(\[.*\])', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        return []

    def analyze_creation_consumption(self):
        """
        Calculate Creation:Consumption Ratio

        Creation = Original Tweets × 3 + Replies × 1
        Consumption = Retweets × 1 + Likes × 0.5
        """
        print("📊 CREATION:CONSUMPTION RATIO ANALYSIS")
        print("=" * 60)

        original_tweets = 0
        replies = 0
        retweets = 0
        quote_tweets = 0

        for item in self.tweets:
            tweet = item.get('tweet', {})
            text = tweet.get('full_text', '')
            in_reply_to = tweet.get('in_reply_to_status_id_str')

            # Check if it's a retweet
            if text.startswith('RT @'):
                retweets += 1
            # Check if it's a quote tweet
            elif 'quoted_status_id_str' in tweet:
                quote_tweets += 1
            # Check if it's a reply
            elif in_reply_to:
                replies += 1
            # Original tweet
            else:
                original_tweets += 1

        total_likes = len(self.likes)

        # Calculate scores
        creation_score = (original_tweets * 3) + (replies * 1)
        consumption_score = (retweets * 1) + (total_likes * 0.5)

        if consumption_score > 0:
            ratio = creation_score / consumption_score
        else:
            ratio = float(creation_score) if creation_score > 0 else 0

        # Interpret ratio
        if ratio > 2.0:
            level = "HIGH CREATOR 🌟"
            recommendation = "Excellent! You create more than you consume."
        elif ratio >= 1.0:
            level = "BALANCED ⚖️"
            recommendation = "Good balance. Consider creating slightly more."
        elif ratio >= 0.5:
            level = "HIGH CONSUMER ⚠️"
            recommendation = "You consume 2x more than you create. Try 1 original tweet per day."
        else:
            level = "PASSIVE SCROLLER 🚨"
            recommendation = "Primarily consuming. Set goal: 3 original tweets per week."

        print(f"Original Tweets:    {original_tweets:,}")
        print(f"Replies:            {replies:,}")
        print(f"Retweets:           {retweets:,}")
        print(f"Quote Tweets:       {quote_tweets:,}")
        print(f"Likes:              {total_likes:,}")
        print()
        print(f"Creation Score:     {creation_score:,}")
        print(f"Consumption Score:  {consumption_score:,.0f}")
        print(f"Ratio:              {ratio:.2f}")
        print()
        print(f"Level:              {level}")
        print(f"Recommendation:     {recommendation}")
        print()

        return {
            'original_tweets': original_tweets,
            'replies': replies,
            'retweets': retweets,
            'quote_tweets': quote_tweets,
            'likes': total_likes,
            'creation_score': creation_score,
            'consumption_score': consumption_score,
            'ratio': ratio,
            'level': level
        }

    def analyze_time_patterns(self):
        """
        Analyze time usage patterns and detect problematic behaviors
        """
        print("⏰ TIME PATTERN ANALYSIS")
        print("=" * 60)

        if not self.tweets:
            print("No tweets to analyze")
            return {}

        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        late_night_posts = 0  # 11pm - 2am
        early_morning_posts = 0  # 2am - 6am

        timestamps = []

        for item in self.tweets:
            tweet = item.get('tweet', {})
            created_at = tweet.get('created_at')

            if not created_at:
                continue

            # Parse Twitter timestamp: "Wed Mar 15 12:34:56 +0000 2023"
            try:
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                timestamps.append(dt)

                hour = dt.hour
                day_of_week = dt.strftime("%A")

                hourly_distribution[hour] += 1
                daily_distribution[day_of_week] += 1

                # Late night detection (11pm - 2am)
                if hour >= 23 or hour < 2:
                    late_night_posts += 1

                # Early morning (2am - 6am) = sleep displacement
                if 2 <= hour < 6:
                    early_morning_posts += 1

            except ValueError:
                continue

        # Calculate session clustering (posts within 10 minutes = same session)
        timestamps.sort()
        sessions = []
        if timestamps:
            current_session = [timestamps[0]]
            for ts in timestamps[1:]:
                if (ts - current_session[-1]).total_seconds() < 600:  # 10 minutes
                    current_session.append(ts)
                else:
                    sessions.append(current_session)
                    current_session = [ts]
            sessions.append(current_session)

        avg_session_length = statistics.mean([len(s) for s in sessions]) if sessions else 0
        long_sessions = [s for s in sessions if len(s) > 10]  # >10 posts in session

        # Calculate metrics
        total_posts = len(timestamps)
        late_night_pct = (late_night_posts / total_posts * 100) if total_posts > 0 else 0
        early_morning_pct = (early_morning_posts / total_posts * 100) if total_posts > 0 else 0

        # Find peak hours
        if hourly_distribution:
            peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])
            peak_day = max(daily_distribution.items(), key=lambda x: x[1])
        else:
            peak_hour = (0, 0)
            peak_day = ("N/A", 0)

        # Interpret patterns
        print(f"Total posts analyzed:     {total_posts:,}")
        print(f"Late night (11pm-2am):    {late_night_posts:,} ({late_night_pct:.1f}%)")
        print(f"Early morning (2am-6am):  {early_morning_posts:,} ({early_morning_pct:.1f}%)")
        print()
        print(f"Estimated sessions:       {len(sessions):,}")
        print(f"Avg posts per session:    {avg_session_length:.1f}")
        print(f"Long sessions (>10 posts):{len(long_sessions):,}")
        print()
        print(f"Peak hour:                {peak_hour[0]}:00 ({peak_hour[1]} posts)")
        print(f"Peak day:                 {peak_day[0]} ({peak_day[1]} posts)")
        print()

        # Sleep displacement warning
        if early_morning_pct > 5:
            print("🚨 SLEEP DISPLACEMENT DETECTED")
            print(f"   {early_morning_pct:.1f}% of posts between 2am-6am")
            print("   Recommendation: Set phone to Do Not Disturb after 11pm")
        elif late_night_pct > 20:
            print("⚠️  HIGH LATE-NIGHT USAGE")
            print(f"   {late_night_pct:.1f}% of posts after 11pm")
            print("   Recommendation: Wind down screen time after 10pm")
        else:
            print("✅ Healthy time patterns")

        print()

        # Hourly breakdown
        print("Hourly Distribution:")
        for hour in range(24):
            count = hourly_distribution[hour]
            bar = "█" * (count // max(1, max(hourly_distribution.values()) // 40))
            print(f"  {hour:02d}:00  {bar} {count}")
        print()

        return {
            'total_posts': total_posts,
            'late_night_posts': late_night_posts,
            'late_night_pct': late_night_pct,
            'early_morning_posts': early_morning_posts,
            'early_morning_pct': early_morning_pct,
            'sessions': len(sessions),
            'avg_session_length': avg_session_length,
            'long_sessions': len(long_sessions),
            'peak_hour': peak_hour[0],
            'peak_day': peak_day[0],
            'hourly_distribution': dict(hourly_distribution),
            'daily_distribution': dict(daily_distribution)
        }

    def analyze_regret_score(self, time_data):
        """
        Calculate Regret Score (0-100, lower is better)

        Regret = (
            Late Night Posts × 2.0 +
            Quote Tweet Ratio × 1.5 +
            Long Sessions × 1.0
        ) / Total Activity × 100
        """
        print("😰 REGRET SCORE ANALYSIS")
        print("=" * 60)

        late_night_posts = time_data.get('late_night_posts', 0)
        early_morning_posts = time_data.get('early_morning_posts', 0)
        long_sessions = time_data.get('long_sessions', 0)
        total_posts = time_data.get('total_posts', 1)

        # Count quote tweets (potential rage engagement)
        quote_tweets = sum(1 for item in self.tweets
                          if 'quoted_status_id_str' in item.get('tweet', {}))

        # Calculate regret components
        late_night_score = (late_night_posts + early_morning_posts * 2) * 2.0
        quote_tweet_score = quote_tweets * 1.5
        session_score = long_sessions * 1.0

        regret_score = (late_night_score + quote_tweet_score + session_score) / total_posts * 100
        regret_score = min(regret_score, 100)  # Cap at 100

        # Interpret score
        if regret_score < 20:
            level = "LOW ✅"
            color = "🟢"
            recommendation = "Excellent! You use X intentionally."
        elif regret_score < 40:
            level = "MODERATE 🟡"
            color = "🟡"
            recommendation = "Some problematic patterns. Set time limits."
        elif regret_score < 60:
            level = "HIGH ⚠️"
            color = "🟠"
            recommendation = "Significant regret patterns. Consider a digital detox."
        else:
            level = "VERY HIGH 🚨"
            color = "🔴"
            recommendation = "Algorithm has captured you. Take a break."

        print(f"Regret Score:           {regret_score:.1f}/100 {color}")
        print(f"Level:                  {level}")
        print()
        print(f"Contributing factors:")
        print(f"  Late-night posts:     {late_night_posts + early_morning_posts:,}")
        print(f"  Quote tweets:         {quote_tweets:,}")
        print(f"  Long sessions:        {long_sessions:,}")
        print()
        print(f"Recommendation:         {recommendation}")
        print()

        return {
            'regret_score': regret_score,
            'level': level,
            'late_night_component': late_night_score,
            'quote_tweet_component': quote_tweet_score,
            'session_component': session_score
        }

    def analyze_relationships(self):
        """
        Analyze relationship quality: Reciprocal vs Parasocial
        """
        print("🤝 RELATIONSHIP QUALITY ANALYSIS")
        print("=" * 60)

        if not self.following or not self.followers:
            print("⚠️  Need following.js and follower.js for full analysis")
            print()
            return {}

        # Extract IDs
        following_ids = set()
        for item in self.following:
            following_item = item.get('following', {})
            account_id = following_item.get('accountId')
            if account_id:
                following_ids.add(account_id)

        follower_ids = set()
        for item in self.followers:
            follower_item = item.get('follower', {})
            account_id = follower_item.get('accountId')
            if account_id:
                follower_ids.add(account_id)

        # Calculate reciprocal relationships (mutual follows)
        reciprocal = following_ids & follower_ids
        parasocial = following_ids - follower_ids  # You follow, they don't follow back

        # Analyze @mentions in tweets for engagement patterns
        mentions = Counter()
        for item in self.tweets:
            tweet = item.get('tweet', {})
            entities = tweet.get('entities', {})
            user_mentions = entities.get('user_mentions', [])
            for mention in user_mentions:
                screen_name = mention.get('screen_name')
                if screen_name:
                    mentions[screen_name] += 1

        top_mentions = mentions.most_common(20)

        # Quality metrics
        total_following = len(following_ids)
        total_followers = len(follower_ids)
        reciprocal_count = len(reciprocal)
        parasocial_count = len(parasocial)

        reciprocal_pct = (reciprocal_count / total_following * 100) if total_following > 0 else 0

        # Calculate relationship quality score (0-100)
        if total_following > 0:
            quality_score = (
                (reciprocal_count * 3.0) +
                (len(top_mentions) * 2.0)
            ) / total_following * 20
            quality_score = min(quality_score, 100)
        else:
            quality_score = 0

        # Interpret
        if quality_score >= 70:
            level = "EXCELLENT ✅"
            recommendation = "Strong reciprocal network. Keep nurturing these connections."
        elif quality_score >= 50:
            level = "GOOD 🟢"
            recommendation = "Healthy mix. Consider deepening top 10 relationships."
        elif quality_score >= 30:
            level = "MODERATE 🟡"
            recommendation = "Too many parasocial follows. Unfollow inactive/one-way accounts."
        else:
            level = "POOR ⚠️"
            recommendation = "Heavily parasocial. Focus on mutual relationships and DMs."

        print(f"Total following:        {total_following:,}")
        print(f"Total followers:        {total_followers:,}")
        print(f"Reciprocal (mutual):    {reciprocal_count:,} ({reciprocal_pct:.1f}%)")
        print(f"Parasocial (one-way):   {parasocial_count:,}")
        print()
        print(f"Relationship Quality:   {quality_score:.1f}/100")
        print(f"Level:                  {level}")
        print(f"Recommendation:         {recommendation}")
        print()

        if top_mentions:
            print(f"Top 10 people you mention:")
            for i, (user, count) in enumerate(top_mentions[:10], 1):
                print(f"  {i:2d}. @{user:<20s} ({count} mentions)")
            print()

        return {
            'total_following': total_following,
            'total_followers': total_followers,
            'reciprocal': reciprocal_count,
            'parasocial': parasocial_count,
            'reciprocal_pct': reciprocal_pct,
            'quality_score': quality_score,
            'level': level,
            'top_mentions': top_mentions[:10]
        }

    def calculate_flourishing_score(self, creation_data, regret_data, relationship_data):
        """
        Calculate composite Flourishing Score (0-100)

        Weighted combination:
        - Creation ratio: 33%
        - Low regret: 25%
        - Relationship quality: 20%
        - (Future: Knowledge retention: 12%, Time patterns: 10%)
        """
        print("🌟 FLOURISHING SCORE")
        print("=" * 60)

        # Normalize creation ratio to 0-100
        creation_ratio = creation_data.get('ratio', 0)
        creation_score = min(creation_ratio * 33, 33)  # Cap at 33

        # Invert regret score (100 - regret = flourishing component)
        regret_score = regret_data.get('regret_score', 50)
        regret_component = (100 - regret_score) * 0.25

        # Relationship quality (already 0-100)
        relationship_score = relationship_data.get('quality_score', 0)
        relationship_component = relationship_score * 0.20

        # Total flourishing score
        flourishing = creation_score + regret_component + relationship_component
        flourishing = min(flourishing, 100)

        # Interpret
        if flourishing >= 86:
            level = "OPTIMAL 🌟"
            emoji = "🟢🟢🟢"
            recommendation = "You're using X optimally! Creating, connecting, thriving."
        elif flourishing >= 61:
            level = "THRIVING ✅"
            emoji = "🟢🟢"
            recommendation = "Mostly positive usage. Small tweaks can get you to optimal."
        elif flourishing >= 31:
            level = "MIXED 🟡"
            emoji = "🟡"
            recommendation = "Some value, some waste. Focus on creating more, consuming less."
        else:
            level = "EXPLOITATION 🚨"
            emoji = "🔴"
            recommendation = "Algorithm has you. Take a break, reset your relationship with X."

        print(f"Flourishing Score:      {flourishing:.1f}/100 {emoji}")
        print(f"Level:                  {level}")
        print()
        print(f"Component breakdown:")
        print(f"  Creation (33%):       {creation_score:.1f}")
        print(f"  Low Regret (25%):     {regret_component:.1f}")
        print(f"  Relationships (20%):  {relationship_component:.1f}")
        print()
        print(f"Overall:                {recommendation}")
        print()

        return {
            'flourishing_score': flourishing,
            'level': level,
            'creation_component': creation_score,
            'regret_component': regret_component,
            'relationship_component': relationship_component
        }

    def run_full_analysis(self):
        """Run complete analysis suite"""
        print("=" * 60)
        print("PERSONAL ALGORITHM ANALYZER")
        print("Reverse-engineering Twitter's algorithm to analyze YOU")
        print("=" * 60)
        print()

        self.load_data()

        if not self.tweets:
            print("❌ No tweet data found. Please place your X data export in the 'data/' folder.")
            print()
            print("How to get your data:")
            print("1. Go to X.com → Settings → Your Account")
            print("2. Download an archive of your data")
            print("3. Extract the ZIP to the 'data/' folder")
            return

        # Run analyses
        creation_data = self.analyze_creation_consumption()
        time_data = self.analyze_time_patterns()
        regret_data = self.analyze_regret_score(time_data)
        relationship_data = self.analyze_relationships()
        flourishing_data = self.calculate_flourishing_score(
            creation_data, regret_data, relationship_data
        )

        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tweets': len(self.tweets),
                'total_likes': len(self.likes),
                'total_following': len(self.following),
                'total_followers': len(self.followers)
            },
            'creation': creation_data,
            'time_patterns': time_data,
            'regret': regret_data,
            'relationships': relationship_data,
            'flourishing': flourishing_data
        }

        output_file = Path('analysis_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"💾 Results saved to {output_file}")
        print()
        print("=" * 60)
        print("Analysis complete! 🎉")
        print("=" * 60)


if __name__ == "__main__":
    analyzer = PersonalAlgorithmAnalyzer()
    analyzer.run_full_analysis()
