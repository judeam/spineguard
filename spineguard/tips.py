"""Health tips for SpineGuard breaks and reminders."""

import random

WALK_TIPS = [
    "Keep your spine neutral - avoid bending forward when you return",
    "When walking, engage your core slightly to support your lower back",
    "Avoid sitting for more than 30 minutes after this break",
    "Walk tall with your shoulders back - good posture aids healing",
    "Take slow, mindful steps - rushing stresses your spine",
    "If you feel any sharp pain, slow down and adjust your posture",
    "Gentle movement promotes blood flow to your spinal discs",
    "Use the handrail on stairs to reduce lower back load",
    "Keep your head balanced over your spine, not jutting forward",
    "Walking is one of the best activities for back health",
]

LIE_DOWN_TIPS = [
    "Lie on your back with knees bent, feet flat - this decompresses your lower back",
    "Try placing a pillow under your knees for extra decompression",
    "Focus on deep belly breathing while lying down",
    "Try the 90-90 position: lie on the floor with your calves resting on your bed, hips and knees at 90 degrees - maximum decompression",
    "If comfortable, try a gentle prone press-up while lying down",
    "Avoid any flexion (bending forward) - extension is your friend",
    "Let gravity decompress your spine - relax completely",
    "Place a small rolled towel under your lower back for extra support",
    "Breathe into your belly, not your chest - this relaxes back muscles",
    "This position allows your spinal discs to rehydrate and decompress",
]

POSITION_SWITCH_TIPS = [
    "Alternate between sitting and standing to reduce spinal compression",
    "When standing, keep your weight evenly distributed on both feet",
    "Adjust your monitor height each time you switch positions",
    "Standing engages your core muscles and promotes better posture",
    "When sitting after standing, focus on maintaining the good posture you had",
    "Position changes improve circulation and reduce spinal compression",
    "Keep your keyboard and mouse at elbow height in both positions",
    "Stand with a slight bend in your knees - don't lock them",
    "Use an anti-fatigue mat when standing for extra comfort",
    "Switching positions regularly prevents muscle fatigue and stiffness",
    "Your spine has natural curves - maintain them in both positions",
    "Take a few deep breaths each time you switch positions",
]

GENERAL_TIPS = [
    "Consistency matters more than intensity for back health",
    "Regular movement is the best prevention for back problems",
    "Avoid prolonged sitting, heavy lifting, and bending forward",
    "Your spine benefits from every break you take",
    "Sleep is crucial for spinal health - prioritize rest tonight",
    "Ice or heat can help relieve back tension and discomfort",
    "Gentle movement is medicine for your back",
    "Small daily habits make the biggest difference for your spine",
]

WATER_TIPS = [
    "Hydration check - drink a glass of water",
    "Your spinal discs need water to stay healthy - drink up",
    "Hydration helps maintain disc height and flexibility",
    "Stay hydrated to support your body's healing process",
    "Time for water - your spine will thank you",
]

PHYSIO_TIPS = [
    "Consistency is key — even a short physio session helps your recovery",
    "Focus on form, not speed — quality reps matter more",
    "Breathe steadily through each exercise — don't hold your breath",
    "Listen to your body — push gently but stop if you feel sharp pain",
    "Your future self will thank you for doing this today",
    "Every physio session builds on the last — progress is cumulative",
    "Engage your core during exercises to protect your spine",
    "Slow, controlled movements are more effective than rushing through",
    "Think of this as maintenance for your body — it keeps everything running",
    "You're investing in your mobility and quality of life right now",
]

SUPPLEMENT_MORNING = [
    "Time for your morning supplements",
    "Start the day right - take your morning supplements",
    "Morning supplement reminder - support your healing",
]

SUPPLEMENT_EVENING = [
    "Don't forget your evening supplements",
    "Evening supplement time - consistency is key",
    "Time for your evening supplements",
]


