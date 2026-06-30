

import html as _html
import os
from datetime import datetime

from langchain_core.tools import tool


# _BASE_CSS = """
# * { box-sizing: border-box; }
# body {
#   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
#   background: #f7f6f3;
#   color: #2c2c2a;
#   margin: 0;
#   padding: 40px 20px;
#   line-height: 1.6;
# }
# .container { max-width: 760px; margin: 0 auto; }
# .hero {
#   background: #ffffff;
#   border: 0.5px solid #e3e1d9;
#   border-radius: 16px;
#   padding: 32px;
#   margin-bottom: 24px;
# }
# .hero h1 { font-size: 26px; font-weight: 600; margin: 0 0 8px; }
# .hero .summary { color: #5f5e5a; font-size: 15px; margin: 0 0 14px; }
# .hero .meta { display: flex; gap: 18px; flex-wrap: wrap; font-size: 13px; color: #5f5e5a; }
# .card {
#   background: #ffffff;
#   border: 0.5px solid #e3e1d9;
#   border-radius: 16px;
#   padding: 24px 28px;
#   margin-bottom: 16px;
# }
# .card.featured { border: 2px solid #378ADD; }
# .badge {
#   display: inline-block;
#   font-size: 11px;
#   font-weight: 600;
#   padding: 3px 10px;
#   border-radius: 20px;
#   margin-bottom: 8px;
# }
# .row { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
# .title { font-size: 17px; font-weight: 600; margin: 0 0 2px; }
# .subtitle { font-size: 13.5px; color: #5f5e5a; margin: 0 0 10px; }
# .price { font-size: 20px; font-weight: 600; }
# .divider { border-top: 0.5px solid #e3e1d9; margin: 14px 0; }
# .kv { font-size: 13.5px; color: #5f5e5a; margin: 3px 0; }
# .kv b { color: #2c2c2a; font-weight: 500; }
# ul.plain { margin: 6px 0; padding-left: 18px; font-size: 13.5px; color: #5f5e5a; }
# ul.plain li { margin-bottom: 4px; }
# .tag {
#   display: inline-block;
#   font-size: 11.5px;
#   background: #f1efe8;
#   color: #5f5e5a;
#   padding: 3px 9px;
#   border-radius: 20px;
#   margin: 2px 4px 2px 0;
# }
# .footer { text-align: center; font-size: 11px; color: #b4b2a9; margin-top: 16px; }
# .section-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #999380; margin: 0 0 12px; }
# """

_BASE_CSS = """
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0c0c10;
  color: rgba(255,255,255,0.85);
  margin: 0;
  padding: 40px 20px;
  line-height: 1.6;
}
.container { max-width: 760px; margin: 0 auto; }
.hero {
  background: #121216;
  border: 0.5px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
}
.hero h1 { font-size: 26px; font-weight: 600; margin: 0 0 8px; color: #fff; }
.hero .summary { color: rgba(255,255,255,0.5); font-size: 15px; margin: 0 0 14px; }
.hero .meta { display: flex; gap: 18px; flex-wrap: wrap; font-size: 13px; color: rgba(255,255,255,0.45); }
.card {
  background: #121216;
  border: 0.5px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 16px;
}
.card.featured { border: 2px solid #a78bfa; }
.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  margin-bottom: 8px;
}
.row { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.title { font-size: 17px; font-weight: 600; margin: 0 0 2px; color: #fff; }
.subtitle { font-size: 13.5px; color: rgba(255,255,255,0.45); margin: 0 0 10px; }
.price { font-size: 20px; font-weight: 600; color: #fff; }
.divider { border-top: 0.5px solid rgba(255,255,255,0.08); margin: 14px 0; }
.kv { font-size: 13.5px; color: rgba(255,255,255,0.5); margin: 3px 0; }
.kv b { color: rgba(255,255,255,0.85); font-weight: 500; }
ul.plain { margin: 6px 0; padding-left: 18px; font-size: 13.5px; color: rgba(255,255,255,0.5); }
ul.plain li { margin-bottom: 4px; }
.tag {
  display: inline-block;
  font-size: 11.5px;
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.55);
  padding: 3px 9px;
  border-radius: 20px;
  margin: 2px 4px 2px 0;
}
.footer { text-align: center; font-size: 11px; color: rgba(255,255,255,0.2); margin-top: 16px; }
.section-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: rgba(255,255,255,0.35); margin: 0 0 12px; }
"""

_CATEGORY_STYLE = {
    "sightseeing": ("#0C447C", "#E6F1FB", "\u25C8"),
    "food": ("#993C1D", "#FAECE7", "\u2615"),
    "nature": ("#27500A", "#EAF3DE", "\u2618"),
    "museum": ("#3C3489", "#EEEDFE", "\u25A0"),
    "shopping": ("#72243E", "#FBEAF0", "\u25CF"),
    "nightlife": ("#633806", "#FAEEDA", "\u2605"),
    "transit": ("#444441", "#F1EFE8", "\u2192"),
    "relaxation": ("#085041", "#E1F5EE", "\u2740"),
    "adventure": ("#791F1F", "#FCEBEB", "\u25B2"),
    "culture": ("#3C3489", "#EEEDFE", "\u25C6"),
}
_DEFAULT_STYLE = ("#444441", "#F1EFE8", "\u25CF")


def _style_for(category):
    return _CATEGORY_STYLE.get((category or "").strip().lower(), _DEFAULT_STYLE)


def _esc(text):
    return _html.escape(str(text)) if text not in (None, "") else ""


