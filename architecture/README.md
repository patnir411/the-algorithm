# Twitter Algorithm - Complete Architecture Documentation

This directory contains comprehensive visual documentation and technical analysis of Twitter's open-source recommendation algorithm.

## 📚 Documentation Structure

### 🏠 [Main Overview](index.html)
Central hub with system statistics, technology stack, and navigation to all documentation sections.

### 🔄 [Recommendation Pipeline](pipeline.html)
Complete end-to-end flow from user request to ranked timeline:
- Request transformation and product pipelines
- Query feature hydration (~100 features)
- Candidate pipeline orchestration (22+ pipelines)
- Scored tweets recommendation pipeline
- Feature hydration (~6,000 features per tweet)
- ML scoring and reranking
- Result selection and filtering
- Response marshalling and delivery

### 📈 [Ranking & Scoring](ranking.html)
Deep dive into the ranking system:
- **15 Engagement Signals**: Like, Retweet, Reply, Video Watch, Dwell Time, etc.
- **Weight Parameters**: Dynamic feature-switch controlled weights (-10K to +10K range)
- **Score Aggregation**: Per-head max normalization + weighted sum + epsilon
- **Contextual Variations**: Video-specific, in/out-network, device context
- **Phoenix Alternative**: Secondary scoring system with different action mappings

## 🎯 Key System Characteristics

### Architecture Patterns
- **Microservices**: Independent services with Thrift RPC communication
- **Pipeline-Based**: Composable, transparent execution stages via Product Mixer framework
- **Hybrid Processing**: Real-time streaming (GraphJet) + batch jobs (Scalding)
- **Parallel Execution**: Stitch framework for async/concurrent operations
- **Multi-Layer Caching**: Memcached, Manhattan, client-side caches

### Scale & Performance
- **Latency**: 200-500ms end-to-end timeline generation
- **Throughput**: 50+ RPS per Earlybird shard, 6000+ RPS SimClusters ANN
- **Features**: ~6,000 features hydrated per tweet candidate
- **Candidates**: ~1,500-4,000 candidates → 35 final tweets
- **Reduction**: 97%+ filtering from candidates to final timeline

## 🔑 Core Components

### Candidate Sources (10+)
1. **Earlybird** - Real-time search index (in-network, 7-day window)
2. **UTEG** - User-Tweet-Entity-Graph (out-of-network with social proof)
3. **SimClusters ANN** - Approximate cosine similarity (145K communities)
4. **Real Graph** - User interaction prediction (batch-computed daily)
5. **CR-Mixer** - Candidate generation orchestrator
6. **FRS** - Follow Recommendations Service → tweet candidates
7. **Tweet Mixer** - Multi-source coordination
8. **User-Tweet Graph** - Co-engagement based (GraphJet)
9. **User-Video Graph** - Video-specific recommendations
10. **Lists, Communities, Cache** - Additional specialized sources

### ML Models
1. **Heavy Ranker** - Neural network (ClemNet architecture, multi-task learning)
2. **Light Ranker** - MLP with sparse embeddings (fast pre-filtering)
3. **SimClusters** - Community detection (sparse embeddings, 145K clusters)
4. **TwHIN** - Dense knowledge graph embeddings
5. **Real Graph** - Gradient boosting for interaction prediction
6. **Safety Models** - NSFW, spam, toxicity, abuse detection

### Graph Algorithms
1. **SimClusters** - Approximate cosine similarity via matrix factorization
2. **GraphJet** - In-memory bipartite graphs (multi-segment power-law)
3. **PageRank/Tweepcred** - User reputation scoring
4. **SALSA** - Social graph expansion for user recommendations
5. **Graph Feature Service** - Intersection calculations (binary search optimization)

### Filtering (50+ Types)
- **Safety**: NSFW, spam, violence, gore (ML-powered)
- **Deduplication**: Semantic clustering (0.88/0.95 thresholds), bloom filters
- **Quality**: Engagement minimums, author reputation, content scoring
- **Diversity**: Author diversity (exponential decay), content balance
- **Visibility**: Blocks, mutes, legal compliance
- **Feedback**: User "Not Interested" signals (14-day fatigue window)

## 📊 System Statistics

