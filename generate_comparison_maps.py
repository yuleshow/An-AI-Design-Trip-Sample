#!/usr/bin/env python3
"""
Generate overlay maps: actual GPS route (from GPX) over the planned route (from OSRM).
Creates day1_comparison.html and day2_comparison.html.
"""

import folium
import xml.etree.ElementTree as ET
import os
import json
import urllib.request
import polyline

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
GPX_NS = "{http://www.topografix.com/GPX/1/1}"


# ── Planned waypoints (from generate_maps.py) ───────────────────────────────

day1_planned_waypoints = [
    (34.1478, -118.1445),   # Pasadena
    (34.2746, -119.2290),   # Ventura
    (34.4208, -119.6982),   # Santa Barbara
    (34.5958, -120.1376),   # Solvang
    (35.2828, -120.6596),   # San Luis Obispo
    (35.6264, -120.6910),   # Paso Robles
    (37.0058, -121.5683),   # Gilroy
    (37.4275, -122.1697),   # Stanford
    (37.3731, -121.9210),   # Hotel
]

day1_planned_stops = [
    {"name": "Pasadena — Departure",    "lat": 34.1478, "lon": -118.1445, "time": "7:00 AM"},
    {"name": "Ventura Pier",            "lat": 34.2746, "lon": -119.2290, "time": "~8:30 AM"},
    {"name": "Santa Barbara",           "lat": 34.4208, "lon": -119.6982, "time": "~9:30 AM"},
    {"name": "Solvang",                 "lat": 34.5958, "lon": -120.1376, "time": "~11:00 AM"},
    {"name": "San Luis Obispo",         "lat": 35.2828, "lon": -120.6596, "time": "~1:15 PM"},
    {"name": "Paso Robles",             "lat": 35.6264, "lon": -120.6910, "time": "~2:20 PM"},
    {"name": "Gilroy",                  "lat": 37.0058, "lon": -121.5683, "time": "~4:15 PM"},
    {"name": "Stanford University",     "lat": 37.4275, "lon": -122.1697, "time": "~5:45 PM"},
    {"name": "Hotel (Hyatt Place SJ)",  "lat": 37.3731, "lon": -121.9210, "time": "evening"},
]

day2_planned_waypoints = [
    (37.3541, -121.9552),   # Santa Clara
    (36.9741, -122.0297),   # Santa Cruz (routing waypoint)
    (36.6177, -121.9010),   # Monterey
    (36.5681, -121.9656),   # Lone Cypress
    (36.5554, -121.9233),   # Carmel
    (36.3714, -121.9020),   # Bixby Bridge
    (36.0544, -121.5569),   # Lucia
    (35.6625, -121.2561),   # San Simeon
    (35.5086, -121.0228),   # Harmony
    (35.3659, -120.8498),   # Morro Bay
    (34.1478, -118.1445),   # Pasadena
]

day2_planned_stops = [
    {"name": "Business Meeting",            "lat": 37.3541, "lon": -121.9552, "time": "9:00 AM"},
    {"name": "Monterey / Cannery Row",      "lat": 36.6177, "lon": -121.9010, "time": "~1:00 PM"},
    {"name": "17-Mile Drive / Lone Cypress", "lat": 36.5681, "lon": -121.9656, "time": "~1:45 PM"},
    {"name": "Carmel-by-the-Sea",           "lat": 36.5554, "lon": -121.9233, "time": "~2:30 PM"},
    {"name": "Bixby Creek Bridge",          "lat": 36.3714, "lon": -121.9020, "time": "~3:15 PM"},
    {"name": "Elephant Seal, San Simeon",   "lat": 35.6625, "lon": -121.2561, "time": "~5:30 PM"},
    {"name": "Harmony (pop. 18)",           "lat": 35.5086, "lon": -121.0228, "time": "~6:00 PM"},
    {"name": "Morro Bay (dinner)",          "lat": 35.3659, "lon": -120.8498, "time": "~6:20 PM"},
    {"name": "Pasadena — Home",             "lat": 34.1478, "lon": -118.1445, "time": "~10:30 PM"},
]


# ── OSRM routing ────────────────────────────────────────────────────────────

