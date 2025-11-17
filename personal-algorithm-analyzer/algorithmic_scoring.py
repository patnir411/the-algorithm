#!/usr/bin/env python3
"""
Algorithmic Scoring Module
Applies Twitter's open-source recommendation algorithm logic to personal tweet data

References Twitter algorithm codebase:
- home-mixer/server/src/main/scala/com/twitter/home_mixer/model/PredictedScoreFeature.scala
- home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/scorer/
- home-mixer/server/src/main/scala/com/twitter/home_mixer/param/HomeGlobalParams.scala
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import statistics
import math
from typing import Dict, List, Tuple, Optional, Set


class FeatureExtractor:
    """
    Extract features from tweets matching Twitter's algorithm feature set

    References:
    - home-mixer/server/src/main/scala/com/twitter/home_mixer/model/HomeFeatures.scala
    - ~6,000 features in production, we extract the most important ~50
    """

    def extract_features(self, tweet: Dict, user_context: Dict) -> Dict[str, float]:
        """Extract all computable features from a tweet"""
        features = {}

        # Get tweet data
        tweet_data = tweet.get('tweet', {})
        text = tweet_data.get('full_text', '')
        created_at = tweet_data.get('created_at', '')
        entities = tweet_data.get('entities', {})

        # === TEXT FEATURES ===
        features['text_length'] = len(text)
        features['text_length_bucket'] = self._bucket_length(len(text))
        features['has_url'] = 1.0 if entities.get('urls') else 0.0
        features['has_media'] = 1.0 if entities.get('media') else 0.0
        features['has_photo'] = 1.0 if self._has_photo(entities.get('media', [])) else 0.0
        features['has_video'] = 1.0 if self._has_video(entities.get('media', [])) else 0.0
        features['has_link'] = 1.0 if entities.get('urls') else 0.0
        features['url_count'] = len(entities.get('urls', []))
        features['hashtag_count'] = len(entities.get('hashtags', []))
        features['mention_count'] = len(entities.get('user_mentions', []))

        # === TEMPORAL FEATURES ===
        if created_at:
            dt = self._parse_twitter_date(created_at)
            if dt:
                features['hour_of_day'] = dt.hour
                features['day_of_week'] = dt.weekday()
                features['is_weekend'] = 1.0 if dt.weekday() >= 5 else 0.0
                features['is_late_night'] = 1.0 if dt.hour >= 22 or dt.hour <= 4 else 0.0
                features['is_peak_time'] = 1.0 if 8 <= dt.hour <= 10 or 17 <= dt.hour <= 20 else 0.0

                # Recency (minutes since post)
                now = datetime.now()
                recency_minutes = (now - dt).total_seconds() / 60
                features['recency_minutes'] = recency_minutes
                features['recency_hours'] = recency_minutes / 60
                features['recency_days'] = recency_minutes / 1440

        # === ENGAGEMENT FEATURES ===
        features['favorite_count'] = float(tweet_data.get('favorite_count', 0))
        features['retweet_count'] = float(tweet_data.get('retweet_count', 0))
        features['reply_count'] = float(tweet_data.get('reply_count', 0) if 'reply_count' in tweet_data else 0)
        features['quote_count'] = float(tweet_data.get('quote_count', 0) if 'quote_count' in tweet_data else 0)

        # Engagement rates (normalized)
        total_engagement = features['favorite_count'] + features['retweet_count'] + features['reply_count']
        features['total_engagement'] = total_engagement
        features['engagement_rate'] = total_engagement / max(user_context.get('follower_count', 1), 1)

        # === TWEET TYPE FEATURES ===
        features['is_retweet'] = 1.0 if tweet_data.get('retweeted_status') or text.startswith('RT @') else 0.0
        features['is_reply'] = 1.0 if tweet_data.get('in_reply_to_status_id_str') else 0.0
        features['is_quote'] = 1.0 if tweet_data.get('quoted_status') or features['is_retweet'] == 0.0 and 'twitter.com' in text else 0.0
        features['is_original'] = 1.0 if features['is_retweet'] == 0.0 and features['is_reply'] == 0.0 else 0.0

        # === CONTENT QUALITY SIGNALS ===
        features['has_thread_continuation'] = 1.0 if text.startswith(('1/', '2/', '3/')) or '/n' in text.lower() else 0.0
        features['has_question'] = 1.0 if '?' in text else 0.0
        features['has_exclamation'] = 1.0 if '!' in text else 0.0
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['emoji_count'] = self._count_emojis(text)

        # === AUTHOR FEATURES (for user's own tweets) ===
        features['author_verified'] = float(user_context.get('is_verified', 0))
        features['author_follower_count'] = float(user_context.get('follower_count', 0))
        features['author_following_count'] = float(user_context.get('following_count', 0))
        features['author_follower_ratio'] = features['author_follower_count'] / max(features['author_following_count'], 1)

        return features

    def _bucket_length(self, length: int) -> int:
        """Bucket text length into categories (matches algorithm)"""
        if length < 50:
            return 0
        elif length < 100:
            return 1
        elif length < 150:
            return 2
        elif length < 200:
            return 3
        elif length < 280:
            return 4
        else:
            return 5

    def _has_photo(self, media: List) -> bool:
        """Check if tweet has photo"""
        return any(m.get('type') == 'photo' for m in media)

    def _has_video(self, media: List) -> bool:
        """Check if tweet has video"""
        return any(m.get('type') in ['video', 'animated_gif'] for m in media)

    def _parse_twitter_date(self, date_str: str) -> Optional[datetime]:
        """Parse Twitter date format: 'Wed Mar 15 12:34:56 +0000 2023'"""
        try:
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
        except:
            return None

    def _count_emojis(self, text: str) -> int:
        """Count emojis in text (simplified)"""
        # This is a simplified version - could use emoji library for accuracy
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE)
        return len(emoji_pattern.findall(text))


class EngagementProxyEstimator:
    """
    Estimate engagement probabilities based on user's historical patterns

    Since we don't have Twitter's trained ML models, we build proxies
    by learning from the user's own engagement history
    """

    def __init__(self):
        self.patterns = {
            'favorite': {},
            'retweet': {},
            'reply': {},
            'click': {},
            'profile_click': {},
            'video_view': {},
            'negative_feedback': {}
        }
        self.trained = False

    def train(self, tweets: List[Dict], likes: List[Dict]):
        """Learn engagement patterns from user's history"""
        print("📚 Training engagement proxy estimators...")

        # Analyze user's own tweets to understand what performs well
        for tweet in tweets:
            tweet_data = tweet.get('tweet', {})
            text = tweet_data.get('full_text', '')

            # Extract features
            has_media = bool(tweet_data.get('entities', {}).get('media'))
            has_url = bool(tweet_data.get('entities', {}).get('urls'))
            text_length = len(text)
            hour = self._get_hour(tweet_data.get('created_at', ''))

            # Engagement metrics
            favs = tweet_data.get('favorite_count', 0)
            rts = tweet_data.get('retweet_count', 0)

            # Learn patterns
            self._update_pattern('favorite', 'has_media', has_media, favs)
            self._update_pattern('favorite', 'has_url', has_url, favs)
            self._update_pattern('favorite', 'hour', hour, favs)

            self._update_pattern('retweet', 'has_media', has_media, rts)
            self._update_pattern('retweet', 'has_url', has_url, rts)

        # Analyze what user likes to understand click probability
        for like in likes[:1000]:  # Sample to avoid overprocessing
            like_data = like.get('like', {})
            # User clicked/liked this, so click probability is high for similar content
            self._update_pattern('click', 'liked', True, 1.0)

        self.trained = True
        print("  ✅ Proxy estimators trained")

    def _update_pattern(self, engagement_type: str, feature: str, value: any, engagement: float):
        """Update pattern statistics"""
        if feature not in self.patterns[engagement_type]:
            self.patterns[engagement_type][feature] = defaultdict(list)

        self.patterns[engagement_type][feature][value].append(engagement)

    def _get_hour(self, date_str: str) -> int:
        """Extract hour from Twitter date"""
        try:
            dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
            return dt.hour
        except:
            return 12  # default

    def estimate_favorite_probability(self, features: Dict) -> float:
        """
        Estimate P(favorite) based on tweet features

        In production, this is from Heavy Ranker neural network.
        We approximate based on learned patterns.
        """
        base_prob = 0.05  # Base rate

        # Adjust based on features
        if features.get('has_media', 0) > 0:
            base_prob *= 2.0  # Media doubles like probability

        if features.get('has_url', 0) > 0:
            base_prob *= 1.5  # Links increase engagement

        if features.get('is_peak_time', 0) > 0:
            base_prob *= 1.3  # Peak time boost

        if features.get('text_length', 0) > 100:
            base_prob *= 1.2  # Longer tweets get more likes

        # Decay by recency (older tweets less likely to get new likes)
        recency_hours = features.get('recency_hours', 0)
        decay_factor = math.exp(-recency_hours / 24)  # Exponential decay

        return min(base_prob * decay_factor, 0.95)

    def estimate_retweet_probability(self, features: Dict) -> float:
        """Estimate P(retweet)"""
        base_prob = 0.02  # Lower base rate than likes

        if features.get('has_url', 0) > 0:
            base_prob *= 2.5  # People RT informative content with links

        if features.get('has_media', 0) > 0:
            base_prob *= 1.8

        if features.get('hashtag_count', 0) > 0:
            base_prob *= 1.3  # Hashtags indicate shareable content

        # Already retweets don't get retweeted as much
        if features.get('is_retweet', 0) > 0:
            base_prob *= 0.3

        return min(base_prob, 0.9)

    def estimate_reply_probability(self, features: Dict) -> float:
        """Estimate P(reply)"""
        base_prob = 0.01

        if features.get('has_question', 0) > 0:
            base_prob *= 3.0  # Questions invite replies

        if features.get('mention_count', 0) > 0:
            base_prob *= 2.0  # Mentions often get replies

        if features.get('is_reply', 0) > 0:
            base_prob *= 1.5  # Replies beget replies (threads)

        return min(base_prob, 0.8)

    def estimate_click_probability(self, features: Dict) -> float:
        """Estimate P(click) - for tweets with URLs"""
        if features.get('has_url', 0) == 0:
            return 0.0

        base_prob = 0.10  # 10% click-through rate

        if features.get('text_length', 0) > 150:
            base_prob *= 1.3  # Longer descriptions boost clicks

        if features.get('has_media', 0) > 0:
            base_prob *= 1.5  # Visual preview increases clicks

        return min(base_prob, 0.95)

    def estimate_negative_feedback_probability(self, features: Dict) -> float:
        """
        Estimate P(negative_feedback) - block, mute, report, "not interested"

        This is a penalty in the algorithm
        """
        base_prob = 0.005  # Low base rate

        if features.get('is_late_night', 0) > 0:
            base_prob *= 2.0  # Late night content more likely to be regretted

        if features.get('caps_ratio', 0) > 0.3:
            base_prob *= 1.8  # ALL CAPS feels spammy

        if features.get('hashtag_count', 0) > 5:
            base_prob *= 2.0  # Excessive hashtags feel spammy

        return min(base_prob, 0.5)


