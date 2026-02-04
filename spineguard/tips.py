"""Health tips for SpineGuard breaks and reminders."""

import random

WALK_TIPS = [
    "Keep your spine neutral - avoid bending forward when you return",
    "When walking, engage your core slightly to support your lower back",
    "Avoid sitting for more than 30 minutes after this break",
    "Walk tall with your shoulders back - good posture aids healing",
    "Take slow, mindful steps - rushing stresses your spine",
    "If you feel any sharp pain, slow down and adjust your posture",
    "Gentle movement promotes blood flow to the healing disc",
    "Avoid stairs if possible - they increase spinal load",
    "Keep your head balanced over your spine, not jutting forward",
    "Walking is one of the best activities for disc recovery",
]

LIE_DOWN_TIPS = [
    "Lie on your back with knees bent, feet flat - this decompresses L5-S1",
    "Try placing a pillow under your knees for extra decompression",
    "Focus on deep belly breathing while lying down",
    "Try the 90-90 position: lie on the floor with your calves resting on your bed, hips and knees at 90 degrees - maximum decompression",
    "If comfortable, try a gentle prone press-up while lying down",
    "Avoid any flexion (bending forward) - extension is your friend",
    "Let gravity decompress your spine - relax completely",
    "Place a small rolled towel under your lower back for extra support",
    "Breathe into your belly, not your chest - this relaxes back muscles",
    "This position allows your disc to rehydrate and heal",
]

GENERAL_TIPS = [
    "Healing takes time - consistency matters more than intensity",
    "Nerve pain decreasing? That's centralization - a good sign",
    "Avoid prolonged sitting, heavy lifting, and bending forward",
    "Your disc is healing every day, even when you can't feel it",
    "Sleep is crucial for recovery - prioritize rest tonight",
    "Ice can help reduce inflammation around the nerve",
    "Gentle movement is medicine for disc injuries",
    "Patience and consistency will get you through this",
]

WATER_TIPS = [
    "Hydration check - drink a glass of water",
    "Your discs need water to stay healthy - drink up",
    "Water helps maintain disc height and flexibility",
    "Stay hydrated to support your body's healing process",
    "Time for water - your spine will thank you",
]

SUPPLEMENT_MORNING = [
    "Time for your morning supplements",
    "Start the day right - take your morning supplements",
    "Morning supplement reminder - support your healing",
]

SUPPLEMENT_EVENING = [
    "Don't forget your evening supplements",
    "Evening supplement time - consistency aids recovery",
    "Time for your evening supplements",
]


def get_walk_tip() -> str:
    """Get a random tip for walk breaks."""
    tips = WALK_TIPS + GENERAL_TIPS
    return random.choice(tips)


def get_lie_down_tip() -> str:
    """Get a random tip for lie down breaks."""
    tips = LIE_DOWN_TIPS + GENERAL_TIPS
    return random.choice(tips)


def get_water_tip() -> str:
    """Get a random water reminder."""
    return random.choice(WATER_TIPS)


def get_supplement_tip(morning: bool) -> str:
    """Get a supplement reminder for morning or evening."""
    if morning:
        return random.choice(SUPPLEMENT_MORNING)
    return random.choice(SUPPLEMENT_EVENING)