| Metric | Value |
|--------|-------|
| Source Files | 6,133 (79% Scala, 17% Java, 3% Python, 0.5% Rust) |
| Services | 20+ microservices |
| Candidate Sources | 10+ parallel sources |
| Features per Tweet | ~6,000 |
| Engagement Signals | 15 tracked & predicted |
| Filter Types | 50+ |
| SimClusters Communities | 145,000 |
| Weight Parameters | 15 independent, dynamically adjustable |
| Weight Range | -10,000 to +10,000 |

## 🧮 Score Calculation Formula

```
For each tweet candidate:

1. ML Model Inference (Navi):
   → 15 engagement probabilities (0.0 to 1.0)

2. Per-Head Max Normalization:
   normalized_score_i = score_i / max(all_scores_i)

3. Apply Dynamic Weights:
   weighted_score_i = normalized_score_i × weight_i

4. Aggregate:
   final_score = Σ(weighted_score_i) + ε
   where ε = 0.001

5. Sort & Select:
   Top 35 tweets by final_score
```

## 🔬 15 Engagement Signals

### Tier 1 (Core Engagement)
1. **Favorite (Like)** - Most common positive signal
2. **Retweet** - Amplification + quotes
3. **Reply** - Conversation engagement
4. **Dwell Time** - Time spent viewing

### Tier 2 (Secondary Engagement)
5. **Bookmark** - Save for later
6. **Share** - Copy link, DM, native share

### Tier 3 (Quality Signals)
7. **Good Click** - Engagement clicks
8. **Good Click with Dwell** - Click + 2s+ engagement
9. **Good Profile Click** - Profile visit + engagement
10. **Reply Engaged by Author** - Author responds to replies

### Tier 4 (Video-Specific)
11. **Video Quality View** - ≥10 seconds watch
12. **Video Quality View Immersive** - Fullscreen mode
13. **Video Watch Time** - Total milliseconds
14. **Video Quality Watch** - Combined quality metric

### Tier 5 (Suppression)
15. **Negative Feedback V2** - Not interested, block, mute, report

## 🏗️ Service Architecture

### Data Layer
- **Tweetypie** - Core tweet read/write service
- **Unified User Actions** - Real-time user action stream (Kafka)
- **User Signal Service** - Centralized signal platform

### ML & Embeddings
- **SimClusters** - Community-based sparse embeddings
- **TwHIN** - Dense knowledge graph embeddings
- **Real Graph** - User interaction prediction
- **Representation Manager** - Embedding serving facade

### Ranking & Scoring
- **Navi** - High-performance ML serving (Rust/TensorFlow)
- **Heavy Ranker** - Neural network inference
- **Light Ranker** - Fast pre-filtering

### Candidate Generation
- **Earlybird** - Real-time search (Lucene-based)
- **GraphJet Services** - In-memory graph systems
- **CR-Mixer** - Candidate orchestrator
- **Follow Recommendations** - User & tweet recommendations
- **SimClusters ANN** - Approximate nearest neighbors

### Framework
- **Product Mixer** - Pipeline framework (200+ reusable components)
- **Home Mixer** - Main timeline orchestrator
- **Pushservice** - Notification recommendations

### Safety & Quality
- **Visibility Library** - Rule engine for content filtering
- **Trust & Safety Models** - NSFW, toxicity, abuse detection

## 🔄 Data Flow

```
User Actions (Favorites, RTs, Replies)
    ↓ [Kafka Stream]
Unified User Actions (UUA)
    ↓ [Recos-Injector]
GraphJet Services (UTEG, User-User Graph)
    ↓
Real-time Candidate Serving

Daily Batch Jobs (Scalding/Scio)
    ↓
SimClusters, Real Graph, PageRank
    ↓
Embedding Updates (Representation Manager)
    ↓
Offline Model Training
    ↓
Navi Model Serving
```

## 🎯 What Makes This Algorithm Unique

1. **Extreme Flexibility**: All weights dynamically adjustable → A/B testing without retraining
2. **Multi-Task Learning**: Single model predicts 15 engagement types simultaneously
3. **Social Proof**: Out-of-network recs show which connections engaged
4. **Hybrid Processing**: Real-time streams + batch ML + cached results
5. **Graph-Powered**: Multiple specialized graphs (User-Tweet, User-Video, UTEG)
6. **Embedding-Rich**: Sparse (SimClusters) + dense (TwHIN) + learned embeddings
7. **Safety-First**: Multiple ML safety models + rule-based visibility engine

## 📖 Technical References