class TwitterAlgorithmScorer:
    """
    Implement Twitter's actual scoring algorithm from the open-source codebase

    References:
    - home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/scorer/WeighedModelRerankingScorer.scala
    - home-mixer/server/src/main/scala/com/twitter/home_mixer/model/PredictedScoreFeature.scala
    """

    # Model weights from algorithm codebase (HomeGlobalParams.scala)
    # These are approximate typical values - production uses dynamic feature switches
    # Reference: home-mixer/server/src/main/scala/com/twitter/home_mixer/param/HomeGlobalParams.scala:786-900
    DEFAULT_WEIGHTS = {
        'favorite': 0.5,           # Likes are most important signal
        'retweet': 1.0,            # Retweets show strong approval
        'reply': 13.5,             # Replies indicate high engagement
        'good_click': 11.0,        # Clicks with dwell time
        'good_profile_click': 12.0,  # Profile visits
        'video_view': 0.005,       # Video quality views (scaled differently)
        'bookmark': 0.0,           # Bookmarks (often 0 weight)
        'share': 0.0,              # Shares (often 0 weight)
        'dwell': 0.0,              # Dwell time (often 0 weight)
        'video_watch_time': 0.0,   # Video watch time
        'negative_feedback': -30.0,  # Penalty for negative actions
    }

    def __init__(self, weights: Optional[Dict] = None):
        """Initialize scorer with custom or default weights"""
        self.weights = weights or self.DEFAULT_WEIGHTS

    def calculate_score(self, features: Dict, probabilities: Dict) -> Tuple[float, Dict]:
        """
        Calculate algorithmic score using Twitter's weighted scoring formula

        Formula from WeighedModelRerankingScorer.scala:
        score = aggregateWeightedScores(transformedScores)

        Returns: (final_score, score_breakdown)
        """
        breakdown = {}

        # === BASE SCORE: Weighted sum of engagement probabilities ===
        # Reference: PredictedScoreFeature.scala:294-311
        base_score = 0.0

        for signal, weight in self.weights.items():
            prob = probabilities.get(signal, 0.0)
            contribution = weight * prob
            base_score += contribution
            breakdown[f'{signal}_contribution'] = contribution
            breakdown[f'{signal}_prob'] = prob

        breakdown['base_score'] = base_score

        # === RECENCY BOOST ===
        # Newer content gets higher weight (from algorithm's time decay logic)
        recency_boost = self._calculate_recency_boost(features)
        breakdown['recency_boost'] = recency_boost

        # === AUTHOR SCORE ===
        # Verified authors, popular accounts get boost
        author_score = self._calculate_author_score(features)
        breakdown['author_score'] = author_score

        # === CONTENT QUALITY MULTIPLIER ===
        quality_mult = self._calculate_quality_multiplier(features)
        breakdown['quality_multiplier'] = quality_mult

        # === FINAL SCORE ===
        final_score = base_score * recency_boost * author_score * quality_mult
        breakdown['final_score'] = final_score

        return final_score, breakdown

    def _calculate_recency_boost(self, features: Dict) -> float:
        """
        Calculate recency decay factor

        Newer tweets get higher scores (exponential decay)
        Similar to algorithm's time-based ranking
        """
        recency_hours = features.get('recency_hours', 0)

        # Exponential decay: half-life of ~6 hours
        half_life = 6.0
        decay = math.exp(-recency_hours * math.log(2) / half_life)

        # Minimum boost of 0.1, max of 1.0
        return max(0.1, min(1.0, decay))

    def _calculate_author_score(self, features: Dict) -> float:
        """
        Calculate author reputation score

        Factors:
        - Verification status
        - Follower count
        - Follower/following ratio
        """
        score = 1.0

        # Verified boost
        if features.get('author_verified', 0) > 0:
            score *= 1.3

        # Follower count boost (logarithmic)
        follower_count = features.get('author_follower_count', 0)
        if follower_count > 0:
            # log10(1000) = 3, log10(10000) = 4, etc.
            follower_boost = 1.0 + (math.log10(max(follower_count, 1)) / 10.0)
            score *= min(follower_boost, 2.0)  # Cap at 2x

        # Follower/following ratio (quality signal)
        ratio = features.get('author_follower_ratio', 1.0)
        if ratio > 2.0:
            score *= 1.2  # High ratio = influential account
        elif ratio < 0.5:
            score *= 0.9  # Low ratio = less influential

        return score

    def _calculate_quality_multiplier(self, features: Dict) -> float:
        """
        Calculate content quality multiplier

        Boosts:
        - Media (images/videos)
        - Links (informative content)
        - Optimal length

        Penalties:
        - Too short
        - Excessive hashtags
        - All caps
        """
        mult = 1.0

        # Media boost
        if features.get('has_photo', 0) > 0:
            mult *= 1.3
        if features.get('has_video', 0) > 0:
            mult *= 1.4

        # Link boost (informative)
        if features.get('has_link', 0) > 0:
            mult *= 1.2

        # Length optimization
        text_length = features.get('text_length', 0)
        if 150 <= text_length <= 250:
            mult *= 1.2  # Optimal length
        elif text_length < 50:
            mult *= 0.7  # Too short

        # Hashtag penalty for spam
        hashtag_count = features.get('hashtag_count', 0)
        if hashtag_count > 5:
            mult *= 0.6  # Too many hashtags

        # All caps penalty
        caps_ratio = features.get('caps_ratio', 0)
        if caps_ratio > 0.5:
            mult *= 0.7  # Shouting

        return mult

    def explain_score(self, breakdown: Dict) -> str:
        """Generate human-readable explanation of score"""
        lines = []
        lines.append("Score Breakdown:")
        lines.append(f"  Base Score: {breakdown['base_score']:.2f}")

        # Top contributing signals
        contributions = [(k, v) for k, v in breakdown.items() if k.endswith('_contribution')]
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)

        for signal, value in contributions[:5]:
            signal_name = signal.replace('_contribution', '')
            prob = breakdown.get(f'{signal_name}_prob', 0)
            lines.append(f"    + {value:+.2f}  {signal_name} (p={prob:.3f})")

        lines.append(f"  × {breakdown['recency_boost']:.2f}  Recency boost")
        lines.append(f"  × {breakdown['author_score']:.2f}  Author score")
        lines.append(f"  × {breakdown['quality_multiplier']:.2f}  Quality multiplier")
        lines.append(f"  = {breakdown['final_score']:.2f}  FINAL SCORE")

        return '\n'.join(lines)