def _wrap_document(title, body_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<style>{_BASE_CSS}</style>
</head>
<body>
  <div class="container">
    {body_html}
    <div class="footer">Generated on {datetime.now().strftime("%B %d, %Y")}</div>
  </div>
</body>
</html>"""


def _save(html_doc, prefix):
    os.makedirs("rendered_html", exist_ok=True)
    filename = f"rendered_html/{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w") as f:
        f.write(html_doc)
    return filename


# itinerary agent
@tool
def render_itinerary_html(
    trip_title: str,
    days: list,
    destination: str = "",
    summary: str = "",
    season: str = "",
    general_tips: list = None,
) -> dict:
    """
    Render a complete day-by-day travel itinerary as a styled HTML document.
    Call this once you have finalized the full itinerary plan for the user,
    instead of returning the plan as plain markdown text.

    Args:
        trip_title (str): Short title, e.g. "4 Days in New York City".
        destination (str): City/region name, e.g. "New York, USA".
        summary (str): 1-2 sentence overview of the trip's vibe and pace.
        season (str): Best season/time of year for this trip, e.g. "Spring or fall".
        general_tips (list[str]): 2-5 trip-wide practical tips.
        days (list[dict]): Ordered list of day plans. Each item:
            {
              "day_number": int,
              "title": str,            # short theme, e.g. "Midtown classics"
              "narrative": str,        # 1 sentence describing the day's flow
              "stops": [
                {
                  "time": str,                # e.g. "9:00 AM"
                  "name": str,                # place/activity name
                  "category": str,            # sightseeing|food|nature|museum|
                                               # shopping|nightlife|transit|
                                               # relaxation|adventure|culture
                  "duration_minutes": int,     # optional
                  "notes": str,                # optional practical tip
                  "food": str,                 # optional food/drink recommendation
                }, ...
              ]
            }

    Returns:
        dict: {"html": <full HTML document string>, "saved_to": <file path>}
    """
    general_tips = general_tips or []
    day_blocks = []

    for day in days:
        stop_rows = []
        for stop in day.get("stops", []):
            color, bg, icon = _style_for(stop.get("category"))
            duration = stop.get("duration_minutes")
            duration_txt = f"{duration} min" if duration else ""
            stop_rows.append(f"""
            <div style="display:grid;grid-template-columns:70px 24px 1fr;">
              <div style="font-size:12px;color:#888780;padding-top:14px;white-space:nowrap;">{_esc(stop.get("time",""))}</div>
              <div style="display:flex;flex-direction:column;align-items:center;">
                <div style="width:10px;height:10px;border-radius:50%;margin-top:16px;background:{color};"></div>
                <div style="width:2px;flex:1;background:#e3e1d9;margin-top:4px;"></div>
              </div>
              <div style="padding:8px 0 22px 16px;">
                <div class="row" style="margin-bottom:4px;">
                  <span class="badge" style="color:{color};background:{bg}">{icon} {_esc(stop.get("category","").title())}</span>
                  {f'<span style="font-size:12px;color:#999380;">{_esc(duration_txt)}</span>' if duration_txt else ''}
                </div>
                <div class="title" style="font-size:16px;">{_esc(stop.get("name",""))}</div>
                {f'<div class="kv">{_esc(stop.get("notes",""))}</div>' if stop.get("notes") else ''}
                {f'<div class="kv">&#127860; {_esc(stop.get("food",""))}</div>' if stop.get("food") else ''}
              </div>
            </div>""")

        day_blocks.append(f"""
        <div class="card">
          <div class="row" style="margin-bottom:2px;">
            <span class="badge" style="color:#5f5e5a;background:#f1efe8;">Day {_esc(day.get("day_number",""))}</span>
            {f'<span class="title" style="font-size:18px;">{_esc(day.get("title",""))}</span>' if day.get("title") else ''}
          </div>
          {f'<p class="subtitle">{_esc(day.get("narrative",""))}</p>' if day.get("narrative") else ''}
          {''.join(stop_rows)}
        </div>""")

    tips_html = ""
    if general_tips:
        tips_html = f"""
        <div class="card">
          <div class="section-title">Good to know</div>
          <ul class="plain">{''.join(f"<li>{_esc(t)}</li>" for t in general_tips)}</ul>
        </div>"""

    meta = []
    if destination:
        meta.append(f"<span>&#128205; {_esc(destination)}</span>")
    if season:
        meta.append(f"<span>&#9728; {_esc(season)}</span>")
    if days:
        meta.append(f"<span>&#128197; {len(days)} day{'s' if len(days) != 1 else ''}</span>")

    body = f"""
    <div class="hero">
      <h1>{_esc(trip_title)}</h1>
      {f'<p class="summary">{_esc(summary)}</p>' if summary else ''}
      <div class="meta">{''.join(meta)}</div>
    </div>
    {''.join(day_blocks)}
    {tips_html}
    """

    doc = _wrap_document(trip_title, body)
    return {"html": doc, "saved_to": _save(doc, "itinerary")}


# # hotel agent
# @tool
# def render_hotel_options_html(
#     destination: str,
#     dates: str,
#     hotels: list,
#     best_overall: str = "",
#     best_budget: str = "",
#     best_premium: str = "",
# ) -> dict:
#     """
#     Render ranked hotel options as a styled HTML document with comparison cards.
#     Call this once you have shortlisted and ranked the final hotel options,
#     instead of returning the list as plain markdown text.

#     Args:
#         destination (str): City/area searched, e.g. "Dubai".
#         dates (str): Stay dates, e.g. "June 10-15, 2026".
#         hotels (list[dict]): Ranked hotel list, best first. Each item:
#             {
#               "name": str,
#               "price_range": str,       # e.g. "$120-150/night"
#               "rating": str,            # e.g. "4.6/5"
#               "location": str,          # e.g. "Downtown, 5 min from metro"
#               "amenities": list[str],   # e.g. ["WiFi", "Pool", "Breakfast"]
#               "pros": list[str],
#               "cons": list[str],
#               "why_recommended": str,
#             }
#         best_overall (str): Name of the best overall pick (highlighted card).
#         best_budget (str): Name of the best budget pick.
#         best_premium (str): Name of the best premium pick.

#     Returns:
#         dict: {"html": <full HTML document string>, "saved_to": <file path>}
#     """
#     cards = []
#     for hotel in hotels:
#         name = hotel.get("name", "")
#         is_featured = name == best_overall
#         amenities = hotel.get("amenities", [])
#         pros = hotel.get("pros", [])
#         cons = hotel.get("cons", [])

#         tags = "".join(f'<span class="tag">{_esc(a)}</span>' for a in amenities)
#         badge_html = ""
#         if name == best_overall:
#             badge_html = '<span class="badge" style="color:#0C447C;background:#E6F1FB;">Best overall</span>'
#         elif name == best_budget:
#             badge_html = '<span class="badge" style="color:#27500A;background:#EAF3DE;">Best budget</span>'
#         elif name == best_premium:
#             badge_html = '<span class="badge" style="color:#3C3489;background:#EEEDFE;">Best premium</span>'

#         pros_html = "".join(f"<li>{_esc(p)}</li>" for p in pros)
#         cons_html = "".join(f"<li>{_esc(c)}</li>" for c in cons)

#         cards.append(f"""
#         <div class="card{' featured' if is_featured else ''}">
#           {badge_html}
#           <div class="row">
#             <div>
#               <div class="title">{_esc(name)}</div>
#               <div class="subtitle">{_esc(hotel.get("location",""))}</div>
#             </div>
#             <div style="text-align:right;">
#               <div class="price">{_esc(hotel.get("price_range",""))}</div>
#               {f'<div class="kv">&#9733; {_esc(hotel.get("rating",""))}</div>' if hotel.get("rating") else ''}
#             </div>
#           </div>
#           {f'<div style="margin-top:8px;">{tags}</div>' if tags else ''}
#           {f'<div class="kv" style="margin-top:10px;">{_esc(hotel.get("why_recommended",""))}</div>' if hotel.get("why_recommended") else ''}
#           {f'''<div class="divider"></div>
#           <div style="display:flex;gap:24px;flex-wrap:wrap;">
#             {f'<div style="flex:1;min-width:200px;"><div class="kv"><b>Pros</b></div><ul class="plain">{pros_html}</ul></div>' if pros else ''}
#             {f'<div style="flex:1;min-width:200px;"><div class="kv"><b>Cons</b></div><ul class="plain">{cons_html}</ul></div>' if cons else ''}
#           </div>''' if (pros or cons) else ''}
#         </div>""")

#     body = f"""
#     <div class="hero">
#       <h1>Hotels in {_esc(destination)}</h1>
#       <p class="summary">{_esc(dates)}</p>
#     </div>
#     {''.join(cards)}
#     """

#     doc = _wrap_document(f"Hotels in {destination}", body)
#     return {"html": doc, "saved_to": _save(doc, "hotels")}


# # flight agent
# @tool
# def render_flight_options_html(
#     route: str,
#     dates: str,
#     flights: list,
#     best_overall: str = "",
#     best_budget: str = "",
#     best_fastest: str = "",
# ) -> dict:
#     """
#     Render ranked flight options as a styled HTML document with comparison cards.
#     Call this once you have shortlisted and ranked the final flight options,
#     instead of returning the list as plain markdown text.

#     Args:
#         route (str): Route searched, e.g. "Chennai to Dubai".
#         dates (str): Travel dates, e.g. "June 10, 2026".
#         flights (list[dict]): Ranked flight list, best first. Each item:
#             {
#               "airline": str,             # e.g. "IndiGo 6E 123"
#               "departure_time": str,
#               "arrival_time": str,
#               "duration": str,            # e.g. "3h 45m"
#               "stops": str,                # e.g. "Non-stop" or "1 stop (DOH, 2h layover)"
#               "price": str,                # e.g. "$320"
#               "notes": str,                # optional, e.g. baggage info
#             }
#         best_overall (str): Airline/flight-number string of the best overall pick.
#         best_budget (str): Airline/flight-number string of the best budget pick.
#         best_fastest (str): Airline/flight-number string of the fastest pick.

#     Returns:
#         dict: {"html": <full HTML document string>, "saved_to": <file path>}
#     """
#     cards = []
#     for flight in flights:
#         airline = flight.get("airline", "")
#         is_featured = airline == best_overall

#         badge_html = ""
#         if airline == best_overall:
#             badge_html = '<span class="badge" style="color:#0C447C;background:#E6F1FB;">Best overall</span>'
#         elif airline == best_budget:
#             badge_html = '<span class="badge" style="color:#27500A;background:#EAF3DE;">Best budget</span>'
#         elif airline == best_fastest:
#             badge_html = '<span class="badge" style="color:#3C3489;background:#EEEDFE;">Fastest</span>'

#         cards.append(f"""
#         <div class="card{' featured' if is_featured else ''}">
#           {badge_html}
#           <div class="row">
#             <div class="title">{_esc(airline)}</div>
#             <div class="price">{_esc(flight.get("price",""))}</div>
#           </div>
#           <div class="row" style="margin-top:6px;">
#             <div class="kv"><b>{_esc(flight.get("departure_time",""))}</b> &#8594; <b>{_esc(flight.get("arrival_time",""))}</b></div>
#             <div class="kv">{_esc(flight.get("duration",""))}</div>
#           </div>
#           <div class="kv" style="margin-top:4px;">{_esc(flight.get("stops",""))}</div>
#           {f'<div class="kv" style="margin-top:6px;">{_esc(flight.get("notes",""))}</div>' if flight.get("notes") else ''}
#         </div>""")

#     body = f"""
#     <div class="hero">
#       <h1>Flights: {_esc(route)}</h1>
#       <p class="summary">{_esc(dates)}</p>
#     </div>
#     {''.join(cards)}
#     """

#     doc = _wrap_document(f"Flights: {route}", body)
#     return {"html": doc, "saved_to": _save(doc, "flights")}


# # generic supervisor
# @tool
# def render_generic_html(title: str, sections: list) -> dict:
#     """
#     Render a free-form styled HTML document from generic structured sections.
#     Use this ONLY for the final combined trip summary, or for content that
#     doesn't fit the itinerary/hotel/flight card formats (e.g. a weather
#     note, a budget breakdown, a packing list, a merged trip overview).
#     Do not use this in place of render_itinerary_html, render_hotel_options_html,
#     or render_flight_options_html -- prefer those for their respective domains.

#     Args:
#         title (str): Document title, e.g. "Your Trip to Dubai".
#         sections (list[dict]): Ordered content blocks. Each item:
#             {
#               "heading": str,             # section heading, e.g. "Budget breakdown"
#               "body": str,                # optional plain paragraph text
#               "bullets": list[str],       # optional bullet list
#               "key_values": list[dict],   # optional [{"key": "Total", "value": "$1,240"}]
#             }

#     Returns:
#         dict: {"html": <full HTML document string>, "saved_to": <file path>}
#     """
#     blocks = []
#     for section in sections:
#         heading = section.get("heading", "")
#         body_text = section.get("body", "")
#         bullets = section.get("bullets", [])
#         key_values = section.get("key_values", [])

#         bullets_html = "".join(f"<li>{_esc(b)}</li>" for b in bullets)
#         kv_html = "".join(
#             f'<div class="kv"><b>{_esc(kv.get("key",""))}:</b> {_esc(kv.get("value",""))}</div>'
#             for kv in key_values
#         )

#         blocks.append(f"""
#         <div class="card">
#           {f'<div class="section-title">{_esc(heading)}</div>' if heading else ''}
#           {f'<p class="kv">{_esc(body_text)}</p>' if body_text else ''}
#           {f'<ul class="plain">{bullets_html}</ul>' if bullets else ''}
#           {kv_html}
#         </div>""")

#     body = f"""
#     <div class="hero"><h1>{_esc(title)}</h1></div>
#     {''.join(blocks)}
#     """

#     doc = _wrap_document(title, body)
#     return {"html": doc, "saved_to": _save(doc, "summary")}


# ---------------------------------------------------------------------------
# 2. HOTEL TOOL (hotel_agent)
# ---------------------------------------------------------------------------
@tool
def render_hotel_options_html(
    destination: str,
    dates: str,
    hotels: list,
    best_overall: str = "",
    best_budget: str = "",
    best_premium: str = "",
) -> dict:
    """
    Render ranked hotel options as a styled HTML document with comparison cards.
    Call this once you have shortlisted and ranked the final hotel options,
    instead of returning the list as plain markdown text.
    Args:
        destination (str): City/area searched, e.g. "Dubai".
        dates (str): Stay dates, e.g. "June 10-15, 2026".
        hotels (list[dict]): Ranked hotel list, best first. Each item:
            {
              "name": str,
              "price_range": str,       # e.g. "$120-150/night"
              "rating": str,            # e.g. "4.6/5"
              "location": str,          # e.g. "Downtown, 5 min from metro"
              "amenities": list[str],   # e.g. ["WiFi", "Pool", "Breakfast"]
              "pros": list[str],
              "cons": list[str],
              "why_recommended": str,
            }
        best_overall (str): Name of the best overall pick (highlighted card).
        best_budget (str): Name of the best budget pick.
        best_premium (str): Name of the best premium pick.
    Returns:
        dict: {"html": <full HTML document string>, "saved_to": <file path>}
    """
    _HOTEL_CSS = """
    <style>
    .htl-hero {
      position: relative; overflow: hidden;
      background: radial-gradient(120% 140% at 0% 0%, rgba(167,139,250,0.16), transparent 60%),
                  radial-gradient(120% 140% at 100% 0%, rgba(56,189,248,0.12), transparent 55%),
                  #121216;
      border: 0.5px solid rgba(255,255,255,0.08);
      border-radius: 20px; padding: 36px 36px 30px;
    }
    .htl-hero .eyebrow {
      font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
      color: rgba(167,139,250,0.85); font-weight: 600; margin-bottom: 10px;
    }
    .htl-hero h1 { font-size: 30px; font-weight: 700; margin: 0 0 6px; color: #fff; letter-spacing: -0.01em; }
    .htl-hero .dates { font-size: 14px; color: rgba(255,255,255,0.45); }
    .htl-card {
      position: relative;
      background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
      border: 0.5px solid rgba(255,255,255,0.09);
      border-radius: 18px; padding: 26px 28px; margin-top: 18px;
      transition: border-color 0.2s;
    }
    .htl-card.featured {
      border: 1px solid rgba(251,191,36,0.55);
      box-shadow: 0 0 0 1px rgba(251,191,36,0.12), 0 16px 40px -16px rgba(251,191,36,0.25);
      background: linear-gradient(180deg, rgba(251,191,36,0.07), rgba(255,255,255,0.015));
    }
    .htl-rank {
      position: absolute; top: -14px; left: 24px;
      width: 30px; height: 30px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      background: #1a1a20; border: 0.5px solid rgba(255,255,255,0.15);
      font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.55);
      font-family: 'JetBrains Mono', monospace;
    }
    .htl-card.featured .htl-rank {
      background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #1a1409; border: none;
    }
    .htl-ribbon {
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 10.5px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
      padding: 4px 12px; border-radius: 20px; margin-bottom: 14px;
    }
    .htl-ribbon.overall { background: rgba(251,191,36,0.16); color: #fbbf24; border: 0.5px solid rgba(251,191,36,0.4); }
    .htl-ribbon.budget { background: rgba(52,211,153,0.14); color: #34d399; border: 0.5px solid rgba(52,211,153,0.35); }
    .htl-ribbon.premium { background: rgba(167,139,250,0.14); color: #a78bfa; border: 0.5px solid rgba(167,139,250,0.35); }
    .htl-top-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
    .htl-name { font-size: 20px; font-weight: 700; color: #fff; margin: 0 0 4px; letter-spacing: -0.01em; }
    .htl-loc { font-size: 13px; color: rgba(255,255,255,0.45); display: flex; align-items: center; gap: 5px; }
    .htl-price-box { text-align: right; flex-shrink: 0; }
    .htl-price { font-size: 22px; font-weight: 700; color: #fff; }
    .htl-price small { font-size: 11px; font-weight: 400; color: rgba(255,255,255,0.4); }
    .htl-stars { font-size: 13px; color: #fbbf24; margin-top: 4px; letter-spacing: 1px; }
    .htl-amenities { display: flex; flex-wrap: wrap; gap: 7px; margin: 16px 0 4px; }
    .htl-amenity {
      font-size: 11.5px; padding: 5px 12px; border-radius: 20px;
      background: rgba(255,255,255,0.05); border: 0.5px solid rgba(255,255,255,0.1);
      color: rgba(255,255,255,0.6);
    }
    .htl-quote {
      margin: 16px 0 0; padding: 14px 16px; border-left: 2px solid #a78bfa;
      background: rgba(167,139,250,0.06); border-radius: 0 10px 10px 0;
      font-size: 13px; color: rgba(255,255,255,0.7); font-style: italic; line-height: 1.6;
    }
    .htl-divider { border-top: 0.5px solid rgba(255,255,255,0.08); margin: 20px 0 16px; }
    .htl-pc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
    .htl-pc-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
    .htl-pc-label.pro { color: #34d399; } .htl-pc-label.con { color: #f87171; }
    .htl-pc-list { list-style: none; margin: 0; padding: 0; }
    .htl-pc-list li { font-size: 12.5px; color: rgba(255,255,255,0.6); padding: 3px 0 3px 18px; position: relative; line-height: 1.5; }
    .htl-pc-list.pro li::before { content: "✓"; position: absolute; left: 0; color: #34d399; font-weight: 700; }
    .htl-pc-list.con li::before { content: "✕"; position: absolute; left: 0; color: #f87171; font-weight: 700; }
    @media (max-width: 520px) { .htl-pc-grid { grid-template-columns: 1fr; } }
    </style>
    """
    cards = []
    for idx, hotel in enumerate(hotels, start=1):
        name = hotel.get("name", "")
        is_featured = name == best_overall
        amenities = hotel.get("amenities", [])
        pros = hotel.get("pros", [])
        cons = hotel.get("cons", [])
        rating_raw = hotel.get("rating", "")
        try:
            score = float(str(rating_raw).split("/")[0].strip())
        except (ValueError, IndexError):
            score = 0
        full_stars = int(round(score))
        stars = "★" * max(0, min(full_stars, 5)) + "☆" * (5 - max(0, min(full_stars, 5)))
        tags = "".join(f'<span class="htl-amenity">{_esc(a)}</span>' for a in amenities)
        ribbon_html = ""
        if name == best_overall:
            ribbon_html = '<span class="htl-ribbon overall">★ Best Overall</span>'
        elif name == best_budget:
            ribbon_html = '<span class="htl-ribbon budget">◆ Best Budget</span>'
        elif name == best_premium:
            ribbon_html = '<span class="htl-ribbon premium">✦ Best Premium</span>'
        pros_html = "".join(f"<li>{_esc(p)}</li>" for p in pros)
        cons_html = "".join(f"<li>{_esc(c)}</li>" for c in cons)
        cards.append(f"""
        <div class="htl-card{' featured' if is_featured else ''}">
          <div class="htl-rank">{idx}</div>
          {ribbon_html}
          <div class="htl-top-row">
            <div>
              <div class="htl-name">{_esc(name)}</div>
              <div class="htl-loc">&#128205; {_esc(hotel.get("location",""))}</div>
            </div>
            <div class="htl-price-box">
              <div class="htl-price">{_esc(hotel.get("price_range",""))}</div>
              {f'<div class="htl-stars">{stars} <small style="color:rgba(255,255,255,0.4);">{_esc(rating_raw)}</small></div>' if rating_raw else ''}
            </div>
          </div>
          {f'<div class="htl-amenities">{tags}</div>' if tags else ''}
          {f'<div class="htl-quote">&#8220;{_esc(hotel.get("why_recommended",""))}&#8221;</div>' if hotel.get("why_recommended") else ''}
          {f'''<div class="htl-divider"></div>
          <div class="htl-pc-grid">
            {f'<div><div class="htl-pc-label pro">Pros</div><ul class="htl-pc-list pro">{pros_html}</ul></div>' if pros else ''}
            {f'<div><div class="htl-pc-label con">Cons</div><ul class="htl-pc-list con">{cons_html}</ul></div>' if cons else ''}
          </div>''' if (pros or cons) else ''}
        </div>""")
    body = f"""
    {_HOTEL_CSS}
    <div class="htl-hero">
      <div class="eyebrow">Hotel Search</div>
      <h1>Stays in {_esc(destination)}</h1>
      <div class="dates">&#128197; {_esc(dates)} &nbsp;&middot;&nbsp; {len(hotels)} options ranked</div>
    </div>
    {''.join(cards)}
    """
    doc = _wrap_document(f"Hotels in {destination}", body)
    return {"html": doc, "saved_to": _save(doc, "hotels")}


# ---------------------------------------------------------------------------
# 3. FLIGHT TOOL (flight_agent)
# ---------------------------------------------------------------------------
@tool
def render_flight_options_html(
    route: str,
    dates: str,
    flights: list,
    best_overall: str = "",
    best_budget: str = "",
    best_fastest: str = "",
) -> dict:
    """
    Render ranked flight options as a styled HTML document with comparison cards.
    Call this once you have shortlisted and ranked the final flight options,
    instead of returning the list as plain markdown text.
    Args:
        route (str): Route searched, e.g. "Chennai to Dubai".
        dates (str): Travel dates, e.g. "June 10, 2026".
        flights (list[dict]): Ranked flight list, best first. Each item:
            {
              "airline": str,             # e.g. "IndiGo 6E 123"
              "departure_time": str,
              "arrival_time": str,
              "duration": str,            # e.g. "3h 45m"
              "stops": str,                # e.g. "Non-stop" or "1 stop (DOH, 2h layover)"
              "price": str,                # e.g. "$320"
              "notes": str,                # optional, e.g. baggage info
            }
        best_overall (str): Airline/flight-number string of the best overall pick.
        best_budget (str): Airline/flight-number string of the best budget pick.
        best_fastest (str): Airline/flight-number string of the fastest pick.
    Returns:
        dict: {"html": <full HTML document string>, "saved_to": <file path>}
    """
    _FLIGHT_CSS = """
    <style>
    .flt-hero {
      position: relative; overflow: hidden;
      background: radial-gradient(120% 140% at 0% 0%, rgba(56,189,248,0.16), transparent 60%),
                  radial-gradient(120% 140% at 100% 0%, rgba(167,139,250,0.12), transparent 55%),
                  #121216;
      border: 0.5px solid rgba(255,255,255,0.08);
      border-radius: 20px; padding: 36px;
    }
    .flt-hero .eyebrow {
      font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
      color: rgba(56,189,248,0.9); font-weight: 600; margin-bottom: 10px;
    }
    .flt-hero h1 { font-size: 28px; font-weight: 700; margin: 0 0 6px; color: #fff; letter-spacing: -0.01em; }
    .flt-hero .dates { font-size: 14px; color: rgba(255,255,255,0.45); }
    .flt-card {
      position: relative;
      background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
      border: 0.5px solid rgba(255,255,255,0.09);
      border-radius: 18px; padding: 24px 28px; margin-top: 16px;
    }
    .flt-card.featured {
      border: 1px solid rgba(56,189,248,0.55);
      box-shadow: 0 0 0 1px rgba(56,189,248,0.12), 0 16px 40px -16px rgba(56,189,248,0.3);
      background: linear-gradient(180deg, rgba(56,189,248,0.07), rgba(255,255,255,0.015));
    }
    .flt-rank {
      position: absolute; top: -14px; left: 24px;
      width: 30px; height: 30px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      background: #1a1a20; border: 0.5px solid rgba(255,255,255,0.15);
      font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.55);
      font-family: 'JetBrains Mono', monospace;
    }
    .flt-card.featured .flt-rank {
      background: linear-gradient(135deg, #38bdf8, #818cf8); color: #06121a; border: none;
    }
    .flt-ribbon {
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 10.5px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
      padding: 4px 12px; border-radius: 20px; margin-bottom: 14px;
    }
    .flt-ribbon.overall { background: rgba(56,189,248,0.16); color: #38bdf8; border: 0.5px solid rgba(56,189,248,0.4); }
    .flt-ribbon.budget { background: rgba(52,211,153,0.14); color: #34d399; border: 0.5px solid rgba(52,211,153,0.35); }
    .flt-ribbon.fastest { background: rgba(251,191,36,0.14); color: #fbbf24; border: 0.5px solid rgba(251,191,36,0.35); }
    .flt-top-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
    .flt-airline { font-size: 17px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }
    .flt-emblem {
      width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(167,139,250,0.2));
      border: 0.5px solid rgba(255,255,255,0.12);
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 700; color: #38bdf8; font-family: 'JetBrains Mono', monospace;
    }
    .flt-price { font-size: 22px; font-weight: 700; color: #fff; }
    .flt-timeline {
      display: grid; grid-template-columns: auto 1fr auto; align-items: center;
      gap: 14px; margin: 20px 0 6px;
    }
    .flt-time { font-size: 18px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; }
    .flt-time-label { font-size: 10px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }
    .flt-path { position: relative; height: 2px; background: rgba(255,255,255,0.12); margin: 0 4px; }
    .flt-path::before, .flt-path::after {
      content: ""; position: absolute; top: 50%; transform: translateY(-50%);
      width: 6px; height: 6px; border-radius: 50%; background: #38bdf8;
    }
    .flt-path::before { left: -2px; } .flt-path::after { right: -2px; }
    .flt-plane { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -55%); font-size: 13px; color: #38bdf8; background: #121216; padding: 0 4px; }
    .flt-duration-badge {
      position: absolute; top: -22px; left: 50%; transform: translateX(-50%);
      font-size: 10.5px; color: rgba(255,255,255,0.45); white-space: nowrap;
      font-family: 'JetBrains Mono', monospace;
    }
    .flt-meta-row { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 10px; }
    .flt-meta { font-size: 12.5px; color: rgba(255,255,255,0.5); display: flex; align-items: center; gap: 6px; }
    .flt-stop-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.3); display: inline-block; }
    .flt-stop-dot.nonstop { background: #34d399; }
    .flt-notes {
      margin-top: 14px; padding: 11px 14px; border-radius: 10px;
      background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.07);
      font-size: 12px; color: rgba(255,255,255,0.45);
    }
    </style>
    """
    cards = []
    for idx, flight in enumerate(flights, start=1):
        airline = flight.get("airline", "")
        is_featured = airline == best_overall
        is_nonstop = "non-stop" in flight.get("stops", "").lower() or "nonstop" in flight.get("stops", "").lower() or "direct" in flight.get("stops", "").lower()
        initials = "".join(w[0] for w in airline.split()[:2]).upper() or "✈"
        ribbon_html = ""
        if airline == best_overall:
            ribbon_html = '<span class="flt-ribbon overall">★ Best Overall</span>'
        elif airline == best_budget:
            ribbon_html = '<span class="flt-ribbon budget">◆ Best Budget</span>'
        elif airline == best_fastest:
            ribbon_html = '<span class="flt-ribbon fastest">&#9889; Fastest</span>'
        cards.append(f"""
        <div class="flt-card{' featured' if is_featured else ''}">
          <div class="flt-rank">{idx}</div>
          {ribbon_html}
          <div class="flt-top-row">
            <div class="flt-airline"><span class="flt-emblem">{_esc(initials)}</span>{_esc(airline)}</div>
            <div class="flt-price">{_esc(flight.get("price",""))}</div>
          </div>
          <div class="flt-timeline">
            <div>
              <div class="flt-time">{_esc(flight.get("departure_time",""))}</div>
              <div class="flt-time-label">Departs</div>
            </div>
            <div class="flt-path">
              <span class="flt-duration-badge">{_esc(flight.get("duration",""))}</span>
              <span class="flt-plane">&#9992;</span>
            </div>
            <div style="text-align:right;">
              <div class="flt-time">{_esc(flight.get("arrival_time",""))}</div>
              <div class="flt-time-label">Arrives</div>
            </div>
          </div>
          <div class="flt-meta-row">
            <span class="flt-meta"><span class="flt-stop-dot{' nonstop' if is_nonstop else ''}"></span>{_esc(flight.get("stops",""))}</span>
          </div>
          {f'<div class="flt-notes">&#128221; {_esc(flight.get("notes",""))}</div>' if flight.get("notes") else ''}
        </div>""")
    body = f"""
    {_FLIGHT_CSS}
    <div class="flt-hero">
      <div class="eyebrow">Flight Search</div>
      <h1>{_esc(route)}</h1>
      <div class="dates">&#128197; {_esc(dates)} &nbsp;&middot;&nbsp; {len(flights)} options ranked</div>
    </div>
    {''.join(cards)}
    """
    doc = _wrap_document(f"Flights: {route}", body)
    return {"html": doc, "saved_to": _save(doc, "flights")}


# ---------------------------------------------------------------------------
# 4. GENERIC TOOL (supervisor only -- free-form fallback)
# ---------------------------------------------------------------------------
@tool
def render_generic_html(title: str, sections: list) -> dict:
    """
    Render a free-form styled HTML document from generic structured sections.
    Use this ONLY for the final combined trip summary, or for content that
    doesn't fit the itinerary/hotel/flight card formats (e.g. a weather
    note, a budget breakdown, a packing list, a merged trip overview).
    Do not use this in place of render_itinerary_html, render_hotel_options_html,
    or render_flight_options_html -- prefer those for their respective domains.
    Args:
        title (str): Document title, e.g. "Your Trip to Dubai".
        sections (list[dict]): Ordered content blocks. Each item:
            {
              "heading": str,             # section heading, e.g. "Budget breakdown"
              "body": str,                # optional plain paragraph text
              "bullets": list[str],       # optional bullet list
              "key_values": list[dict],   # optional [{"key": "Total", "value": "$1,240"}]
            }
    Returns:
        dict: {"html": <full HTML document string>, "saved_to": <file path>}
    """
    _GENERIC_CSS = """
    <style>
    .gen-hero {
      position: relative; overflow: hidden;
      background: radial-gradient(120% 160% at 0% 0%, rgba(167,139,250,0.18), transparent 55%),
                  radial-gradient(120% 160% at 100% 0%, rgba(52,211,153,0.12), transparent 55%),
                  #121216;
      border: 0.5px solid rgba(255,255,255,0.08);
      border-radius: 20px; padding: 38px 36px;
    }
    .gen-hero .eyebrow {
      font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
      color: rgba(167,139,250,0.85); font-weight: 600; margin-bottom: 10px;
    }
    .gen-hero h1 { font-size: 30px; font-weight: 700; margin: 0; color: #fff; letter-spacing: -0.01em; }
    .gen-section {
      background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
      border: 0.5px solid rgba(255,255,255,0.09);
      border-radius: 18px; padding: 26px 28px; margin-top: 16px;
    }
    .gen-head { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
    .gen-icon {
      width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: rgba(167,139,250,0.14); border: 0.5px solid rgba(167,139,250,0.3);
      font-size: 13px; color: #a78bfa;
    }
    .gen-heading { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(255,255,255,0.8); }
    .gen-body { font-size: 13.5px; color: rgba(255,255,255,0.6); line-height: 1.75; margin: 0 0 6px; }
    .gen-bullets { list-style: none; margin: 10px 0 0; padding: 0; }
    .gen-bullets li {
      font-size: 13px; color: rgba(255,255,255,0.62); padding: 6px 0 6px 22px; position: relative; line-height: 1.6;
      border-bottom: 0.5px solid rgba(255,255,255,0.05);
    }
    .gen-bullets li:last-child { border-bottom: none; }
    .gen-bullets li::before { content: "→"; position: absolute; left: 0; color: #a78bfa; font-weight: 700; }
    .gen-kv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 12px; }
    .gen-kv-box {
      background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08);
      border-radius: 12px; padding: 12px 14px;
    }
    .gen-kv-key { font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: rgba(255,255,255,0.35); margin-bottom: 4px; }
    .gen-kv-value { font-size: 16px; font-weight: 700; color: #fff; }
    </style>
    """
    _ICON_MAP = [
        (("budget", "cost", "price", "expense"), "&#128176;"),
        (("pack", "luggage", "bring"), "&#128092;"),
        (("weather", "climate", "forecast"), "&#9728;"),
        (("overview", "summary", "trip"), "&#128506;"),
        (("note", "tip", "caveat"), "&#128161;"),
        (("flight", "fly", "airport"), "&#9992;"),
        (("hotel", "stay", "accommodation"), "&#127968;"),
        (("itinerary", "schedule", "day"), "&#128197;"),
    ]

    def _icon_for(heading):
        h = (heading or "").lower()
        for keys, icon in _ICON_MAP:
            if any(k in h for k in keys):
                return icon
        return "&#9670;"
    blocks = []
    for section in sections:
        heading = section.get("heading", "")
        body_text = section.get("body", "")
        bullets = section.get("bullets", [])
        key_values = section.get("key_values", [])
        bullets_html = "".join(f"<li>{_esc(b)}</li>" for b in bullets)
        kv_html = "".join(
            f'<div class="gen-kv-box"><div class="gen-kv-key">{_esc(kv.get("key",""))}</div>'
            f'<div class="gen-kv-value">{_esc(kv.get("value",""))}</div></div>'
            for kv in key_values
        )
        blocks.append(f"""
        <div class="gen-section">
          {f'<div class="gen-head"><span class="gen-icon">{_icon_for(heading)}</span><span class="gen-heading">{_esc(heading)}</span></div>' if heading else ''}
          {f'<p class="gen-body">{_esc(body_text)}</p>' if body_text else ''}
          {f'<ul class="gen-bullets">{bullets_html}</ul>' if bullets else ''}
          {f'<div class="gen-kv-grid">{kv_html}</div>' if key_values else ''}
        </div>""")
    body = f"""
    {_GENERIC_CSS}
    <div class="gen-hero">
      <div class="eyebrow">Trip Summary</div>
      <h1>{_esc(title)}</h1>
    </div>
    {''.join(blocks)}
    """
    doc = _wrap_document(title, body)
    return {"html": doc, "saved_to": _save(doc, "summary")}


ITINERARY_HTML_ADDENDUM = """
## HTML rendering

You have a 4th tool: render_itinerary_html. Once you've built the final
day-wise plan (after using discover_attractions, estimate_travel_logistics,
and find_local_events as needed), call render_itinerary_html with the
structured plan instead of writing the itinerary out as plain text.

- Every stop must include time, name, and category. Category must be one
  of: sightseeing, food, nature, museum, shopping, nightlife, transit,
  relaxation, adventure, culture. Pick the closest match.
- Fill notes with practical tips (timing, booking, what makes it worth it)
  and food with a specific recommendation tied to that stop, when you
  have one. Leave blank rather than guessing.
- Keep stops within a day chronologically ordered and geographically grouped.
- Always include trip_title, destination, and a short summary.
- Use general_tips for 2-5 trip-wide tips (transit passes, weather, booking
  ahead) -- not a restated itinerary.
- After calling the tool, respond with at most 1-2 sentences highlighting
  anything important (e.g. a scheduling caveat) -- do not repeat the
  itinerary content, since the rendered HTML already shows it.
"""

HOTEL_HTML_ADDENDUM = """
## HTML rendering

You have a 3rd tool: render_hotel_options_html. Once you've shortlisted
and ranked your final hotel recommendations (after using search_hotels and
get_hotel_ratings_and_reviews), call render_hotel_options_html instead of
writing the comparison out as plain text.

- Include 3-7 ranked hotels, best first.
- Fill amenities, pros, and cons from real review/search data -- never
  invent them.
- Set best_overall, best_budget, and best_premium to the exact `name`
  string of the matching hotel in your `hotels` list (only set the ones
  that meaningfully apply -- leave blank rather than forcing a category).
- After calling the tool, respond with at most 1-2 sentences (e.g. a
  trade-off worth flagging) -- do not repeat the hotel list, since the
  rendered HTML already shows it.
"""

FLIGHT_HTML_ADDENDUM = """
## HTML rendering

You have a 4th tool: render_flight_options_html. Once you've shortlisted
and ranked your final flight recommendations (after using
analyze_flight_routes and search_flights, and get_flight_status if
relevant), call render_flight_options_html instead of writing the
comparison out as plain text.

- Include 3-7 ranked flights, best first.
- Use real data from search_flights/analyze_flight_routes only -- never
  invent prices, times, or airlines.
- Set best_overall, best_budget, and best_fastest to the exact `airline`
  string of the matching flight in your `flights` list (only set the ones
  that meaningfully apply).
- After calling the tool, respond with at most 1-2 sentences (e.g. a
  layover risk worth flagging) -- do not repeat the flight list, since the
  rendered HTML already shows it.
"""

SUPERVISOR_HTML_ADDENDUM = """
## HTML rendering

You have a 4th shared tool: render_generic_html. Use it ONLY for the final
combined trip summary that merges flight, hotel, and itinerary results
into one overview, or for standalone content that doesn't belong to any
single sub-agent's domain (e.g. a budget breakdown, a packing list, a
weather note). Do NOT use it as a substitute for the sub-agents' own
rendering tools -- the itinerary_agent, hotel_agent, and flight_agent
already render their own polished HTML internally; your job is to
present their already-rendered outputs together, not re-render their data
yourself.

- Call render_generic_html with one section per major part of the trip
  (e.g. "Trip overview", "Budget breakdown", "What to pack") -- not a
  catch-all single block.
- When a sub-agent already produced a render_*_html result earlier in the
  conversation, treat that as the answer for that domain. Don't re-call
  the sub-agent or duplicate that content inside render_generic_html.
- Keep each section's body, bullets, and key_values factual and sourced
  from what the agents/tools actually returned -- never invent prices,
  flight numbers, or hotel names here.
- After calling the tool, add at most 1-2 sentences of plain-text framing
  (e.g. "Here's everything pulled together") -- do not restate the content.
- This tool is for presentation only. It does not replace the existing
  "Conversational Messages -- Do NOT Delegate" rule: simple acknowledgements
  and greetings still get a plain-text reply with no tool calls at all.
"""
