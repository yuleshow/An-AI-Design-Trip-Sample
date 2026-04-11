#!/usr/bin/env python3
"""
Compare the actual GPS track (GPX files) against the original trip plan.

Parses GPX tracks from each day, detects stops where the vehicle was stationary,
matches them to planned stops, and generates a comparison report.
"""

import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

# ── Constants ────────────────────────────────────────────────────────────────

GPX_NS = "{http://www.topografix.com/GPX/1/1}"
STOP_SPEED_THRESHOLD_MPH = 3.0   # below this = stopped
MIN_STOP_DURATION_MIN = 3        # must be stopped at least this long to count
MATCH_RADIUS_MILES = 5.0         # how close actual stop must be to planned stop

PT = timezone(timedelta(hours=-7))  # Pacific Daylight Time (Apr 2026)


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class PlannedStop:
    name: str
    lat: float
    lon: float
    planned_time: str          # e.g. "7:00 AM", "~8:30 AM"
    day: int


@dataclass
class ActualStop:
    lat: float
    lon: float
    arrive: datetime
    depart: datetime
    duration_min: float


@dataclass
class TrackPoint:
    lat: float
    lon: float
    time: datetime
    ele: float


# ── Planned itinerary (from trip plan) ───────────────────────────────────────

PLANNED_STOPS = [
    # ── Day 1: Pasadena → Santa Clara via US-101 ──
    PlannedStop("Departure: Pasadena",        34.1539, -118.1083, "7:00 AM",   1),
    PlannedStop("Ventura Pier",               34.2741, -119.2645, "~8:30 AM",  1),
    PlannedStop("Stearns Wharf, Santa Barbara",34.4095,-119.6854, "~9:30 AM",  1),
    PlannedStop("Solvang Danish Village",     34.5957, -120.1376, "~11:00 AM", 1),
    PlannedStop("San Luis Obispo",            35.2828, -120.6596, "~1:15 PM",  1),
    PlannedStop("Paso Robles",                35.6266, -120.6910, "~2:20 PM",  1),
    PlannedStop("Gilroy",                     37.0072, -121.5684, "~4:15 PM",  1),
    PlannedStop("Stanford University",        37.4275, -122.1697, "~5:45 PM",  1),
    PlannedStop("Hyatt Place San Jose (hotel)",37.3730,-121.9210, "evening",   1),

    # ── Day 2: Santa Clara → Pasadena via CA-1 ──
    PlannedStop("Business meeting, Santa Clara",37.3735,-121.9188,"9:00 AM",   2),
    PlannedStop("Monterey / Cannery Row",     36.6161, -121.9012, "~1:00 PM",  2),
    PlannedStop("17-Mile Drive / Lone Cypress",36.5700,-121.9617, "~1:45 PM",  2),
    PlannedStop("Carmel-by-the-Sea",          36.5554, -121.9233, "~2:30 PM",  2),
    PlannedStop("Bixby Creek Bridge",         36.3714, -121.9020, "~3:15 PM",  2),
    PlannedStop("Elephant Seal, San Simeon",  35.6625, -121.2542, "~5:30 PM",  2),
    PlannedStop("Harmony (pop. 18)",          35.5086, -121.0228, "~6:00 PM",  2),
    PlannedStop("Morro Bay (dinner)",         35.3628, -120.8510, "~6:20 PM",  2),
    PlannedStop("Arrive Home: Pasadena",      34.1539, -118.1083, "~10:30 PM", 2),
]


# ── Geo helpers ──────────────────────────────────────────────────────────────

def haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in miles."""
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ── GPX parsing ──────────────────────────────────────────────────────────────

def parse_gpx(filepath: str) -> list[TrackPoint]:
    """Parse a GPX file and return a flat, time-sorted list of track points."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    points = []
    for trk in root.findall(f"{GPX_NS}trk"):
        for seg in trk.findall(f"{GPX_NS}trkseg"):
            for pt in seg.findall(f"{GPX_NS}trkpt"):
                lat = float(pt.attrib["lat"])
                lon = float(pt.attrib["lon"])
                time_str = pt.find(f"{GPX_NS}time").text
                ele_el = pt.find(f"{GPX_NS}ele")
                ele = float(ele_el.text) if ele_el is not None else 0.0
                # Parse ISO 8601 with UTC offset
                t = datetime.fromisoformat(time_str)
                points.append(TrackPoint(lat, lon, t, ele))
    points.sort(key=lambda p: p.time)
    return points