def get_osrm_route(waypoints):
    """Get road-following route from OSRM."""
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
    url = f"https://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=polyline"
    print(f"  Fetching planned route from OSRM ({len(waypoints)} waypoints)...")
    req = urllib.request.Request(url, headers={"User-Agent": "TripMapGenerator/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    if data["code"] != "Ok":
        print(f"  ⚠️ OSRM error: {data['code']}. Using straight lines.")
        return waypoints
    decoded = polyline.decode(data["routes"][0]["geometry"])
    dist_mi = data["routes"][0]["distance"] / 1609.34
    print(f"  ✅ Planned route: {dist_mi:.0f} miles, {len(decoded)} points")
    return decoded


# ── GPX parsing ──────────────────────────────────────────────────────────────

def parse_gpx(filepath):
    """Parse GPX file, return list of (lat, lon)."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    points = []
    for trk in root.findall(f"{GPX_NS}trk"):
        for seg in trk.findall(f"{GPX_NS}trkseg"):
            for pt in seg.findall(f"{GPX_NS}trkpt"):
                lat = float(pt.attrib["lat"])
                lon = float(pt.attrib["lon"])
                points.append((lat, lon))
    return points


def downsample(points, factor=5):
    """Keep every Nth point to reduce file size."""
    return points[::factor] + [points[-1]]


# ── Map creation ─────────────────────────────────────────────────────────────

def create_comparison_map(planned_route, planned_stops, actual_route, day_label, filename):
    """Create a Folium map with planned route (dashed) and actual route (solid) overlaid."""

    # Center on midpoint
    all_lats = [p[0] for p in planned_route + actual_route]
    all_lons = [p[1] for p in planned_route + actual_route]
    center_lat = (min(all_lats) + max(all_lats)) / 2
    center_lon = (min(all_lons) + max(all_lons)) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="OpenStreetMap")

    # Google Maps tile layers
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Maps",
    ).add_to(m)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
    ).add_to(m)

    # Planned route — dashed blue/pink
    plan_color = "#1a73e8" if "1" in day_label else "#db2777"
    folium.PolyLine(
        locations=planned_route,
        weight=4,
        color=plan_color,
        opacity=0.6,
        dash_array="10 8",
        tooltip="Planned route",
    ).add_to(m)

    # Actual route — solid orange/red
    folium.PolyLine(
        locations=actual_route,
        weight=3,
        color="#e65100",
        opacity=0.85,
        tooltip="Actual GPS track",
    ).add_to(m)

    # Planned stop markers (blue/pink circles)
    for stop in planned_stops:
        folium.CircleMarker(
            location=[stop["lat"], stop["lon"]],
            radius=7,
            color=plan_color,
            fill=True,
            fill_color=plan_color,
            fill_opacity=0.7,
            tooltip=f"📍 PLANNED: {stop['name']} ({stop['time']})",
            popup=f"<b>Planned:</b> {stop['name']}<br><b>Time:</b> {stop['time']}",
        ).add_to(m)

    # Legend
    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 12px 16px; border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: -apple-system, sans-serif;
                font-size: 13px; line-height: 1.6;">
        <b>{day_label}</b><br>
        <span style="color: {plan_color};">┅┅┅</span> Planned route<br>
        <span style="color: #e65100;">━━━</span> Actual GPS track<br>
        <span style="color: {plan_color};">●</span> Planned stop
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Layer switcher (top-right corner)
    folium.LayerControl(collapsed=False).add_to(m)

    out_path = os.path.join(OUT_DIR, filename)
    m.save(out_path)
    print(f"  💾 Saved {out_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    gpx_day1 = os.path.join(OUT_DIR, "gpx", "merged_20260409.gpx")
    gpx_day2 = os.path.join(OUT_DIR, "gpx", "merged_20260410.gpx")

    # Parse actual GPS tracks
    print("Parsing GPX tracks...")
    actual1 = downsample(parse_gpx(gpx_day1), factor=8)
    actual2 = downsample(parse_gpx(gpx_day2), factor=8)
    print(f"  Day 1: {len(actual1)} points (downsampled)")
    print(f"  Day 2: {len(actual2)} points (downsampled)")

    # Get planned routes from OSRM
    print("\nFetching planned routes...")
    planned1 = get_osrm_route(day1_planned_waypoints)
    planned2 = get_osrm_route(day2_planned_waypoints)

    # Generate maps
    print("\nGenerating comparison maps...")
    create_comparison_map(planned1, day1_planned_stops, actual1,
                          "Day 1: Pasadena → Santa Clara (US-101)",
                          "day1_comparison.html")
    create_comparison_map(planned2, day2_planned_stops, actual2,
                          "Day 2: Santa Clara → Pasadena (CA-1 PCH)",
                          "day2_comparison.html")

    print("\nDone! Open day1_comparison.html and day2_comparison.html in a browser.")


if __name__ == "__main__":
    main()
