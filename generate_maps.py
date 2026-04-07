#!/usr/bin/env python3
"""Generate interactive Folium HTML maps and static PNG map images for the trip.
Uses OSRM (Open Source Routing Machine) for actual road-following routes."""

import folium
from folium import plugins
from staticmap import StaticMap, CircleMarker, Line
from PIL import Image, ImageDraw, ImageFont
import os
import json
import urllib.request
import polyline  # pip install polyline

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_osrm_route(coords_list):
    """Query OSRM for actual road route between a list of (lat, lon) coordinates.
    Returns a list of (lat, lon) tuples following real roads."""
    # OSRM expects lon,lat format
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in coords_list)
    url = f"https://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=polyline"

    print(f"  Fetching road route from OSRM ({len(coords_list)} waypoints)...")
    req = urllib.request.Request(url, headers={"User-Agent": "TripMapGenerator/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    if data["code"] != "Ok":
        print(f"  ⚠️ OSRM returned: {data['code']}. Falling back to straight lines.")
        return coords_list

    # Decode the polyline geometry into (lat, lon) pairs
    geometry = data["routes"][0]["geometry"]
    decoded = polyline.decode(geometry)  # returns list of (lat, lon)
    distance_km = data["routes"][0]["distance"] / 1000
    duration_hr = data["routes"][0]["duration"] / 3600
    print(f"  ✅ Got road route: {distance_km:.0f} km ({duration_hr:.1f} hr), {len(decoded)} points")
    return decoded

# ═══════════════════════════════════════════
# Stop data
# ═══════════════════════════════════════════

day1_stops = [
    {"name": "Pasadena — Departure", "lat": 34.1478, "lon": -118.1445, "time": "7:00 AM", "icon": "home", "color": "green",
     "desc": "Fill gas, grab coffee, take I-210 W → SR-134 W → US-101 N"},
    {"name": "Ventura", "lat": 34.2746, "lon": -119.2290, "time": "~8:30 AM", "icon": "tint", "color": "blue",
     "desc": "Ventura Pier & Promenade. First ocean views!"},
    {"name": "Santa Barbara", "lat": 34.4208, "lon": -119.6982, "time": "~9:30 AM", "icon": "star", "color": "blue",
     "desc": "Stearns Wharf, State Street. The 'American Riviera.'"},
    {"name": "Solvang", "lat": 34.5958, "lon": -120.1376, "time": "~10:30 AM", "icon": "home", "color": "blue",
     "desc": "Danish village! Æbleskiver pancakes, windmills."},
    {"name": "Pismo Beach — Lunch", "lat": 35.1428, "lon": -120.6413, "time": "~12:00 PM", "icon": "cutlery", "color": "orange",
     "desc": "Splash Café clam chowder! ⛽ Refuel here."},
    {"name": "Paso Robles", "lat": 35.6264, "lon": -120.6910, "time": "~1:45 PM", "icon": "glass", "color": "blue",
     "desc": "Wine country town square. Coffee & stretch."},
    {"name": "Gilroy", "lat": 37.0058, "lon": -121.5683, "time": "~4:15 PM", "icon": "shopping-cart", "color": "blue",
     "desc": "Garlic Capital! Gilroy Premium Outlets."},
    {"name": "3223 Kenneth St, Santa Clara", "lat": 37.3541, "lon": -121.9552, "time": "~5:30 PM", "icon": "briefcase", "color": "red",
     "desc": "Arrive at destination. Drop luggage at hotel."},
    {"name": "Stanford University", "lat": 37.4275, "lon": -122.1697, "time": "~5:45–7:00 PM", "icon": "graduation-cap", "color": "purple",
     "desc": "Palm Drive, Main Quad, Memorial Church at golden hour!"},
]

day2_stops = [
    {"name": "Business Meeting — Kenneth St", "lat": 37.3541, "lon": -121.9552, "time": "9:00–11:00 AM", "icon": "briefcase", "color": "darkred",
     "desc": "💼 2-hour business meeting. ⛽ Fill gas after."},
    {"name": "Depart Santa Clara", "lat": 37.3541, "lon": -121.9552, "time": "~11:15 AM", "icon": "play", "color": "pink",
     "desc": "Head to coast via CA-17 S → CA-1 S."},
    {"name": "Monterey / Cannery Row", "lat": 36.6177, "lon": -121.9010, "time": "~1:00 PM", "icon": "tint", "color": "pink",
     "desc": "Sea otters! ⛽ LAST GAS for 90 miles!"},
    {"name": "Bixby Bridge & Big Sur", "lat": 36.3714, "lon": -121.9020, "time": "~2:20 PM", "icon": "camera", "color": "pink",
     "desc": "714-ft bridge, 280 ft above crashing surf. Jaw-dropping!"},
    {"name": "San Simeon — Elephant Seals", "lat": 35.6625, "lon": -121.2561, "time": "~4:40 PM", "icon": "eye-open", "color": "pink",
     "desc": "FREE boardwalk over thousands of elephant seals!"},
    {"name": "Morro Bay — Dinner", "lat": 35.3659, "lon": -120.8498, "time": "~5:15 PM", "icon": "cutlery", "color": "orange",
     "desc": "Morro Rock! Seafood dinner. ⛽ Refuel after Big Sur."},
    {"name": "Pasadena — Home", "lat": 34.1478, "lon": -118.1445, "time": "~9:15–9:30 PM", "icon": "home", "color": "green",
     "desc": "Home sweet home! 🎉 ~215 mi via US-101 S."},
]

# OSRM will compute actual road routes from stop coordinates
# For Day 2, add waypoints to force the coastal CA-1 route through Big Sur
day2_routing_waypoints = [
    (37.3541, -121.9552),   # Santa Clara (departure)
    (36.9741, -122.0297),   # Santa Cruz (force CA-17 → CA-1)
    (36.6177, -121.9010),   # Monterey
    (36.3714, -121.9020),   # Bixby Bridge
    (36.0544, -121.5569),   # Lucia (Big Sur coast)
    (35.6625, -121.2561),   # San Simeon
    (35.3659, -120.8498),   # Morro Bay
    (34.1478, -118.1445),   # Pasadena
]


def create_folium_map(stops, route_coords, day_label, day_color, filename):
    """Create an interactive Folium HTML map with actual road routes."""
    # Center the map
    avg_lat = sum(s["lat"] for s in stops) / len(stops)
    avg_lon = sum(s["lon"] for s in stops) / len(stops)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7, tiles="OpenStreetMap")

    # Route line
    folium.PolyLine(
        locations=route_coords,
        weight=4,
        color="#1a73e8" if "1" in day_label else "#db2777",
        opacity=0.8,
    ).add_to(m)

    # Stop markers with popups
    for i, stop in enumerate(stops):
        popup_html = f"""
        <div style="font-family: -apple-system, sans-serif; min-width: 200px;">
            <h4 style="margin:0 0 4px; color: #1a202c;">{stop['name']}</h4>
            <p style="margin:0 0 4px; color: #64748b; font-size: 13px;"><b>{stop['time']}</b></p>
            <p style="margin:0; font-size: 13px; color: #475569;">{stop['desc']}</p>
        </div>
        """
        folium.Marker(
            location=[stop["lat"], stop["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{stop['time']} — {stop['name']}",
            icon=folium.Icon(color=stop["color"], icon=stop["icon"], prefix="glyphicon"),
        ).add_to(m)

    # Number markers
    for i, stop in enumerate(stops):
        folium.CircleMarker(
            location=[stop["lat"], stop["lon"]],
            radius=0,
        ).add_to(m)

    # Title
    title_html = f"""
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000;
         background: {'#1a73e8' if '1' in day_label else '#db2777'}; color: white;
         padding: 10px 24px; border-radius: 8px; font-family: -apple-system, sans-serif;
         font-size: 16px; font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
         white-space: nowrap;">
        🚙 {day_label}
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Legend
    legend_items = "".join(
        f'<div style="margin: 2px 0; font-size: 12px;"><b>{s["time"]}</b> — {s["name"]}</div>'
        for s in stops
    )
    legend_html = f"""
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000;
         background: white; padding: 12px 16px; border-radius: 8px;
         font-family: -apple-system, sans-serif; max-width: 300px;
         box-shadow: 0 2px 8px rgba(0,0,0,0.2); max-height: 50vh; overflow-y: auto;">
        <div style="font-weight:700; margin-bottom:6px; font-size:14px;">📍 Stops</div>
        {legend_items}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Fit bounds
    m.fit_bounds([[s["lat"], s["lon"]] for s in stops], padding=[40, 40])

    filepath = os.path.join(OUT_DIR, filename)
    m.save(filepath)
    print(f"✅ Saved interactive map: {filepath}")
    return filepath


def create_static_png(stops, route_coords, day_label, filename, width=1200, height=800):
    """Create a static PNG map image."""
    m = StaticMap(width, height, url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")

    # Draw route line
    line_color = "#1a73e8" if "1" in day_label else "#db2777"
    line_coords = [(lon, lat) for lat, lon in route_coords]
    m.add_line(Line(line_coords, line_color, 3))

    # Draw stop markers
    for stop in stops:
        marker_color = "#e53e3e" if stop["color"] in ("red", "darkred") else (
            "#38a169" if stop["color"] == "green" else (
                "#805ad5" if stop["color"] == "purple" else (
                    "#dd6b20" if stop["color"] == "orange" else "#3182ce"
                )
            )
        )
        m.add_marker(CircleMarker((stop["lon"], stop["lat"]), marker_color, 8))

    image = m.render()

    # Add title bar
    result = Image.new("RGB", (width, height + 60), "#1a202c")
    result.paste(image, (0, 60))

    draw = ImageDraw.Draw(result)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        font = ImageFont.load_default()
        font_small = font

    # Title background
    draw.rectangle([(0, 0), (width, 58)], fill="#1a73e8" if "1" in day_label else "#db2777")
    draw.text((width // 2, 18), f"🚙 {day_label}", fill="white", font=font, anchor="mt")
    draw.text((width // 2, 44), "2011 Jeep Wrangler Sahara · Click interactive HTML for details", fill="#ffffffcc", font=font_small, anchor="mt")

    filepath = os.path.join(OUT_DIR, filename)
    result.save(filepath, "PNG", quality=95)
    print(f"✅ Saved static map: {filepath}")
    return filepath


# ═══════════════════════════════════════════
# Generate all maps
# ═══════════════════════════════════════════

if __name__ == "__main__":
    # Get actual road routes from OSRM
    print("Fetching Day 1 road route (US-101)...")
    day1_waypoints = [(s["lat"], s["lon"]) for s in day1_stops]
    day1_road_route = get_osrm_route(day1_waypoints)

    print("\nFetching Day 2 road route (CA-1 PCH)...")
    day2_road_route = get_osrm_route(day2_routing_waypoints)

    print("\nGenerating interactive Folium maps...")
    create_folium_map(day1_stops, day1_road_route,
                      "Day 1 (Thu 4/9) — Pasadena → Santa Clara via US-101",
                      "#1a73e8", "day1_map.html")
    create_folium_map(day2_stops, day2_road_route,
                      "Day 2 (Fri 4/10) — Santa Clara → Pasadena via CA-1 PCH 🌊",
                      "#db2777", "day2_map.html")

    print("\nGenerating static PNG maps...")
    create_static_png(day1_stops, day1_road_route,
                      "Day 1 (Thu 4/9) — Pasadena → Santa Clara via US-101",
                      "day1_map.png")
    create_static_png(day2_stops, day2_road_route,
                      "Day 2 (Fri 4/10) — Santa Clara → Pasadena via CA-1 PCH",
                      "day2_map.png")

    print("\n🎉 All maps generated!")
    print("   Interactive: day1_map.html, day2_map.html (open directly in browser)")
    print("   Static:      day1_map.png,  day2_map.png  (share anywhere)")