# ── Stop detection ───────────────────────────────────────────────────────────

def detect_stops(points: list[TrackPoint]) -> list[ActualStop]:
    """
    Detect stops: clusters of consecutive points where speed < threshold.
    Returns list of ActualStop with arrive/depart times and center location.
    """
    if len(points) < 2:
        return []

    stops: list[ActualStop] = []
    stop_start = None      # index where current stop began
    stop_points = []       # points in current stop cluster

    for i in range(1, len(points)):
        dt = (points[i].time - points[i - 1].time).total_seconds()
        if dt <= 0:
            continue
        dist = haversine_miles(points[i - 1].lat, points[i - 1].lon,
                               points[i].lat, points[i].lon)
        speed_mph = (dist / dt) * 3600

        if speed_mph < STOP_SPEED_THRESHOLD_MPH:
            if stop_start is None:
                stop_start = i - 1
                stop_points = [points[i - 1]]
            stop_points.append(points[i])
        else:
            if stop_start is not None and stop_points:
                _maybe_add_stop(stop_points, stops)
            stop_start = None
            stop_points = []

    # flush final stop
    if stop_start is not None and stop_points:
        _maybe_add_stop(stop_points, stops)

    return stops


def _maybe_add_stop(pts: list[TrackPoint], stops: list[ActualStop]):
    duration = (pts[-1].time - pts[0].time).total_seconds() / 60
    if duration >= MIN_STOP_DURATION_MIN:
        avg_lat = sum(p.lat for p in pts) / len(pts)
        avg_lon = sum(p.lon for p in pts) / len(pts)
        stops.append(ActualStop(avg_lat, avg_lon, pts[0].time, pts[-1].time, round(duration, 1)))


# ── Merge nearby stops ───────────────────────────────────────────────────────

def merge_nearby_stops(stops: list[ActualStop], merge_radius_mi=0.3, gap_min=10) -> list[ActualStop]:
    """Merge stops that are close together and have a small gap between them."""
    if not stops:
        return []
    merged = [stops[0]]
    for s in stops[1:]:
        prev = merged[-1]
        dist = haversine_miles(prev.lat, prev.lon, s.lat, s.lon)
        gap = (s.arrive - prev.depart).total_seconds() / 60
        if dist < merge_radius_mi and gap < gap_min:
            # Merge: extend previous stop
            all_dur = (s.depart - prev.arrive).total_seconds() / 60
            avg_lat = (prev.lat + s.lat) / 2
            avg_lon = (prev.lon + s.lon) / 2
            merged[-1] = ActualStop(avg_lat, avg_lon, prev.arrive, s.depart, round(all_dur, 1))
        else:
            merged.append(s)
    return merged


# ── Matching & comparison ────────────────────────────────────────────────────

def match_stops(actual: list[ActualStop], planned: list[PlannedStop]):
    """Match each actual stop to the nearest planned stop within radius."""
    results = []
    used_planned = set()

    for a in actual:
        best = None
        best_dist = float("inf")
        for i, p in enumerate(planned):
            if i in used_planned:
                continue
            d = haversine_miles(a.lat, a.lon, p.lat, p.lon)
            if d < best_dist:
                best_dist = d
                best = (i, p)
        if best and best_dist <= MATCH_RADIUS_MILES:
            used_planned.add(best[0])
            results.append((a, best[1], round(best_dist, 2)))
        else:
            results.append((a, None, round(best_dist, 2) if best else None))

    # Planned stops that had no actual match
    missed = [(i, p) for i, p in enumerate(planned) if i not in used_planned]
    return results, missed


# ── Track stats ──────────────────────────────────────────────────────────────

def compute_track_stats(points: list[TrackPoint]):
    """Compute total distance, moving time, etc."""
    total_dist = 0.0
    moving_time_s = 0.0
    max_speed = 0.0
    max_ele = -9999
    min_ele = 9999

    for i in range(1, len(points)):
        d = haversine_miles(points[i - 1].lat, points[i - 1].lon,
                            points[i].lat, points[i].lon)
        dt = (points[i].time - points[i - 1].time).total_seconds()
        total_dist += d
        if dt > 0:
            speed = (d / dt) * 3600
            if speed > STOP_SPEED_THRESHOLD_MPH:
                moving_time_s += dt
            if speed < 120:  # ignore GPS glitches
                max_speed = max(max_speed, speed)
        max_ele = max(max_ele, points[i].ele)
        min_ele = min(min_ele, points[i].ele)

    elapsed = (points[-1].time - points[0].time).total_seconds()
    return {
        "total_distance_mi": round(total_dist, 1),
        "elapsed_time_hr": round(elapsed / 3600, 1),
        "moving_time_hr": round(moving_time_s / 3600, 1),
        "max_speed_mph": round(max_speed, 1),
        "max_elevation_ft": round(max_ele * 3.28084),
        "min_elevation_ft": round(min_ele * 3.28084),
        "start_time": points[0].time.strftime("%-I:%M %p"),
        "end_time": points[-1].time.strftime("%-I:%M %p"),
    }