# Structured exercise routines for walk breaks
WALK_ROUTINES = [
    {
        "name": "McKenzie Standing Extensions",
        "benefit": "Relieves lower back pressure and improves spinal extension",
        "steps": [
            {"instruction": "Stand with feet shoulder-width apart, hands on lower back", "duration_seconds": 10},
            {"instruction": "Slowly lean backward, supporting with your hands — hold 5 seconds", "duration_seconds": 15},
            {"instruction": "Return to upright. Repeat the extension", "duration_seconds": 15},
            {"instruction": "Extend again — try to go slightly further each time", "duration_seconds": 15},
            {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
        ],
    },
    {
        "name": "Gentle Walking Stretch Routine",
        "benefit": "Loosens hip flexors and mobilizes the spine gently",
        "steps": [
            {"instruction": "Walk slowly, focusing on heel-to-toe gait", "duration_seconds": 30},
            {"instruction": "Stop. Standing hip flexor stretch: step one foot forward, gently push hips forward — hold", "duration_seconds": 20},
            {"instruction": "Switch legs and repeat the hip flexor stretch", "duration_seconds": 20},
            {"instruction": "Standing tall, gently rotate your trunk left and right 5 times each", "duration_seconds": 20},
            {"instruction": "Continue walking with engaged core for the remaining time", "duration_seconds": 0},
        ],
    },
    {
        "name": "Posture Reset Walk",
        "benefit": "Resets spinal alignment and engages stabilizing muscles",
        "steps": [
            {"instruction": "Stand tall. Pull shoulder blades together and down — hold 10 seconds", "duration_seconds": 15},
            {"instruction": "Tuck your chin slightly (double chin). Hold 10 seconds", "duration_seconds": 15},
            {"instruction": "Walk with this posture: shoulders back, chin tucked, core engaged", "duration_seconds": 30},
            {"instruction": "Stop. Reach arms overhead, interlace fingers, stretch upward — hold", "duration_seconds": 15},
            {"instruction": "Resume walking with good posture for the remaining time", "duration_seconds": 0},
        ],
    },
]

# Structured exercise routines for lie-down breaks
LIE_DOWN_ROUTINES = [
    {
        "name": "90-90 Spinal Decompression",
        "benefit": "Maximum lower back decompression with gravity-assisted positioning",
        "steps": [
            {"instruction": "Lie on your back. Place calves on a chair/bed — hips and knees at 90 degrees", "duration_seconds": 20},
            {"instruction": "Let your arms rest at your sides. Close your eyes. Breathe deeply", "duration_seconds": 30},
            {"instruction": "Focus on belly breathing — inflate your stomach on inhale, flatten on exhale", "duration_seconds": 60},
            {"instruction": "Gently press your lower back into the floor and release — repeat 5 times", "duration_seconds": 30},
            {"instruction": "Continue resting in the 90-90 position, breathing deeply", "duration_seconds": 0},
        ],
    },
    {
        "name": "Prone Press-Up Sequence",
        "benefit": "McKenzie extension to relieve lower back tension",
        "steps": [
            {"instruction": "Lie face down, arms at your sides. Relax completely for 30 seconds", "duration_seconds": 30},
            {"instruction": "Place palms near your shoulders. Gently press up, keeping hips on the floor", "duration_seconds": 15},
            {"instruction": "Hold the press-up for 5 seconds, then slowly lower back down", "duration_seconds": 15},
            {"instruction": "Repeat the press-up. Try to extend slightly further each time", "duration_seconds": 30},
            {"instruction": "Rest face down, arms at sides. Breathe deeply for remaining time", "duration_seconds": 0},
        ],
    },
    {
        "name": "Supine Relaxation & Breathing",
        "benefit": "Deep muscle relaxation and spinal decompression",
        "steps": [
            {"instruction": "Lie on your back, knees bent, feet flat on the floor", "duration_seconds": 15},
            {"instruction": "Place a small pillow or rolled towel under your neck. Arms at sides", "duration_seconds": 10},
            {"instruction": "Breathe in through your nose for 4 counts, filling your belly", "duration_seconds": 30},
            {"instruction": "Breathe out through your mouth for 6 counts. Feel your back relax into the floor", "duration_seconds": 30},
            {"instruction": "Continue this breathing pattern. Let gravity decompress your spine", "duration_seconds": 0},
        ],
    },
    {
        "name": "Gentle Knee-to-Chest Stretch",
        "benefit": "Stretches lower back muscles and opens spinal joints",
        "steps": [
            {"instruction": "Lie on your back, knees bent, feet flat", "duration_seconds": 10},
            {"instruction": "Slowly bring one knee toward your chest — hold with both hands for 15 seconds", "duration_seconds": 20},
            {"instruction": "Switch legs. Bring the other knee to chest — hold 15 seconds", "duration_seconds": 20},
            {"instruction": "Gently bring both knees to chest together — hold 15 seconds", "duration_seconds": 20},
            {"instruction": "Return to starting position. Rest with deep breathing for remaining time", "duration_seconds": 0},
        ],
    },
]


def get_walk_routine() -> dict:
    """Get a random walk routine."""
    return random.choice(WALK_ROUTINES)


def get_lie_down_routine() -> dict:
    """Get a random lie-down routine."""
    return random.choice(LIE_DOWN_ROUTINES)


def get_walk_tip() -> str:
    """Get a random tip for walk breaks."""
    all_tips = WALK_TIPS + GENERAL_TIPS
    return random.choice(all_tips)


def get_lie_down_tip() -> str:
    """Get a random tip for lie down breaks."""
    all_tips = LIE_DOWN_TIPS + GENERAL_TIPS
    return random.choice(all_tips)


def get_water_tip() -> str:
    """Get a random water reminder."""
    return random.choice(WATER_TIPS)


def get_position_switch_tip() -> str:
    """Get a random tip for position switch breaks."""
    all_tips = POSITION_SWITCH_TIPS + GENERAL_TIPS
    return random.choice(all_tips)


def get_physio_tip() -> str:
    """Get a random tip for physio workout breaks."""
    return random.choice(PHYSIO_TIPS)


def get_supplement_tip(morning: bool) -> str:
    """Get a supplement reminder for morning or evening."""
    if morning:
        return random.choice(SUPPLEMENT_MORNING)
    return random.choice(SUPPLEMENT_EVENING)