### Key Files
- **Main Pipeline**: `/home-mixer/product/for_you/ForYouProductPipelineConfig.scala`
- **Scoring**: `/home-mixer/product/scored_tweets/ScoredTweetsRecommendationPipelineConfig.scala`
- **Ranking**: `/home-mixer/functional_component/scorer/WeighedModelRerankingScorer.scala`
- **Signals**: `/home-mixer/model/PredictedScoreFeature.scala`
- **Weights**: `/home-mixer/param/HomeGlobalParams.scala`
- **CR-Mixer**: `/cr-mixer/candidate_generation/CrCandidateGenerator.scala`
- **SimClusters**: `/simclusters-ann/server/src/main/scala/com/twitter/simclustersann/`
- **GraphJet**: `/src/scala/com/twitter/recos/user_tweet_entity_graph/`

### Configuration Parameters
- **ServerMaxResultsParam**: 35 (tweets per response)
- **AdsNumOrganicItemsParam**: 35 (organic items before ads)
- **NegativeScoreConstantFilterThreshold**: 0.001
- **NegativeScoreNormFilterThreshold**: 0.15
- **RequestRankDecayFactor**: 0.95 (time decay)
- **SimClusters Threshold**: 0.7 (cosine similarity)
- **Author Diversity Decay**: 0.5 (exponential)

### Technology Stack
- **Languages**: Scala (79%), Java (17%), Python (3%), Rust (0.5%)
- **Build**: Bazel
- **RPC**: Thrift
- **Streaming**: Kafka, Summingbird
- **Batch**: Scalding (Hadoop), Scio (Beam)
- **Storage**: Manhattan (database), Memcached, HDFS
- **ML**: TensorFlow, ONNX, PyTorch (via Navi)
- **Search**: Apache Lucene (Earlybird)
- **Graphs**: GraphJet (custom in-memory)

## 🚀 Getting Started

1. Open `index.html` in a web browser to start exploring
2. Navigate through different sections via the main page
3. Each page contains detailed visualizations and technical explanations
4. File references link back to actual codebase locations

## 📝 Documentation Pages

- **index.html** - Main overview and navigation hub
- **pipeline.html** - End-to-end recommendation flow (8 stages)
- **ranking.html** - 15 signals, weights, score aggregation

## 🔍 Deep Dive Topics

### SimClusters Algorithm
- 145,000 communities covering 20M+ producers
- Sparse embeddings (top 50-100 clusters per entity)
- Approximate cosine similarity (reduces 15K candidates to 900 evaluations)
- Multiple normalization methods (cosine, log-cosine, dot product)
- Daily batch updates via Scalding jobs

### GraphJet Architecture
- Multi-segment bipartite graphs (5 segments × 64M edges)
- Power-law degree distribution
- Edge type encoding (top 4 bits for engagement type)
- Real-time updates via Kafka streaming
- Concurrent read/write via segment isolation

### Feature Engineering
- **Continuous Features**: Log transform + batch normalization + clipping [-5, 5]
- **Sparse Features**: Hashing (18-bit) + embedding (50-dim)
- **Real-time Aggregates**: Hourly engagement windows
- **Graph Features**: Intersection counts, similarity scores
- **Safety Features**: Multi-model NSFW, spam, toxicity scores

## 📊 Performance Optimizations

1. **Parallel Candidate Fetching**: All sources run concurrently
2. **Batch Feature Hydration**: Group RPC calls by service
3. **Multi-Layer Caching**: Memory, distributed, client-side
4. **Segment-Based Graphs**: Concurrent access without locks
5. **Approximate Algorithms**: SimClusters ANN, HNSW
6. **Circuit Breakers**: Fallback to cache on failures
7. **Load Shedding**: Request sampling during high traffic

## 🎓 Key Learnings

1. **Complexity at Scale**: 6000+ features, 15 signals, 50+ filters working together
2. **Real-time + Batch Hybrid**: Complementary strengths for different use cases
3. **Flexibility via Weights**: External parameters enable rapid iteration
4. **Graph Power**: Multiple specialized graphs capture different relationships
5. **Safety Integration**: Not an afterthought - built into core pipeline
6. **Multi-Objective Optimization**: Balance engagement, quality, diversity, safety

---

**Generated**: November 2025
**Source**: Twitter Algorithm Open Source Repository
**Analysis**: Comprehensive codebase investigation with 6+ specialized exploration agents
**Coverage**: 6,133 source files across 20+ services