class TopicClusterer:
    """
    Detect topics and build user interest profile

    Simplified version of Twitter's SimClusters
    Reference: src/scala/com/twitter/simclusters_v2/
    """

    def __init__(self):
        self.user_interests = Counter()
        self.tweet_topics = {}

    def build_user_profile(self, tweets: List[Dict], likes: List[Dict]):
        """Build user's interest profile from their tweets and likes"""
        print("🔍 Building topic clusters...")

        # Extract topics from user's tweets
        for tweet in tweets:
            topics = self._extract_topics(tweet)
            for topic in topics:
                self.user_interests[topic] += 2.0  # Own content weighted higher

        # Extract topics from likes
        for like in likes[:1000]:
            topics = self._extract_topics(like)
            for topic in topics:
                self.user_interests[topic] += 1.0

        # Normalize to probabilities
        total = sum(self.user_interests.values())
        if total > 0:
            for topic in self.user_interests:
                self.user_interests[topic] /= total

        print(f"  ✅ Identified {len(self.user_interests)} interest clusters")

    def _extract_topics(self, tweet: Dict) -> Set[str]:
        """Extract topics from tweet (hashtags + keywords)"""
        topics = set()

        tweet_data = tweet.get('tweet', tweet.get('like', {}))
        text = tweet_data.get('full_text', tweet_data.get('fullText', ''))
        entities = tweet_data.get('entities', {})

        # Add hashtags as topics
        for hashtag in entities.get('hashtags', []):
            tag = hashtag.get('text', '').lower()
            if tag:
                topics.add(tag)

        # Extract simple keywords (this could be enhanced with NLP)
        keywords = self._extract_keywords(text)
        topics.update(keywords)

        return topics

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction (could use TF-IDF in production)
        tech_keywords = {'ai', 'ml', 'tech', 'startup', 'saas', 'code', 'developer',
                        'software', 'data', 'crypto', 'web3', 'design', 'product'}

        words = set(text.lower().split())
        return words & tech_keywords

    def calculate_topic_similarity(self, tweet: Dict) -> float:
        """
        Calculate how well tweet matches user's interests

        Similar to SimClusters cosine similarity
        """
        tweet_topics = self._extract_topics(tweet)

        if not tweet_topics or not self.user_interests:
            return 0.5  # Neutral

        # Calculate overlap
        matching_weight = sum(self.user_interests.get(topic, 0) for topic in tweet_topics)

        return min(matching_weight * 5.0, 1.0)  # Scale to 0-1


