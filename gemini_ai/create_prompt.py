def create_prompt(input_text: str):
    """
    Creates a prompt by inserting the input text into the template.

    Args:
        input_text (str): The text to be inserted into the template.

    Returns:
        str: The formatted prompt.
    """
    return f"""
You are a professional content editor and SEO expert. Read the following event description and rewrite it to be persuasive, SEO-optimised, and conversational for a general audience. Return a JSON object with the following fields:

1. "Title": Event name (plain text - exactly as it is referenced in the source, but using colon+space as dividing syntax when one is required - to replace dashes, vertical lines and other syntax)

2. "Dates": Return all event dates in a compact, human-readable, single-line string. Follow these format rules:
- If dates do not include a year (e.g. "Saturday, 7 Jun"), assume the current year: "7 Jun 2025"
- Use "DD MM YYYY, HH:MM–HH:MM" for a single event.
- For a range, use "DD–DD MM YYYY, HH:MM–HH:MM"
- Multiple dates, same month/year: "12, 18, 26 Jun 2025, HH:MM–HH:MM"
- Multiple months, same year: "26 Jun, 24 Jul, 25 Sep 2025, HH:MM–HH:MM"
- Different times: "26 Jun, 10:00–12:00; 24 Jul, 14:00–16:00; 2025"
- Different years: "27 Jun 2025, 10:00–12:00; 24 Jul 2026, 14:00–16:00"
- Flexible/online-only: "Jun 2025" or "26–28 Jun 2025"
- Times must be 24-hour format
- No lists, arrays, or line breaks

3. "IndexIntro": A 1–2 sentence summary of the event (don’t repeat the title). Add the formatted event date at the end. Use one of these formats:
- Single day: "26 June 2025"
- Multi-day: "26–28 June 2025"
- Spanning months: "26 June–4 July 2025"

4. "Intro": Same as IndexIntro, but omit the date

5. "Content": A ~200-word SEO-friendly event description including value, themes, and outcomes. Conversational and persuasive in tone.

6. "DateOrder": The last event date in "YYYYMMDD" format.
- For single-day events, use that date.
- For multi-day or scattered events, return the final occurring date.
- For flexible/month-only events, assume the last day of the mentioned month.

7. "Location": Format as "Venue Name, Address, City, Country". If hybrid, append "and online".

8. "Cost": Return pricing details (all tiers if applicable) or "Free"

9. "Category": One or more relevant categories (comma-separated, one line) selected based on the event’s themes and value. Use this guidance:
- "Conferences and Networking Events" → if event is about industry conferences, networking socials, places to meet clients and collaborators.
- "Education, Training and CPD" → if focus is on seminars for exchanging knowledge, CPD accredited training events, day courses, academic conferences, creative workshops.
- "Cultural Events and Exhibitions" → if focus is on design festivals, talks by architects, walking tours, architectural films, exhibitions, talks and lectures.

Constraints:
- All fields must be strings. Only "Content" can include paragraphs.
- No markdown, no bullet points, no extra commentary.
- Output must be valid JSON.

**Event context:**
{input_text}
    """
