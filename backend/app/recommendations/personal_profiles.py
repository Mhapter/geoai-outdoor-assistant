"""
Personal health, demographic, and vulnerability constraints for Fieldwise.
Conservative, transparent risk adjustments without diagnosing or medical prescription.
"""

from typing import Dict, Any

PROFILE_MODIFIERS: Dict[str, Dict[str, Any]] = {
    "asthma": {
        "id": "asthma",
        "label": "Asthma & Respiratory Sensitivity",
        "icon": "Lungs",
        "max_aqi": 75,
        "max_pm25": 25.0,
        "max_wind_kmh": 22,
        "downwind_penalty_multiplier": 2.5,
        "extra_carry": [
            "Prescribed fast-acting rescue inhaler (albuterol / salbutamol)",
            "N95/FFP2 protective respirator mask for transit near arterial roads"
        ],
        "watch_note": "Strictly avoid hours where US AQI exceeds 75 or when wind blows directly from expressways or industrial zones toward the venue."
    },
    "senior": {
        "id": "senior",
        "label": "Senior Citizens / Elderly Parents",
        "icon": "HeartHandshake",
        "ideal_temp": (18, 27),
        "max_temp": 31,
        "min_temp": 12,
        "max_aqi": 90,
        "downwind_penalty_multiplier": 1.8,
        "extra_carry": [
            "Insulated thermal bottle with lukewarm or cool water",
            "Wide-brim sun hat and walking stick if on unpaved gravel trails",
            "Cushioned non-slip ergonomic walking shoes"
        ],
        "watch_note": "Avoid peak midday solar and UV exposure (11:30 AM – 3:30 PM); choose shaded pathways with resting benches and level grades."
    },
    "child": {
        "id": "child",
        "label": "Children & Kids Outing",
        "icon": "Baby",
        "ideal_temp": (17, 29),
        "max_temp": 32,
        "min_temp": 10,
        "max_aqi": 95,
        "downwind_penalty_multiplier": 1.8,
        "extra_carry": [
            "Additional 1L water bottles and electrolyte fruit juices",
            "Pediatric mineral SPF 50+ sunscreen and lightweight caps",
            "Antiseptic wipes, sting relief ointment, and adhesive bandages"
        ],
        "watch_note": "Children have higher ventilation rates per kg body weight; prioritize tree-canopy parks well away from arterial expressway exhaust plumes."
    },
    "pregnancy": {
        "id": "pregnancy",
        "label": "Pregnancy & Expecting Mothers",
        "icon": "ShieldHeart",
        "ideal_temp": (18, 27),
        "max_temp": 30,
        "min_temp": 12,
        "max_aqi": 85,
        "downwind_penalty_multiplier": 2.0,
        "extra_carry": [
            "Electrolyte hydration flask",
            "Cooling neck towel and portable USB handheld fan",
            "Compact folding cushion/stool for frequent sitting breaks"
        ],
        "watch_note": "Prioritize low heat-index windows, clean air (AQI < 85), short transit times (< 20 mins), and venues with level paved paths and accessible clean restrooms."
    }
}
