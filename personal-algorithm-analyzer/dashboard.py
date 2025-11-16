#!/usr/bin/env python3
"""
Interactive Dashboard for Personal Algorithm Analysis
Visualize your X/Twitter behavior patterns over time
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from dash import Dash, html, dcc, Input, Output
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("⚠️  Plotly/Dash not installed. Install with: pip install plotly dash")
    print("   Falling back to text-only visualization")


def load_analysis_results():
    """Load analysis results from JSON file"""
    results_file = Path('analysis_results.json')
    if not results_file.exists():
        print("❌ No analysis results found. Run 'python analyze.py' first.")
        return None

    with open(results_file, 'r') as f:
        return json.load(f)


def create_dashboard(results):
    """Create interactive Plotly/Dash dashboard"""
    if not DASH_AVAILABLE:
        print_text_dashboard(results)
        return

    app = Dash(__name__)

    # Extract data
    creation = results.get('creation', {})
    time_patterns = results.get('time_patterns', {})
    regret = results.get('regret', {})
    relationships = results.get('relationships', {})
    flourishing = results.get('flourishing', {})

    # Create visualizations
    # 1. Flourishing Score Gauge
    flourishing_score = flourishing.get('flourishing_score', 0)
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=flourishing_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Flourishing Score", 'font': {'size': 24}},
        delta={'reference': 60},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "red"},
                {'range': [30, 60], 'color': "orange"},
                {'range': [60, 85], 'color': "lightgreen"},
                {'range': [85, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))

    # 2. Creation vs Consumption Bar Chart
    creation_fig = go.Figure(data=[
        go.Bar(name='Creation', x=['Original Tweets', 'Replies'],
               y=[creation.get('original_tweets', 0), creation.get('replies', 0)],
               marker_color='green'),
        go.Bar(name='Consumption', x=['Retweets', 'Likes'],
               y=[creation.get('retweets', 0), creation.get('likes', 0)],
               marker_color='orange')
    ])
    creation_fig.update_layout(
        title="Creation vs Consumption",
        xaxis_title="Activity Type",
        yaxis_title="Count",
        barmode='group'
    )

    # 3. Hourly Activity Heatmap
    hourly_dist = time_patterns.get('hourly_distribution', {})
    hours = list(range(24))
    counts = [hourly_dist.get(str(h), 0) for h in hours]

    hourly_fig = go.Figure(data=go.Bar(
        x=hours,
        y=counts,
        marker_color=['red' if (h >= 23 or h < 6) else 'blue' for h in hours]
    ))
    hourly_fig.update_layout(
        title="Activity by Hour of Day (Red = Problematic)",
        xaxis_title="Hour",
        yaxis_title="Number of Posts",
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )

    # 4. Metrics Summary
    metrics_summary = html.Div([
        html.H2("📊 Analysis Summary", style={'color': '#1da1f2'}),
        html.Hr(),

        html.H3("🎨 Creation:Consumption Ratio"),
        html.P(f"Ratio: {creation.get('ratio', 0):.2f} - {creation.get('level', 'N/A')}"),
        html.Ul([
            html.Li(f"Original Tweets: {creation.get('original_tweets', 0):,}"),
            html.Li(f"Replies: {creation.get('replies', 0):,}"),
            html.Li(f"Retweets: {creation.get('retweets', 0):,}"),
            html.Li(f"Likes: {creation.get('likes', 0):,}"),
        ]),
        html.Hr(),

        html.H3("😰 Regret Score"),
        html.P(f"Score: {regret.get('regret_score', 0):.1f}/100 - {regret.get('level', 'N/A')}"),
        html.Ul([
            html.Li(f"Late-night posts: {time_patterns.get('late_night_posts', 0):,} ({time_patterns.get('late_night_pct', 0):.1f}%)"),
            html.Li(f"Early morning posts: {time_patterns.get('early_morning_posts', 0):,}"),
            html.Li(f"Long sessions: {time_patterns.get('long_sessions', 0):,}"),
        ]),
        html.Hr(),

        html.H3("🤝 Relationship Quality"),
        html.P(f"Score: {relationships.get('quality_score', 0):.1f}/100 - {relationships.get('level', 'N/A')}"),
        html.Ul([
            html.Li(f"Following: {relationships.get('total_following', 0):,}"),
            html.Li(f"Followers: {relationships.get('total_followers', 0):,}"),
            html.Li(f"Reciprocal (mutual): {relationships.get('reciprocal', 0):,} ({relationships.get('reciprocal_pct', 0):.1f}%)"),
            html.Li(f"Parasocial (one-way): {relationships.get('parasocial', 0):,}"),
        ]),
        html.Hr(),

        html.H3("🌟 Flourishing Score"),
        html.P(f"Score: {flourishing_score:.1f}/100 - {flourishing.get('level', 'N/A')}",
               style={'fontSize': '20px', 'fontWeight': 'bold'}),
    ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px'})

    # Layout
    app.layout = html.Div([
        html.H1("📊 Personal Algorithm Analyzer Dashboard",
                style={'textAlign': 'center', 'color': '#1da1f2'}),
        html.P("Reverse-engineering Twitter's algorithm to analyze YOUR behavior",
               style={'textAlign': 'center', 'color': '#666'}),
        html.Hr(),

        # Flourishing Score Gauge
        dcc.Graph(figure=gauge_fig),

        # Two column layout
        html.Div([
            html.Div([
                dcc.Graph(figure=creation_fig),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(figure=hourly_fig),
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
        ]),

        # Metrics summary
        metrics_summary,

        html.Hr(),
        html.P(f"Analysis generated: {results.get('timestamp', 'Unknown')}",
               style={'textAlign': 'center', 'color': '#999', 'fontSize': '12px'}),
    ], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

    return app


def print_text_dashboard(results):
    """Fallback text-only visualization if Plotly not available"""
    print("\n" + "=" * 80)
    print(" " * 20 + "PERSONAL ALGORITHM ANALYSIS DASHBOARD")
    print("=" * 80)
    print()

    # Flourishing Score
    flourishing = results.get('flourishing', {})
    score = flourishing.get('flourishing_score', 0)
    level = flourishing.get('level', 'N/A')

    print("🌟 FLOURISHING SCORE")
    print("-" * 80)
    print(f"  Score: {score:.1f}/100")
    print(f"  Level: {level}")
    print()

    # Progress bar
    filled = int(score / 2)  # 50 chars max
    bar = "█" * filled + "░" * (50 - filled)
    print(f"  [{bar}] {score:.1f}%")
    print()

    # Component breakdown
    creation = results.get('creation', {})
    regret = results.get('regret', {})
    relationships = results.get('relationships', {})

    print("📊 SUMMARY")
    print("-" * 80)
    print(f"  Creation:Consumption Ratio:  {creation.get('ratio', 0):.2f} ({creation.get('level', 'N/A')})")
    print(f"  Regret Score:                {regret.get('regret_score', 0):.1f}/100 ({regret.get('level', 'N/A')})")
    print(f"  Relationship Quality:        {relationships.get('quality_score', 0):.1f}/100 ({relationships.get('level', 'N/A')})")
    print()

    print("💡 RECOMMENDATIONS")
    print("-" * 80)

    if creation.get('ratio', 0) < 1.0:
        print("  ⚠️  Create more, consume less. Aim for 1 original tweet per day.")

    if regret.get('regret_score', 0) > 40:
        print("  ⚠️  High regret patterns detected. Set time limits and avoid late-night usage.")

    if relationships.get('reciprocal_pct', 0) < 30:
        print("  ⚠️  Too many parasocial follows. Unfollow accounts that don't engage back.")

    if score < 60:
        print("  🚨 Overall: Consider a digital detox and rebuild intentional X usage.")
    elif score < 85:
        print("  🟡 Overall: Mostly positive. Small tweaks can optimize further.")
    else:
        print("  ✅ Overall: Excellent! You're using X optimally.")

    print()
    print("=" * 80)
    print("For interactive visualizations, install: pip install plotly dash")
    print("Then run: python dashboard.py")
    print("=" * 80)


def main():
    """Main dashboard entry point"""
    results = load_analysis_results()
    if not results:
        return

    if DASH_AVAILABLE:
        app = create_dashboard(results)
        print("🚀 Starting dashboard server...")
        print("📊 Open your browser to: http://localhost:8050")
        print("   Press Ctrl+C to stop")
        app.run_server(debug=False, host='0.0.0.0', port=8050)
    else:
        print_text_dashboard(results)


if __name__ == "__main__":
    main()
