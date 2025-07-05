def create_prompt(input_text: str):
    """
    Creates a prompt by inserting the input text into the template.

    Args:
        input_text (str): The text to be inserted into the template.

    Returns:
        str: The formatted prompt.
    """
    return f"""
You are a professional content editor and SEO expert. Read the following event description and rewrite it to be persuasive, SEO-optimised, and conversational for a general audience. Return a JSON object with the following exact fields:

1. "Title": Event name (plain text - exactly as it is referenced in the source, but use colon+space as the divider instead of dashes, vertical bars, or other syntax). Do not generate your own title. If the title is not found, return null. **If the title is "None" or "", then all other fields must also be returned as null.**

2. "Dates": Return all event dates in a compact, human-readable, single-line string. Follow these format rules:
- If dates omit the year (e.g. "Saturday, 7 Jun"), assume current year: "7 Jun 2025"
- Use "DD MM YYYY, HH:MM–HH:MM" for a single event
- For a range: "DD–DD MM YYYY, HH:MM–HH:MM"
- Multiple dates, same month/year: "12, 18, 26 Jun 2025, HH:MM–HH:MM"
- Across months: "26 Jun, 24 Jul, 25 Sep 2025, HH:MM–HH:MM"
- Different times: "26 Jun, 10:00–12:00; 24 Jul, 14:00–16:00; 2025"
- Different years: "27 Jun 2025, 10:00–12:00; 24 Jul 2026, 14:00–16:00"
- Flexible/online-only: "Jun 2025" or "26–28 Jun 2025"
- Use 24-hour time format
- No lists, arrays, or line breaks

3. "IndexIntro": A 1–2 sentence summary of the event (do not repeat the title). Append the formatted event date at the end in one of these forms:
- Single-day: "26 June 2025"
- Multi-day: "26–28 June 2025"
- Spanning months: "26 June–4 July 2025"

4. "Intro": Same as IndexIntro but omit the date.

5. "Content": A ~200-word SEO-optimised event description. It must be persuasive, conversational, and informative—covering value, themes, and expected outcomes. Paragraphs allowed.

6. "DateOrder": Last occurring event date in "YYYYMMDD" format.
- Use final date for multi-day or scattered events.
- For flexible or month-only events, use the last day of the mentioned month.
- Use the same day for single-date events.

7. "Location": Format as "Venue Name, Address, City, Country". If hybrid or online, append "and online".

8. "Cost": Include pricing details (all tiers if available) or "Free".

9. "Categories": Choose one or more from the below, in a json list:
- "Conferences and Networking Events" → for industry conferences, networking socials, places to meet clients and collaborators
- "Education, Training and CPD" → seminars for exchanging knowledge, CPD accredited training events, day courses, academic conferences, creative workshops.
- "Cultural Events and Exhibitions" → design festivals, talks by architects, walking tours, architectural films, exhibitions.

**Strict rules:**
- All fields must be returned as JSON.
- Only "Categories" may be returned as [] (empty list) if no suitable match is found. All other fields are strictly required.
- If either "Title" or "Dates" is null, then all fields must be returned as null.
- If the event appears expired, ended, or clearly sold out, then return all fields as null.
- Do not output markdown, bullet points, or any commentary.
- Final output must be a valid JSON object using null (not the string "null") where applicable.

**Event context:**
{input_text}

**Example JSON Output:**
{{
  "Title": "Design Futures: Exploring Tomorrow’s Spaces",
  "Dates": "12, 18, 26 Jun 2025, 10:00–17:00",
  "IndexIntro": "Join thought leaders in design and architecture as they discuss the future of spaces and sustainability. 12, 18, 26 June 2025",
  "Intro": "Join thought leaders in design and architecture as they discuss the future of spaces and sustainability.",
  "Content": "generated content",
  "DateOrder": "20250626",
  "Location": "RIBA, 66 Portland Place, London, UK",
  "Cost": "£120 standard, £60 students",
  "Categories": ["Conferences and Networking Events", "Education, Training and CPD", "Cultural Events and Exhibitions"]
}}
    """