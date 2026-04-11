# Post-Trip Report: Pasadena ↔ Santa Clara (Apr 9–10, 2026)

## Trip Completed

The trip was completed as planned — Pasadena to Santa Clara on Thursday April 9 via US-101, and back on Friday April 10 via CA-1 Pacific Coast Highway. GPS tracks were recorded for both days using a CardputerADV device.

## Actual vs Planned Summary

| Metric | Planned | Actual | Delta |
|---|---|---|---|
| **Total distance** | ~770 miles | 871 miles | +101 miles (+13%) |
| **Day 1 distance** | ~370 miles | 451 miles | +81 miles |
| **Day 2 distance** | ~400 miles | 419 miles | +19 miles |
| **Day 1 departure** | 7:00 AM | 6:45 AM | 15 min early |
| **Day 1 arrival (hotel)** | evening | 8:12 PM | — |
| **Day 2 departure** | ~11:15 AM | ~1:29 PM | ~2 hr late |
| **Day 2 arrival home** | ~10:30 PM | ~12:32 AM (+1) | ~2 hr late |
| **Day 1 stops** | 7 planned | 9 actual (7 matched + 2 unplanned) | — |
| **Day 2 stops** | 8 planned | 15 actual (5 matched + 10 unplanned) | — |

### Day 1 — Stops Matched

All 7 planned Day 1 stops were visited:

| Planned Stop | Planned Time | Actual Time | Duration | Distance Off |
|---|---|---|---|---|
| Departure: Pasadena | 7:00 AM | 6:45 AM | 16 min | 0.15 mi |
| Ventura Pier | ~8:30 AM | 8:28 AM | 31 min | 1.44 mi |
| Stearns Wharf, Santa Barbara | ~9:30 AM | 9:36 AM | 23 min | 0.05 mi |
| Solvang Danish Village | ~11:00 AM | 10:47 AM | 53 min | 0.11 mi |
| San Luis Obispo | ~1:15 PM | 12:47 PM | 55 min | 0.26 mi |
| Paso Robles | ~2:20 PM | 2:22 PM | 6 min | 0.09 mi |
| Gilroy | ~4:15 PM | 4:30 PM | 26 min | 0.08 mi |
| Stanford University | ~5:45 PM | 5:57 PM | 39 min | 0.16 mi |
| Hyatt Place San Jose (hotel) | evening | 7:25 PM | 48 min | 0.02 mi |

### Day 2 — Stops Matched

5 of 8 planned Day 2 stops were visited. 2 were skipped due to running late:

| Planned Stop | Planned Time | Actual Time | Duration | Status |
|---|---|---|---|---|
| Business meeting, Santa Clara | 9:00 AM | 8:49 AM – 1:29 PM | 260 min | ✅ (ran long) |
| Monterey / Cannery Row | ~1:00 PM | 3:07 PM | 10 min | ✅ |
| 17-Mile Drive / Lone Cypress | ~1:45 PM | 3:30 PM | 3 min | ✅ (drive-through) |
| Carmel-by-the-Sea | ~2:30 PM | 3:35 PM | 4 min | ✅ (drive-through) |
| Bixby Creek Bridge | ~3:15 PM | 5:01 PM | 9 min | ✅ |
| Elephant Seal, San Simeon | ~5:30 PM | 7:19 PM | 4 min | ✅ |
| Harmony (pop. 18) | ~6:00 PM | — | — | ❌ Skipped |
| Morro Bay (dinner) | ~6:20 PM | — | — | ❌ Skipped |
| Arrive Home: Pasadena | ~10:30 PM | ~12:32 AM | — | 2 hr late |

### Key Deviations

1. **Day 2 departed 2+ hours late** — The business meeting / morning activities ran from 8:49 AM to 1:29 PM (260 min), far beyond the planned 9–11 AM window. This cascaded into every subsequent stop running late.

2. **Harmony and Morro Bay were skipped** — Running ~2 hours behind schedule with sunset approaching, these two stops were cut to get home at a reasonable hour.

3. **Day 2 had many short unplanned stops** — Big Sur's winding roads and photo-worthy scenery led to ~10 brief pullover stops not in the plan.

