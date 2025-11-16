#!/usr/bin/env python3
"""
Gemini 2.5 Pro Insights Generator
Uses Google's Gemini 2.5 Pro with deep thinking mode to provide personalized insights
"""

import json
import os
from pathlib import Path
from google import genai
from google.genai import types


class GeminiInsightGenerator:
    """Generate deep personalized insights using Gemini 2.5 Pro"""

    def __init__(self, api_key=None):
        """Initialize Gemini client"""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it with:\n"
                "export GEMINI_API_KEY='your-api-key-here'"
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-pro"

    def load_analysis_results(self, results_path="analysis_results.json"):
        """Load the analysis results from JSON"""
        results_file = Path(results_path)
        if not results_file.exists():
            raise FileNotFoundError(
                f"Analysis results not found at {results_path}\n"
                "Run 'python analyze.py' first to generate results."
            )

        with open(results_file, 'r') as f:
            return json.load(f)

    def load_personal_notes(self, notes_path="personal_notes.txt"):
        """Load optional personal notes/context"""
        notes_file = Path(notes_path)
        if notes_file.exists():
            with open(notes_file, 'r') as f:
                return f.read().strip()
        return None

    def construct_prompt(self, results, personal_notes=None):
        """Construct comprehensive prompt for Gemini"""

        # Extract key metrics
        flourishing = results.get('flourishing_score', {})
        creation = results.get('creation_consumption', {})
        regret = results.get('regret_analysis', {})
        time_patterns = results.get('time_patterns', {})
        relationships = results.get('relationships', {})

        prompt = f"""You are an expert psychologist, behavioral scientist, and digital wellness consultant analyzing someone's X/Twitter usage patterns. You have deep knowledge of:
- Social media psychology and addiction patterns
- Behavioral economics and choice architecture
- Human flourishing and eudaimonic well-being
- Attention economy and algorithmic manipulation
- Digital minimalism and intentional technology use

## ANALYSIS RESULTS

### Flourishing Score: {flourishing.get('score', 'N/A')}/100
**Category:** {flourishing.get('category', 'N/A')}
**Interpretation:** {flourishing.get('interpretation', 'N/A')}

### Creation vs Consumption
- **Ratio:** {creation.get('ratio', 'N/A')}
- **Original Tweets:** {creation.get('original_tweets', 0)}
- **Replies:** {creation.get('replies', 0)}
- **Retweets:** {creation.get('retweets', 0)}
- **Likes:** {creation.get('likes', 0)}
- **Total Creation Score:** {creation.get('creation_score', 0)}
- **Total Consumption Score:** {creation.get('consumption_score', 0)}

### Regret Score: {regret.get('score', 'N/A')}/100
**Components:**
- Late-night usage (10pm-4am): {regret.get('late_night_percentage', 0):.1f}%
- Quote tweet ratio: {regret.get('quote_tweet_ratio', 0):.1f}%
- Average session length: {regret.get('avg_session_minutes', 0):.1f} minutes

### Time Patterns
**Most Active Hours:** {', '.join(map(str, time_patterns.get('peak_hours', [])))}
**Hourly Distribution:**
{self._format_hourly_distribution(time_patterns.get('hourly_distribution', {}))}

**Sleep Displacement Risk:** {time_patterns.get('sleep_displacement_risk', 'N/A')}

### Relationship Quality
- **Following:** {relationships.get('following_count', 0)}
- **Followers:** {relationships.get('follower_count', 0)}
- **Reciprocal connections:** {relationships.get('reciprocal_count', 0)}
- **Parasocial ratio:** {relationships.get('parasocial_ratio', 0):.2f}
- **Quality score:** {relationships.get('quality_score', 0):.1f}/100

---

## YOUR TASK

Using your expertise in psychology, behavioral science, and digital wellness, provide a **comprehensive, deeply personalized analysis** of this person's X/Twitter usage. Structure your insights as follows:

### 1. BEHAVIORAL PATTERN ANALYSIS
- What do these metrics reveal about their relationship with X/Twitter?
- What psychological patterns or tendencies are evident?
- Are they being optimized by the algorithm, or optimizing themselves?

### 2. RED FLAGS & CONCERNS
- What behaviors show signs of unhealthy patterns?
- Where is the algorithm potentially exploiting their psychology?
- What specific risks do you see (attention fragmentation, sleep issues, parasocial relationships, etc.)?

### 3. STRENGTHS & POSITIVE PATTERNS
- What healthy behaviors are evident?
- Where do they show agency and intentionality?
- What protective factors exist?

### 4. ROOT CAUSE HYPOTHESIS
- What underlying needs might X/Twitter be fulfilling? (belonging, validation, intellectual stimulation, procrastination, anxiety avoidance, etc.)
- What might be driving the observed patterns?

### 5. PERSONALIZED RECOMMENDATIONS
Provide 5-7 **specific, actionable** recommendations tailored to THIS person's patterns. Not generic advice - interventions based on THEIR specific metrics.

### 6. 30-DAY TRANSFORMATION PLAN
Create a concrete 30-day plan with:
- Week 1 focus
- Week 2 focus
- Week 3 focus
- Week 4 focus
- Specific metrics to track
- Success criteria

### 7. DEEPER QUESTIONS TO EXPLORE
What questions should this person ask themselves? What might require deeper self-reflection?

---
"""

        # Add personal notes if provided
        if personal_notes:
            prompt += f"""
## PERSONAL CONTEXT FROM USER

{personal_notes}

**IMPORTANT:** Use this personal context to make your insights even more specific and relevant. Reference their specific situation, goals, and concerns in your analysis.

---
"""

        prompt += """
**CRITICAL INSTRUCTIONS:**
- Be direct and honest, even if uncomfortable truths emerge
- Use specific numbers from the data to support your insights
- Avoid generic social media advice - make it personal to THESE metrics
- Think deeply about the psychological dynamics at play
- Consider both individual psychology AND algorithmic influence
- Your goal is to help them reclaim agency and optimize for flourishing, not engagement

Begin your analysis:
"""

        return prompt

    def _format_hourly_distribution(self, distribution):
        """Format hourly distribution for readability"""
        if not distribution:
            return "No data"

        sorted_hours = sorted(distribution.items(), key=lambda x: int(x[0]))
        lines = []
        for hour, count in sorted_hours:
            bar = '█' * min(int(count / 10), 50)  # Scale for readability
            lines.append(f"  {hour:02d}:00 - {count:4d} tweets {bar}")

        return '\n'.join(lines) if lines else "No data"

    def generate_insights(self, results_path="analysis_results.json",
                         notes_path="personal_notes.txt",
                         save_output=True):
        """Generate insights using Gemini 2.5 Pro with deep thinking"""

        print("🧠 Loading analysis results...")
        results = self.load_analysis_results(results_path)

        print("📝 Checking for personal notes...")
        personal_notes = self.load_personal_notes(notes_path)
        if personal_notes:
            print(f"  ✅ Loaded personal context ({len(personal_notes)} characters)")
        else:
            print("  ℹ️  No personal_notes.txt found (optional)")

        print("\n🤖 Constructing prompt for Gemini 2.5 Pro...")
        prompt = self.construct_prompt(results, personal_notes)

        print(f"\n{'='*80}")
        print("🌟 GEMINI 2.5 PRO DEEP ANALYSIS")
        print(f"{'='*80}\n")

        # Configure Gemini with deep thinking mode
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,  # Unlimited thinking for deep analysis
            ),
            temperature=1.0,  # Balanced creativity and accuracy
        )

        # Stream the response
        full_response = []
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response.append(chunk.text)

        except Exception as e:
            print(f"\n\n❌ Error generating insights: {e}")
            raise

        print(f"\n\n{'='*80}")

        # Save output if requested
        if save_output:
            output_file = Path("gemini_insights.txt")
            with open(output_file, 'w') as f:
                f.write(''.join(full_response))
            print(f"💾 Insights saved to {output_file}")

        return ''.join(full_response)


def main():
    """Main entry point"""
    import sys

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   GEMINI 2.5 PRO INSIGHTS - Personal Algorithm Analysis       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY environment variable not set\n")
        print("To set your API key:")
        print("  export GEMINI_API_KEY='your-api-key-here'\n")
        print("Get your API key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Check if analysis results exist
    if not Path("analysis_results.json").exists():
        print("❌ ERROR: analysis_results.json not found\n")
        print("Run the analyzer first:")
        print("  python analyze.py\n")
        sys.exit(1)

    try:
        generator = GeminiInsightGenerator()
        generator.generate_insights()

        print("\n✨ Analysis complete!")
        print("\nNext steps:")
        print("  1. Read gemini_insights.txt for your personalized analysis")
        print("  2. Create personal_notes.txt with your context for even deeper insights")
        print("  3. Re-run this script after adding personal notes")

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