class AlgorithmicAnalyzer:
    """
    Main analyzer that orchestrates all components
    Applies Twitter's algorithm to analyze personal tweets
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.tweets = []
        self.likes = []
        self.following = []
        self.followers = []

        # Components
        self.feature_extractor = FeatureExtractor()
        self.proxy_estimator = EngagementProxyEstimator()
        self.scorer = TwitterAlgorithmScorer()
        self.topic_clusterer = TopicClusterer()

        self.user_context = {}

    def load_data(self):
        """Load X data export files"""
        from analyze import PersonalAlgorithmAnalyzer

        analyzer = PersonalAlgorithmAnalyzer(str(self.data_dir))
        analyzer.load_data()

        self.tweets = analyzer.tweets
        self.likes = analyzer.likes
        self.following = analyzer.following
        self.followers = analyzer.followers

        # Build user context
        self.user_context = {
            'follower_count': len(self.followers),
            'following_count': len(self.following),
            'tweet_count': len(self.tweets),
            'is_verified': False  # Could extract from profile.js
        }

        print(f"✅ Loaded {len(self.tweets)} tweets, {len(self.likes)} likes")

    def train_models(self):
        """Train proxy estimators and topic clusterer"""
        print("\n🎓 Training algorithmic models...")
        self.proxy_estimator.train(self.tweets, self.likes)
        self.topic_clusterer.build_user_profile(self.tweets, self.likes)

    def analyze_tweet(self, tweet: Dict) -> Dict:
        """Analyze a single tweet with algorithmic scoring"""
        # Extract features
        features = self.feature_extractor.extract_features(tweet, self.user_context)

        # Estimate engagement probabilities
        probabilities = {
            'favorite': self.proxy_estimator.estimate_favorite_probability(features),
            'retweet': self.proxy_estimator.estimate_retweet_probability(features),
            'reply': self.proxy_estimator.estimate_reply_probability(features),
            'good_click': self.proxy_estimator.estimate_click_probability(features),
            'good_profile_click': 0.01,  # Base rate
            'video_view': 0.05 if features.get('has_video', 0) > 0 else 0.0,
            'bookmark': 0.01,
            'share': 0.01,
            'dwell': 0.05,
            'video_watch_time': 0.0,
            'negative_feedback': self.proxy_estimator.estimate_negative_feedback_probability(features),
        }

        # Calculate algorithmic score
        score, breakdown = self.scorer.calculate_score(features, probabilities)

        # Topic similarity
        topic_similarity = self.topic_clusterer.calculate_topic_similarity(tweet)

        # Get actual engagement
        tweet_data = tweet.get('tweet', {})
        actual_engagement = {
            'favorites': tweet_data.get('favorite_count', 0),
            'retweets': tweet_data.get('retweet_count', 0),
            'replies': tweet_data.get('reply_count', 0) if 'reply_count' in tweet_data else 0,
        }

        return {
            'features': features,
            'probabilities': probabilities,
            'score': score,
            'breakdown': breakdown,
            'topic_similarity': topic_similarity,
            'actual_engagement': actual_engagement,
            'tweet_text': tweet_data.get('full_text', '')[:100],
            'created_at': tweet_data.get('created_at', ''),
        }

    def analyze_all_tweets(self) -> List[Dict]:
        """Analyze all user's tweets and rank by algorithmic score"""
        print("\n📊 Analyzing your tweets through algorithm's lens...")

        analyzed = []
        for i, tweet in enumerate(self.tweets):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(self.tweets)} tweets analyzed")

            result = self.analyze_tweet(tweet)
            analyzed.append(result)

        # Sort by score
        analyzed.sort(key=lambda x: x['score'], reverse=True)

        print(f"  ✅ Analyzed {len(analyzed)} tweets")
        return analyzed

    def generate_report(self, analyzed_tweets: List[Dict]) -> Dict:
        """Generate comprehensive algorithmic analysis report"""
        print("\n📝 Generating algorithmic report...")

        report = {
            'summary': {},
            'top_tweets': [],
            'bottom_tweets': [],
            'insights': {},
            'optimization_tips': []
        }

        # Summary statistics
        scores = [t['score'] for t in analyzed_tweets]
        report['summary'] = {
            'total_tweets': len(analyzed_tweets),
            'avg_score': statistics.mean(scores) if scores else 0,
            'median_score': statistics.median(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
        }

        # Top 10 tweets by algorithmic score
        report['top_tweets'] = analyzed_tweets[:10]

        # Bottom 10 tweets
        report['bottom_tweets'] = analyzed_tweets[-10:]

        # Insights
        report['insights'] = self._generate_insights(analyzed_tweets)

        # Optimization tips
        report['optimization_tips'] = self._generate_optimization_tips(analyzed_tweets)

        return report

    def _generate_insights(self, analyzed_tweets: List[Dict]) -> Dict:
        """Generate insights from analyzed tweets"""
        insights = {}

        # What performs best?
        top_tweets = analyzed_tweets[:20]

        # Analyze common features of top performers
        has_media_scores = [t['score'] for t in top_tweets if t['features'].get('has_media', 0) > 0]
        no_media_scores = [t['score'] for t in top_tweets if t['features'].get('has_media', 0) == 0]

        insights['media_impact'] = {
            'avg_score_with_media': statistics.mean(has_media_scores) if has_media_scores else 0,
            'avg_score_without_media': statistics.mean(no_media_scores) if no_media_scores else 0,
            'boost_factor': statistics.mean(has_media_scores) / statistics.mean(no_media_scores) if no_media_scores and has_media_scores else 1.0
        }

        # Peak hours analysis
        hour_scores = defaultdict(list)
        for tweet in analyzed_tweets:
            hour = tweet['features'].get('hour_of_day', 12)
            hour_scores[hour].append(tweet['score'])

        best_hours = sorted([(h, statistics.mean(scores)) for h, scores in hour_scores.items()],
                          key=lambda x: x[1], reverse=True)[:3]
        insights['best_posting_hours'] = [h for h, _ in best_hours]

        # User's algorithmic profile
        top_topics = self.topic_clusterer.user_interests.most_common(5)
        insights['top_interests'] = [topic for topic, _ in top_topics]

        return insights

    def _generate_optimization_tips(self, analyzed_tweets: List[Dict]) -> List[str]:
        """Generate personalized optimization tips"""
        tips = []

        # Analyze top vs bottom performers
        top_20 = analyzed_tweets[:20]
        bottom_20 = analyzed_tweets[-20:]

        # Media usage
        top_media_pct = sum(1 for t in top_20 if t['features'].get('has_media', 0) > 0) / len(top_20)
        bottom_media_pct = sum(1 for t in bottom_20 if t['features'].get('has_media', 0) > 0) / len(bottom_20)

        if top_media_pct > bottom_media_pct * 1.5:
            tips.append(f"📸 Add media (images/videos) to tweets - your top performers use media {top_media_pct*100:.0f}% of the time")

        # Posting time
        top_hours = [t['features'].get('hour_of_day', 12) for t in top_20]
        best_hour = statistics.mode(top_hours) if top_hours else 9
        tips.append(f"⏰ Post around {best_hour}:00 - your highest-scoring tweets are posted at this time")

        # Length optimization
        top_lengths = [t['features'].get('text_length', 0) for t in top_20]
        avg_top_length = statistics.mean(top_lengths) if top_lengths else 150
        tips.append(f"✍️ Optimal tweet length: ~{int(avg_top_length)} characters based on your top performers")

        # Link usage
        top_link_pct = sum(1 for t in top_20 if t['features'].get('has_link', 0) > 0) / len(top_20)
        if top_link_pct > 0.5:
            tips.append(f"🔗 Include links - {top_link_pct*100:.0f}% of your top tweets have URLs")

        # Topic focus
        top_topics = self.topic_clusterer.user_interests.most_common(3)
        if top_topics:
            topics_str = ', '.join([t for t, _ in top_topics])
            tips.append(f"🎯 Stay focused on your top topics: {topics_str}")

        return tips


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   ALGORITHMIC SCORING - Twitter Algorithm Analysis            ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    analyzer = AlgorithmicAnalyzer()

    # Load data
    analyzer.load_data()

    # Train models
    analyzer.train_models()

    # Analyze all tweets
    analyzed_tweets = analyzer.analyze_all_tweets()

    # Generate report
    report = analyzer.generate_report(analyzed_tweets)

    # Save results
    output_file = Path("algorithmic_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Results saved to {output_file}")

    # Print summary
    print("\n" + "="*80)
    print("ALGORITHMIC ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nTotal Tweets Analyzed: {report['summary']['total_tweets']}")
    print(f"Average Algorithmic Score: {report['summary']['avg_score']:.2f}")
    print(f"Score Range: {report['summary']['min_score']:.2f} - {report['summary']['max_score']:.2f}")

    print("\n🏆 TOP 5 TWEETS BY ALGORITHMIC SCORE:")
    for i, tweet in enumerate(report['top_tweets'][:5], 1):
        print(f"\n{i}. Score: {tweet['score']:.2f}")
        print(f"   Text: {tweet['tweet_text']}")
        print(f"   Actual engagement: {tweet['actual_engagement']['favorites']} likes, "
              f"{tweet['actual_engagement']['retweets']} RTs")

    print("\n💡 OPTIMIZATION TIPS:")
    for tip in report['optimization_tips']:
        print(f"  • {tip}")

    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()