4. **Total distance was 101 miles more than planned** — See "Day 1 Mileage Discrepancy" below for a detailed breakdown.

---

## Known Issue #1: Day 1 Mileage Discrepancy (+81 miles)

The plan stated Day 1 was **~370 miles**. The GPS recorded **451 miles** — 81 miles more. Here's why:

### Segment Breakdown

| Segment | Plan | Actual (GPS) | Delta |
|---|---|---|---|
| Pasadena → Ventura | 70 mi | 81.8 mi | +11.8 mi |
| Ventura → Santa Barbara | 30 mi | 33.8 mi | +3.8 mi |
| Santa Barbara → Solvang | 35 mi | 34.1 mi | -0.9 mi |
| Solvang → San Luis Obispo | 75 mi | 66.7 mi | -8.3 mi |
| SLO → Paso Robles | 30 mi | 30.8 mi | +0.8 mi |
| Paso Robles → Gilroy | 100 mi | 126.0 mi | +26.0 mi |
| Gilroy → Stanford | 40 mi | 52.7 mi | +12.7 mi |
| Stanford → Hotel | **(not listed)** | 25.5 mi | +25.5 mi |
| Evening outing from hotel | — | 5.6 mi | +5.6 mi |
| **Total** | **380 mi** | **451.3 mi** | **+71.3 mi** |

### Root Cause: Stanford Was Added Without Recalculating

The original plan had Gilroy as the last stop before the hotel, totaling ~370 miles. When Stanford University was added later in the conversation, the AI:

1. **Inserted "40 miles from Gilroy" for the Gilroy → Stanford segment** but never added a driving segment from Stanford to the hotel — the plan just says "Evening — Dinner & Hotel" as if the hotel is walking distance from Stanford.
2. **Never updated the "~370 miles" headline number.** The listed segments alone already sum to 380 mi (without Stanford → Hotel), and the true total should have been ~406 miles.

Stanford is in **Palo Alto**, 20+ miles northwest of the Hyatt Place San Jose Airport. The AI treated "Stanford + Dinner + Hotel" as one location, when they're in entirely different cities. Every other stop in the plan has a "Drive: ~X miles from [previous stop]" header — the hotel section is the only one missing it.

This is an **incremental edit failure**: the AI correctly added a new stop but failed to propagate the change to the total distance, the segment structure, and the evening logistics.

### Corrected Distance vs Actual

After accounting for the AI's missing Stanford → Hotel segment, the **real** extra miles were:

| | Miles |
|---|---|
| Plan's listed segments (Pasadena → Stanford) | 380 mi |
| Missing: Stanford → Hotel | +26 mi |
| **Corrected plan total** | **~406 mi** |
| **Actual GPS total** | **~451 mi** |
| **Real extra miles beyond the planned route** | **~45 mi** |

Of the ~81 miles difference between "plan says 370" and "GPS says 451":
- **~36 miles** were the AI's own math errors (not counting Stanford → Hotel, rounding headline to 370)
- **~45 miles** were real extra miles on the road

Those ~45 real extra miles break down as:

- **~26 mi — AI underestimated road distances.** The plan used round numbers instead of actual road distances. The route was followed as planned, but the roads were simply longer than the AI said. Examples: Paso Robles → Gilroy listed as 100 mi, actually ~126 mi on US-101 through the Salinas Valley. Pasadena → Ventura listed as 70 mi, actually ~82 mi on I-210/US-101. These are not detours — the plan's mileage figures were just wrong.
- **~12 mi — Local driving at stops.** Exiting the freeway, driving through towns to find parking, and returning to the highway at each of the 7 stops.
- **~6 mi — Evening outing from hotel** (8:15–9:13 PM, 1.6 mi away — likely dinner).

---

## Known Issue #2: Hallucinated Hotel Address

The AI-generated trip plan listed the hotel address as:

> **1471 N 4th St, San Jose, CA 95112**

The actual address of the Hyatt Place San Jose Airport is:

> **82 Karina Court, San Jose, CA 95131**

