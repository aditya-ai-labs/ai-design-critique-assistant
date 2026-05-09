def build_prompt():
    return """
Act as a senior UX design mentor.

Analyze the UI image based on:
- Layout
- Visual hierarchy
- Typography
- Color
- Spacing
- Accessibility

Return structured JSON:
[
  {
    "category": "",
    "issue": "",
    "reason": "",
    "suggestion": "",
    "severity": "Critical/Recommended/Minor"
  }
]
"""