# ── Reporting ────────────────────────────────────────────────────────────────

def fmt_time(dt: datetime) -> str:
    return dt.strftime("%-I:%M %p")


def print_day_report(day_num, points, planned_day_stops):
    stats = compute_track_stats(points)
    raw_stops = detect_stops(points)
    stops = merge_nearby_stops(raw_stops)

    matched, missed = match_stops(stops, planned_day_stops)

    print(f"\n{'='*72}")
    print(f" DAY {day_num} — ACTUAL vs PLANNED")
    print(f"{'='*72}")
    print(f"\n📊 Track Statistics:")
    print(f"   Total distance:   {stats['total_distance_mi']} miles")
    print(f"   Elapsed time:     {stats['elapsed_time_hr']} hr  ({stats['start_time']} → {stats['end_time']})")
    print(f"   Moving time:      {stats['moving_time_hr']} hr")
    print(f"   Stopped time:     {round(stats['elapsed_time_hr'] - stats['moving_time_hr'], 1)} hr")
    print(f"   Max speed:        {stats['max_speed_mph']} mph")
    print(f"   Elevation range:  {stats['min_elevation_ft']} ft → {stats['max_elevation_ft']} ft")
    print(f"   Stops detected:   {len(stops)}")

    print(f"\n{'─'*72}")
    print(f" STOP COMPARISON")
    print(f"{'─'*72}")
    print(f"{'Actual Time':<22} {'Duration':>8}  {'Planned Stop':<30} {'Planned Time':<14} {'Dist'}")
    print(f"{'─'*22} {'─'*8}  {'─'*30} {'─'*14} {'─'*8}")

    for actual, planned, dist in matched:
        time_str = f"{fmt_time(actual.arrive)} – {fmt_time(actual.depart)}"
        dur_str = f"{actual.duration_min:.0f} min"
        if planned:
            p_name = planned.name[:30]
            p_time = planned.planned_time
            dist_str = f"{dist} mi"
        else:
            p_name = "(unplanned stop)"
            p_time = "—"
            dist_str = f"{dist} mi" if dist else "—"
        print(f"{time_str:<22} {dur_str:>8}  {p_name:<30} {p_time:<14} {dist_str}")

    if missed:
        print(f"\n⚠  Planned stops NOT matched to any actual stop:")
        for _, p in missed:
            print(f"   • {p.name}  (planned {p.planned_time})")

    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    import os
    base = os.path.dirname(os.path.abspath(__file__))

    gpx_day1 = os.path.join(base, "gpx", "merged_20260409.gpx")
    gpx_day2 = os.path.join(base, "gpx", "merged_20260410.gpx")

    print("Parsing GPX tracks...")
    pts1 = parse_gpx(gpx_day1)
    pts2 = parse_gpx(gpx_day2)
    print(f"  Day 1: {len(pts1):,} track points")
    print(f"  Day 2: {len(pts2):,} track points")

    day1_planned = [s for s in PLANNED_STOPS if s.day == 1]
    day2_planned = [s for s in PLANNED_STOPS if s.day == 2]

    print_day_report(1, pts1, day1_planned)
    print_day_report(2, pts2, day2_planned)

    # ── Overall summary ──
    stats1 = compute_track_stats(pts1)
    stats2 = compute_track_stats(pts2)
    total_mi = stats1["total_distance_mi"] + stats2["total_distance_mi"]
    total_hr = stats1["elapsed_time_hr"] + stats2["elapsed_time_hr"]
    print(f"{'='*72}")
    print(f" TRIP TOTALS")
    print(f"{'='*72}")
    print(f"   Total distance:  {total_mi} miles  (plan: ~770 miles)")
    print(f"   Total time:      {total_hr} hr")
    print()


if __name__ == "__main__":
    main()