These are **1.8 miles apart**. The wrong address is near Japantown in San Jose; the real hotel is off I-880 near the airport.

### Why This Happened

The trip plan was generated entirely by an AI assistant (GitHub Copilot / Claude) through conversational prompts (see [chat_history.txt](chat_history.txt)). The AI correctly identified the hotel **name** (Hyatt Place San Jose Airport), **price** ($168.98), **rating** (4.2★), and **amenities** — but **fabricated the street address**.

This is a well-documented failure mode of large language models known as **hallucination**: the model generates plausible-sounding details (a real-looking San Jose street address) that are factually incorrect. The AI had no mechanism to verify the address against a live database — it produced a confident-looking but wrong answer.

### Lesson Learned

> **Always independently verify specific factual details generated by AI** — especially addresses, phone numbers, hours of operation, and prices. AI is good at planning, structuring, and reasoning, but it can silently fabricate precise facts. Cross-check with Google Maps, the hotel's website, or your booking confirmation before relying on AI-generated addresses for navigation.

In this case, the GPS tracker recorded the real coordinates (37.3731, -121.9210), which reverse-geocode to the correct address at 82 Karina Court.

---

## Fuel Analysis

### Fill-ups

| # | Date | Station | Cost | Gallons | $/gal |
|---|---|---|---|---|---|
| 1 | Apr 9 | Chevron, 475 Allen Ave, Pasadena | $32.32 | 5.213 | $6.20 |
| 2 | Apr 9 | Mission Chevron, 328 Marsh St, SLO | $74.33 | 11.096 | $6.70 |
| 3 | Apr 10 | 76 Gas, 2101 N First St, San Jose | $83.30 | 12.857 | $6.48 |
| 4 | Apr 10 | Mini Mart, 19019 CA-1, Ragged Point | $50.00 | 6.098 | $8.20 |
| 5 | Apr 10 | Chevron, 225 Hampshire Rd, Thousand Oaks | $84.27 | 14.286 | $5.90 |
| | | **Total** | **$324.22** | **49.550** | **$6.54 avg** |

### Plan vs Actual

| Metric | Plan | Actual | Delta |
|---|---|---|---|
| Total fuel | ~45 gallons | 49.6 gallons | +4.6 gal |
| Total cost | ~$255–$270 | $324.22 | +$54 over high estimate |
| Average price | $5.70–$6.00/gal | $6.54/gal | +$0.54–$0.84/gal |
| Overall MPG | 17 combined / 19 hwy | 17.6 mpg | On target |

The cost overrun came from two factors: more miles driven (871 vs 770) and higher gas prices than the plan assumed.

### Fuel Strategy: Plan vs Reality

| Plan said | What happened |
|---|---|
| Fill in Pasadena before departure | ✅ Filled at Chevron, Allen Ave |
| Refuel at San Luis Obispo (Day 1) | ✅ Filled at Mission Chevron, Marsh St |
| Fill in Santa Clara before Day 2 | ✅ Filled at 76 Gas, N First St, San Jose |
| Fill in Monterey (last gas before Big Sur) | ❌ Skipped — filled at Ragged Point instead |
| Fill in San Simeon/Cambria or Morro Bay | ❌ Skipped — filled at Thousand Oaks |
| (no stop planned on homeward stretch) | ➕ Added Thousand Oaks fill-up |

### Big Sur Gas Premium

The plan warned: *"NO gas stations for ~90 miles through Big Sur."* There is in fact a station at **Ragged Point** on CA-1, but at **$8.20/gal** — a 32% premium over the $6.20 paid in Pasadena. Skipping the planned Monterey fill-up cost an extra ~$12 on the 6-gallon Ragged Point fill.

---

## Files

| File | Description |
|---|---|
| [compare_trip.py](compare_trip.py) | GPX parser — detects stops and compares actual vs. planned |
| [gpx/merged_20260409.gpx](gpx/merged_20260409.gpx) | Day 1 GPS track (14,408 points) |
| [gpx/merged_20260410.gpx](gpx/merged_20260410.gpx) | Day 2 GPS track (15,147 points) |

### Run the comparison

```bash
python3 compare_trip.py
```
