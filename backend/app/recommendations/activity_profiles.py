"""
Activity profiles and constraints for Fieldwise Outdoor Intelligence.
All 10 hackathon-mandated outdoor activities + supplemental outdoor pursuits.
"""

from typing import Dict, Any

ACTIVITY_PROFILES: Dict[str, Dict[str, Any]] = {
    # 1. Running or jogging (Hackathon Mandatory)
    "running": {
        "id": "running",
        "label": "Running or Jogging",
        "icon": "Footprints",
        "category": "Cardio & Fitness",
        "description": "Road, track, or park jogging requiring optimal aerobic air quality and comfortable thermal range.",
        "osm_filters": [
            '["leisure"="park"]',
            '["leisure"="track"]',
            '["leisure"="recreation_ground"]',
            '["leisure"="garden"]',
            '["highway"="pedestrian"]',
            '["highway"="footway"]'
        ],
        "ideal_temp": (12, 24),
        "max_temp": 32,
        "min_temp": 4,
        "max_aqi": 110,
        "max_wind_kmh": 28,
        "max_rain_prob": 35,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Breathable moisture-wicking running apparel",
            "500ml handheld hydration flask with electrolytes",
            "Reflective clip-on strobe or band for dawn/dusk safety",
            "Cushioned road or trail running shoes"
        ],
        "watch_note": "High respiration rate increases pollutant intake. Avoid arterial roadways during morning and evening rush hours when exhaust concentrates."
    },

    # 2. Cycling (leisure or commute) (Hackathon Mandatory)
    "cycling": {
        "id": "cycling",
        "label": "Cycling (Leisure or Commute)",
        "icon": "Bike",
        "category": "Wheels & Transit",
        "description": "Road cycling, urban commuting, or paved bike trail riding sensitive to head/crosswinds and surface slickness.",
        "osm_filters": [
            '["highway"="cycleway"]',
            '["leisure"="park"]',
            '["leisure"="recreation_ground"]',
            '["route"="bicycle"]',
            '["highway"="tertiary"]'
        ],
        "ideal_temp": (14, 27),
        "max_temp": 34,
        "min_temp": 6,
        "max_aqi": 105,
        "max_wind_kmh": 24,
        "max_rain_prob": 25,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Certified cycling helmet (CPSC/CE approved)",
            "Front high-lumen white light & rear pulsating red beacon",
            "750ml insulated frame cage water bottle",
            "Wraparound polarized UV cycling eyewear",
            "Compact mini-pump and inner tube patch kit"
        ],
        "watch_note": "Crosswinds above 20 km/h cause instability on open bridges and expressways. Wet pavement sharply increases braking distance."
    },

    # 3. Golf (Hackathon Mandatory)
    "golf": {
        "id": "golf",
        "label": "Golf",
        "icon": "Flag",
        "category": "Club & Target Sports",
        "description": "Multi-hour outdoor rounds on links and parkland courses requiring sustained daylight, low wind for ball flight, and mild temperatures.",
        "osm_filters": [
            '["leisure"="golf_course"]',
            '["golf"="driving_range"]',
            '["sport"="golf"]',
            '["leisure"="sports_centre"]'
        ],
        "ideal_temp": (15, 29),
        "max_temp": 35,
        "min_temp": 8,
        "max_aqi": 140,
        "max_wind_kmh": 20,
        "max_rain_prob": 20,
        "needs_daylight": True,
        "golden_hour_bonus": False,
        "carry": [
            "Broad-spectrum SPF 50+ sweat-resistant sunscreen",
            "Wide-brim golf cap or visor",
            "Windproof golf umbrella",
            "1L electrolyte water",
            "Cabretta leather golf glove & dry microfiber grip towel"
        ],
        "watch_note": "Golf rounds take 3-4 hours; solar UV accumulation and crosswind gust shifts represent the primary course hazards."
    },

    # 4. Recreational Cricket (Hackathon Mandatory)
    "cricket": {
        "id": "cricket",
        "label": "Cricket (Match & Practice)",
        "icon": "Trophy",
        "category": "Team Sports",
        "description": "Pitch turf play requiring dry turf conditions, reliable daylight visibility, and moderate wind.",
        "osm_filters": [
            '["sport"="cricket"]',
            '["leisure"="pitch"]',
            '["leisure"="stadium"]',
            '["leisure"="sports_centre"]',
            '["leisure"="park"]'
        ],
        "ideal_temp": (16, 30),
        "max_temp": 35,
        "min_temp": 10,
        "max_aqi": 130,
        "max_wind_kmh": 26,
        "max_rain_prob": 20,
        "needs_daylight": True,
        "golden_hour_bonus": False,
        "carry": [
            "Full cricket protective kit (pads, helmet, gloves, abdominal guard)",
            "Wide-brim white sun hat and UV sports sunglasses",
            "1.5L chilled electrolyte hydration per player",
            "First aid ice pack and muscle cramp spray"
        ],
        "watch_note": "Wet outfields soften the pitch, cause leather ball slippage, and increase bowler ankle sprain risks. Rain probability over 20% should delay start."
    },

    # 5. Outdoor Football or Five-a-side (Hackathon Mandatory)
    "football": {
        "id": "football",
        "label": "Outdoor Football (5-a-side / Turf)",
        "icon": "CircleDot",
        "category": "Team Sports",
        "description": "High-intensity agility play on grass pitches or turf arenas sensitive to heat exhaustion and slick turf.",
        "osm_filters": [
            '["sport"="soccer"]',
            '["leisure"="pitch"]',
            '["leisure"="sports_centre"]',
            '["leisure"="stadium"]'
        ],
        "ideal_temp": (14, 28),
        "max_temp": 33,
        "min_temp": 5,
        "max_aqi": 125,
        "max_wind_kmh": 30,
        "max_rain_prob": 30,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Molded firm-ground or turf studs with ankle support",
            "Shin guards and compression socks",
            "1L isotonic hydration drink",
            "Microfiber sweat towel and post-match dry jersey"
        ],
        "watch_note": "Sustained high anaerobic effort in AQI > 120 triggers throat irritation. Ensure frequent hydration breaks during sunny midday games."
    },

    # 6. Outdoor Tennis (Hackathon Mandatory)
    "tennis": {
        "id": "tennis",
        "label": "Outdoor Tennis",
        "icon": "Activity",
        "category": "Racket Sports",
        "description": "Hard, clay, or synthetic court games severely disrupted by wind drift, court dampness, and glare.",
        "osm_filters": [
            '["sport"="tennis"]',
            '["leisure"="pitch"]',
            '["leisure"="sports_centre"]',
            '["leisure"="stadium"]'
        ],
        "ideal_temp": (15, 29),
        "max_temp": 34,
        "min_temp": 8,
        "max_aqi": 125,
        "max_wind_kmh": 18,
        "max_rain_prob": 15,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Non-marking hard-court or clay tennis shoes",
            "Wrist sweatbands and spare tack overgrips",
            "Sports visor or polarized UV eyewear",
            "1L electrolyte water and court towel"
        ],
        "watch_note": "Wind speeds above 18 km/h noticeably alter tennis ball aerodynamics. Wet courts create acute slipping hazards."
    },

    # 7. Hiking or Nature Walks (Hackathon Mandatory)
    "hiking": {
        "id": "hiking",
        "label": "Hiking & Nature Walks",
        "icon": "Mountain",
        "category": "Trails & Wilderness",
        "description": "Trail navigation through reserves, ridgelines, and forest trails requiring daylight, safe footing, and rain preparedness.",
        "osm_filters": [
            '["route"="hiking"]',
            '["highway"="path"]',
            '["natural"="peak"]',
            '["leisure"="nature_reserve"]',
            '["leisure"="park"]'
        ],
        "ideal_temp": (12, 26),
        "max_temp": 31,
        "min_temp": 4,
        "max_aqi": 110,
        "max_wind_kmh": 28,
        "max_rain_prob": 25,
        "needs_daylight": True,
        "golden_hour_bonus": False,
        "carry": [
            "Deep-lugged trail shoes with rigid ankle support",
            "1.5L water & energy-dense trail snacks (nuts, dates)",
            "DEET insect repellent & mini first-aid kit",
            "Downloaded offline OSM trail map and charged power bank",
            "Lightweight breathable rain shell jacket"
        ],
        "watch_note": "Trails become muddy and slippery after rain; plan to complete hikes at least 60 minutes prior to sunset to prevent disorientation."
    },

    # 8. Picnics or Park Outings (Hackathon Mandatory)
    "picnic": {
        "id": "picnic",
        "label": "Picnic & Park Outing",
        "icon": "Coffee",
        "category": "Leisure & Social",
        "description": "Relaxed gatherings on park grass or designated picnic zones requiring shaded tree canopies and calm breezes.",
        "osm_filters": [
            '["leisure"="park"]',
            '["leisure"="garden"]',
            '["tourism"="picnic_site"]',
            '["leisure"="nature_reserve"]'
        ],
        "ideal_temp": (18, 29),
        "max_temp": 33,
        "min_temp": 12,
        "max_aqi": 120,
        "max_wind_kmh": 20,
        "max_rain_prob": 20,
        "needs_daylight": True,
        "golden_hour_bonus": False,
        "carry": [
            "Waterproof-backed picnic blanket or ground sheet",
            "Insulated cooler tote with chilled refreshments",
            "Sun hat, mineral sunscreen, and insect repellent wipes",
            "Biodegradable trash bag for leave-no-trace cleanup"
        ],
        "watch_note": "Check canopy shade density; avoid unshaded open lawns between 12:00 PM and 3:30 PM in summer months."
    },

    # 9. Outdoor Events or Gatherings (Hackathon Mandatory)
    "event": {
        "id": "event",
        "label": "Outdoor Event & Gathering",
        "icon": "Users",
        "category": "Leisure & Social",
        "description": "Fairs, campus gatherings, outdoor celebrations, or community functions requiring stable weather and accessible grounds.",
        "osm_filters": [
            '["leisure"="park"]',
            '["leisure"="garden"]',
            '["leisure"="recreation_ground"]',
            '["amenity"="community_centre"]'
        ],
        "ideal_temp": (18, 30),
        "max_temp": 33,
        "min_temp": 12,
        "max_aqi": 120,
        "max_wind_kmh": 20,
        "max_rain_prob": 15,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Weighted canopy or gazebo shade tents with ground tie-downs",
            "Dedicated covered hydration stations with dispenser water",
            "Citronella mosquito coils or battery diffusers for dusk",
            "Backup waterproof tarps for sound and catering equipment"
        ],
        "watch_note": "Sudden squalls or rain bursts can damage outdoor audiovisual equipment and tents. Ensure an indoor backup space is accessible."
    },

    # 10. Outdoor Photography (Hackathon Mandatory)
    "photography": {
        "id": "photography",
        "label": "Outdoor Photography & Sunset",
        "icon": "Camera",
        "category": "Creative & Observation",
        "description": "Scenic landscape, architectural, or golden-hour portrait sessions prioritizing clear visibility, unique lighting, and low wind.",
        "osm_filters": [
            '["tourism"="viewpoint"]',
            '["leisure"="park"]',
            '["natural"="water"]',
            '["tourism"="attraction"]'
        ],
        "ideal_temp": (10, 32),
        "max_temp": 36,
        "min_temp": 2,
        "max_aqi": 140,
        "max_wind_kmh": 26,
        "max_rain_prob": 25,
        "needs_daylight": True,
        "golden_hour_bonus": True,
        "carry": [
            "Microfiber optical lens cloths and silicone rocket blower",
            "Circular polarizing (CPL) and neutral density (ND) filters",
            "Weather-sealed camera backpack with integrated rain fly",
            "Sturdy carbon-fiber travel tripod for dusk / long exposures"
        ],
        "watch_note": "Golden hour occurs ~45 minutes before sunset; haze and PM2.5 soften direct sunlight into dramatic warm tones but reduce distant horizon clarity."
    },

    # 11. Swimming (Supplemental)
    "swimming": {
        "id": "swimming",
        "label": "Outdoor Swimming & Aquatic Sports",
        "icon": "Waves",
        "category": "Water & Aquatics",
        "description": "Outdoor pools, lidos, and managed lakes requiring warm air and water temperatures and zero lightning risk.",
        "osm_filters": [
            '["leisure"="swimming_pool"]',
            '["sport"="swimming"]',
            '["leisure"="sports_centre"]',
            '["amenity"="public_bath"]',
            '["natural"="water"]'
        ],
        "ideal_temp": (24, 34),
        "max_temp": 38,
        "min_temp": 20,
        "max_aqi": 130,
        "max_wind_kmh": 22,
        "max_rain_prob": 15,
        "needs_daylight": True,
        "golden_hour_bonus": False,
        "carry": [
            "UV-protective swimwear and anti-fog swimming goggles",
            "Silicone swim cap and earplugs",
            "Water-resistant broad-spectrum sunscreen (SPF 50+)",
            "Absorbent microfiber quick-dry towel",
            "Insulated cold hydration flask"
        ],
        "watch_note": "Never swim outdoors during convective storm/thundercloud activity; water is an electrical conductor."
    },

    # 12. Badminton (Supplemental)
    "badminton": {
        "id": "badminton",
        "label": "Outdoor Badminton",
        "icon": "Wind",
        "category": "Racket Sports",
        "description": "Outdoor shuttlecock play exceptionally sensitive to breeze and air currents.",
        "osm_filters": [
            '["sport"="badminton"]',
            '["leisure"="pitch"]',
            '["leisure"="sports_centre"]',
            '["leisure"="park"]'
        ],
        "ideal_temp": (16, 29),
        "max_temp": 33,
        "min_temp": 10,
        "max_aqi": 120,
        "max_wind_kmh": 12,
        "max_rain_prob": 15,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Outdoor airshuttles / heavy nylon wind-resistant shuttlecocks",
            "Tension-grip badminton rackets",
            "Non-slip court shoes and sweat wristbands",
            "Hydration bottle"
        ],
        "watch_note": "Outdoor shuttlecocks drift wildly in wind over 10 km/h; seek tree-canopy sheltered courtyards or enclosed garden lawns."
    },

    # 13. Outdoor Fitness & Yoga (Supplemental)
    "fitness": {
        "id": "fitness",
        "label": "Outdoor Fitness, Yoga & Calisthenics",
        "icon": "HeartPulse",
        "category": "Cardio & Fitness",
        "description": "Bodyweight, yoga, and calisthenics sessions requiring clean air, serene green surroundings, and shaded turf.",
        "osm_filters": [
            '["leisure"="fitness_station"]',
            '["leisure"="park"]',
            '["leisure"="garden"]',
            '["leisure"="recreation_ground"]'
        ],
        "ideal_temp": (16, 28),
        "max_temp": 33,
        "min_temp": 10,
        "max_aqi": 100,
        "max_wind_kmh": 22,
        "max_rain_prob": 20,
        "needs_daylight": False,
        "golden_hour_bonus": True,
        "carry": [
            "Non-slip rubber or natural cork outdoor yoga mat",
            "Resistance bands / workout accessories",
            "Chilled electrolyte water (1L)",
            "Insect repellent lotion & sweat towel"
        ],
        "watch_note": "Pranayama and deep breathwork demand clean air (AQI < 100); dawn hours inside botanical parks offer optimal oxygenation."
    },

    # 14. Basketball (Supplemental)
    "basketball": {
        "id": "basketball",
        "label": "Outdoor Basketball",
        "icon": "Trophy",
        "category": "Team Sports",
        "description": "Asphalt or concrete outdoor hoop play requiring dry court traction.",
        "osm_filters": [
            '["sport"="basketball"]',
            '["leisure"="pitch"]',
            '["leisure"="sports_centre"]'
        ],
        "ideal_temp": (15, 30),
        "max_temp": 35,
        "min_temp": 8,
        "max_aqi": 120,
        "max_wind_kmh": 22,
        "max_rain_prob": 15,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "High-traction outdoor basketball shoes",
            "Moisture-wicking athletic jersey and shorts",
            "1L electrolyte hydration drink",
            "Ankle braces / compression sleeves"
        ],
        "watch_note": "Outdoor concrete becomes slick with light dew or drizzle, leading to ankle inversion injuries."
    },

    # 15. General Outdoor Outing (Universal Fallback)
    "general_outdoor": {
        "id": "general_outdoor",
        "label": "General Outdoor Outing",
        "icon": "Compass",
        "category": "Leisure & Social",
        "description": "General open-air campus walk, park visit, or casual exploration.",
        "osm_filters": [
            '["leisure"="park"]',
            '["leisure"="garden"]',
            '["leisure"="recreation_ground"]',
            '["amenity"="university"]',
            '["tourism"="attraction"]'
        ],
        "ideal_temp": (16, 29),
        "max_temp": 34,
        "min_temp": 8,
        "max_aqi": 120,
        "max_wind_kmh": 26,
        "max_rain_prob": 30,
        "needs_daylight": False,
        "golden_hour_bonus": False,
        "carry": [
            "Comfortable walking / casual outdoor footwear",
            "Reusable 750ml water bottle",
            "Sun hat or sunglasses for daytime solar protection",
            "Lightweight compact rain umbrella if overcast"
        ],
        "watch_note": "General recreation is adaptable; stay attentive to midday sun intensity and carry water."
    }
}
