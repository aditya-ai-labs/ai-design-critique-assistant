from PIL import Image
import io

async def analyze_ui(file):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # TEMP dummy response
    return {
        "analysis": [
            {
                "category": "Layout",
                "issue": "Elements are misaligned",
                "reason": "Breaks visual consistency",
                "suggestion": "Use a grid system",
                "severity": "Critical"
            },
            {
                "category": "Typography",
                "issue": "Font sizes inconsistent",
                "reason": "Affects readability",
                "suggestion": "Use consistent scale",
                "severity": "Recommended"
            }
        ]
    }