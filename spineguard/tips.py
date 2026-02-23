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


# Structured exercise routines for walk breaks, organized into progressive tracks
WALK_TRACKS = {
    "spinal_extension": {
        "name": "Spinal Extension",
        "focus": "McKenzie method",
        "routines": [
            # Level 1
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
            # Level 2
            {
                "name": "Wall Press-Ups",
                "benefit": "Progresses spinal extension with upper body support",
                "steps": [
                    {"instruction": "Stand facing a wall, about arm's length away. Place palms flat on the wall at chest height", "duration_seconds": 10},
                    {"instruction": "Lean your hips toward the wall while keeping your feet planted — feel the extension in your lower back. Hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Push back to upright. Repeat, pressing hips closer to the wall each time", "duration_seconds": 15},
                    {"instruction": "Move hands slightly higher on the wall and repeat — this increases the extension range", "duration_seconds": 15},
                    {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3
            {
                "name": "Standing Back Bends",
                "benefit": "Full range spinal extension without wall support",
                "steps": [
                    {"instruction": "Stand with feet shoulder-width apart. Place hands on your lower back for support", "duration_seconds": 10},
                    {"instruction": "Inhale and slowly arch backward, leading with your chest. Hold 5 seconds at end range", "duration_seconds": 15},
                    {"instruction": "Return to upright on the exhale. Repeat, reaching slightly further back each time", "duration_seconds": 15},
                    {"instruction": "Perform 3 more extensions — hold each for 5 seconds at full range. Breathe steadily", "duration_seconds": 20},
                    {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4
            {
                "name": "Dynamic Extension Walk",
                "benefit": "Combines spinal extension with walking movement",
                "steps": [
                    {"instruction": "Begin walking at a comfortable pace with hands on your lower back", "duration_seconds": 15},
                    {"instruction": "Every 5 steps, pause and perform a gentle standing back extension. Hold 3 seconds", "duration_seconds": 20},
                    {"instruction": "Resume walking. Focus on a slight backward lean as you walk — chest up, shoulders back", "duration_seconds": 20},
                    {"instruction": "Perform 3 deeper extensions while stationary — reach further each time", "duration_seconds": 15},
                    {"instruction": "Continue walking with upright, extended posture for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
    "lower_body": {
        "name": "Lower Body",
        "focus": "Glute/leg activation",
        "routines": [
            # Level 1
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
            # Level 2
            {
                "name": "Single-Leg Balance & Glute Activation",
                "benefit": "Strengthens hip stabilizers and improves pelvic control",
                "steps": [
                    {"instruction": "Stand tall, feet hip-width apart. Shift weight to your left foot", "duration_seconds": 10},
                    {"instruction": "Lift your right foot off the floor. Balance for 20 seconds — squeeze your standing glute", "duration_seconds": 25},
                    {"instruction": "Switch sides. Balance on your right foot for 20 seconds", "duration_seconds": 25},
                    {"instruction": "Standing on one leg, slowly hinge forward at the hips (warrior 3). Hold 10 seconds each side", "duration_seconds": 30},
                    {"instruction": "Walk with engaged glutes and core for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3
            {
                "name": "Wall Sit & Isometric Hold",
                "benefit": "Builds quad and core endurance to support the lower back",
                "steps": [
                    {"instruction": "Find a wall. Lean your back flat against it and slide down until knees are at 90 degrees", "duration_seconds": 10},
                    {"instruction": "Hold the wall sit — keep your lower back pressed into the wall. Breathe steadily", "duration_seconds": 30},
                    {"instruction": "Stand up and shake out your legs for 10 seconds", "duration_seconds": 15},
                    {"instruction": "Wall sit again — this time squeeze a fist between your knees to activate inner thighs", "duration_seconds": 30},
                    {"instruction": "Stand and walk slowly, focusing on tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4
            {
                "name": "Walking Lunges",
                "benefit": "Dynamic leg strengthening with spinal stability challenge",
                "steps": [
                    {"instruction": "Stand tall with hands on hips, core braced. Take a large step forward with your right foot", "duration_seconds": 10},
                    {"instruction": "Lower your back knee toward the floor, keeping your torso upright. Push through the front heel to step forward. Alternate legs — 5 each side", "duration_seconds": 30},
                    {"instruction": "Rest standing for 10 seconds. Shake out your legs", "duration_seconds": 15},
                    {"instruction": "Perform 5 more lunges each side — focus on keeping your spine neutral and core tight throughout", "duration_seconds": 30},
                    {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
    "posture": {
        "name": "Posture",
        "focus": "Alignment",
        "routines": [
            # Level 1
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
            # Level 2
            {
                "name": "Standing Pallof Press (Imaginary)",
                "benefit": "Anti-rotation core training to protect the spine under load",
                "steps": [
                    {"instruction": "Stand with feet shoulder-width apart, arms extended in front of your chest, hands clasped", "duration_seconds": 10},
                    {"instruction": "Brace your core. Slowly rotate your clasped hands to the left — resist with your trunk. Hold 5 seconds", "duration_seconds": 15},
                    {"instruction": "Return to centre. Rotate to the right — resist with your trunk. Hold 5 seconds", "duration_seconds": 15},
                    {"instruction": "Repeat: left hold 5s, centre, right hold 5s. Focus on keeping hips square", "duration_seconds": 20},
                    {"instruction": "Walk with engaged core, feeling your obliques activated, for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3
            {
                "name": "Thoracic Rotation Walk",
                "benefit": "Mobilizes the thoracic spine to reduce compensatory lower back movement",
                "steps": [
                    {"instruction": "Stand tall, arms crossed over your chest with hands on opposite shoulders", "duration_seconds": 10},
                    {"instruction": "Slowly rotate your upper body to the left, keeping hips square. Hold 5 seconds. Rotate right. Hold 5 seconds", "duration_seconds": 20},
                    {"instruction": "Walk forward, gently rotating your torso left and right with each step — like a controlled twist walk", "duration_seconds": 20},
                    {"instruction": "Stop. Place hands behind your head. Rotate left and right 5 times each — feel the mid-back open up", "duration_seconds": 20},
                    {"instruction": "Continue walking with an open chest and relaxed shoulders for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4
            {
                "name": "Farmer's Walk",
                "benefit": "Builds grip, core, and postural endurance under load",
                "steps": [
                    {"instruction": "Pick up a moderately heavy object in each hand (water bottles, books, or bags). Stand tall, shoulders down and back", "duration_seconds": 10},
                    {"instruction": "Walk slowly with the weights at your sides — keep your core braced and avoid leaning to either side", "duration_seconds": 25},
                    {"instruction": "Stop and rest for 10 seconds. Reset your posture: shoulders back, chest up, neutral spine", "duration_seconds": 15},
                    {"instruction": "Walk again with the weights. Focus on squeezing your shoulder blades together and breathing steadily", "duration_seconds": 25},
                    {"instruction": "Set the weights down. Walk with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
}

# Structured exercise routines for lie-down breaks, organized into progressive tracks
LIE_DOWN_TRACKS = {
    "decompression": {
        "name": "Decompression",
        "focus": "Spinal relief",
        "routines": [
            # Level 1
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
            # Level 2
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
            # Level 3
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
            # Level 4
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
        ],
    },
    "core_stability": {
        "name": "Core Stability",
        "focus": "Deep core",
        "routines": [
            # Level 1
            {
                "name": "Dead Bug Anti-Extension",
                "benefit": "Builds deep core strength while keeping the lower back safe and supported",
                "steps": [
                    {"instruction": "Lie on your back. Raise arms straight to ceiling, knees bent at 90 degrees (tabletop position)", "duration_seconds": 10},
                    {"instruction": "Press your lower back into the floor — this is your brace. Don't let it arch", "duration_seconds": 10},
                    {"instruction": "Slowly extend your right arm overhead and left leg straight out. Return. Alternate sides — 5 each", "duration_seconds": 40},
                    {"instruction": "If that's easy: extend both opposite limbs and hold 5 seconds at full extension. 3 each side", "duration_seconds": 30},
                    {"instruction": "Return to starting position and rest. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 2
            {
                "name": "Bird-Dog Core Stability",
                "benefit": "Trains anti-rotation and spinal stabilization through contralateral movement",
                "steps": [
                    {"instruction": "Get on all fours — hands under shoulders, knees under hips. Neutral spine", "duration_seconds": 10},
                    {"instruction": "Extend your right arm forward and left leg back simultaneously. Hold 5 seconds", "duration_seconds": 10},
                    {"instruction": "Return to start. Extend left arm and right leg. Hold 5 seconds. Alternate 5 each side", "duration_seconds": 40},
                    {"instruction": "Slow it down: extend and hold each rep for 10 seconds. 3 each side", "duration_seconds": 30},
                    {"instruction": "Return to all fours, then sit back into child's pose. Rest for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3
            {
                "name": "Side Plank Progression",
                "benefit": "Strengthens obliques and quadratus lumborum — key spinal stabilizers",
                "steps": [
                    {"instruction": "Lie on your right side, knees bent. Prop up on your right elbow under your shoulder", "duration_seconds": 10},
                    {"instruction": "Lift your hips off the floor into a modified side plank (knees down). Hold 20 seconds", "duration_seconds": 25},
                    {"instruction": "Lower and rest 10 seconds. If able, try a full side plank with legs straight", "duration_seconds": 15},
                    {"instruction": "Switch to your left side. Modified or full side plank — hold 20 seconds", "duration_seconds": 25},
                    {"instruction": "Lower and rest. Repeat each side once more if time allows", "duration_seconds": 0},
                ],
            },
            # Level 4
            {
                "name": "Hollow Body Hold",
                "benefit": "Trains anterior core bracing to protect the spine",
                "steps": [
                    {"instruction": "Lie on your back. Press your lower back firmly into the floor — this is your anchor point", "duration_seconds": 10},
                    {"instruction": "Raise your arms overhead and lift your legs straight, a few inches off the floor. Hold this hollow position for 15 seconds", "duration_seconds": 20},
                    {"instruction": "Rest for 10 seconds. If too hard, bend your knees or keep arms at your sides", "duration_seconds": 15},
                    {"instruction": "Hollow body hold again — aim for 20 seconds this time. Keep your lower back glued to the floor", "duration_seconds": 25},
                    {"instruction": "Release and rest on your back. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
    "hip_glute": {
        "name": "Hip & Glute",
        "focus": "Posterior chain",
        "routines": [
            # Level 1
            {
                "name": "Clamshells & Hip Strengthening",
                "benefit": "Activates gluteus medius to stabilize the pelvis and reduce lower back strain",
                "steps": [
                    {"instruction": "Lie on your right side, knees bent at 45 degrees, feet together. Head resting on your arm", "duration_seconds": 10},
                    {"instruction": "Keeping feet together, open your top knee like a clamshell. Squeeze at the top. 10 reps slowly", "duration_seconds": 30},
                    {"instruction": "Hold the last rep open for 10 seconds — feel the burn in your outer hip", "duration_seconds": 15},
                    {"instruction": "Switch to your left side. 10 slow clamshells, then hold the last rep open 10 seconds", "duration_seconds": 45},
                    {"instruction": "Lie on your back and rest. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 2
            {
                "name": "Glute Bridge Progression",
                "benefit": "Activates glutes and hamstrings to offload the lower back",
                "steps": [
                    {"instruction": "Lie on your back, knees bent, feet flat and hip-width apart. Arms at sides", "duration_seconds": 10},
                    {"instruction": "Squeeze your glutes and lift your hips to form a straight line from shoulders to knees. Hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Lower slowly. Repeat 5 times — squeeze hard at the top each time", "duration_seconds": 30},
                    {"instruction": "Single-leg bridge: extend one leg straight. Lift hips with the other. 5 reps each side", "duration_seconds": 40},
                    {"instruction": "Rest on your back with knees bent. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3
            {
                "name": "Side-Lying Hip Abduction Series",
                "benefit": "Strengthens lateral hip muscles to improve pelvic stability during walking and standing",
                "steps": [
                    {"instruction": "Lie on your right side, body in a straight line, head on your arm", "duration_seconds": 10},
                    {"instruction": "Keeping your top leg straight, lift it 30-45 degrees. Slowly lower. 10 reps", "duration_seconds": 30},
                    {"instruction": "Small circles with the top leg — 10 forward, 10 backward", "duration_seconds": 20},
                    {"instruction": "Switch to your left side. 10 leg lifts, then 10 circles each direction", "duration_seconds": 50},
                    {"instruction": "Lie on your back and rest. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4
            {
                "name": "Single-Leg Bridge",
                "benefit": "Unilateral glute strength with pelvic stability",
                "steps": [
                    {"instruction": "Lie on your back, knees bent, feet flat. Extend your right leg straight toward the ceiling", "duration_seconds": 10},
                    {"instruction": "Press through your left foot, squeeze your glute, and lift your hips. Hold 5 seconds at the top. 5 reps", "duration_seconds": 25},
                    {"instruction": "Switch legs. Right foot planted, left leg extended. 5 reps with a 5-second hold at the top", "duration_seconds": 25},
                    {"instruction": "Rest 10 seconds, then do 3 more reps each side — focus on keeping your pelvis level, no tilting", "duration_seconds": 30},
                    {"instruction": "Lower both feet to the floor and rest. Breathe deeply for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
}

# Breathing exercise data for guided breathing during breaks
BREATHING_EXERCISES = [
    {
        "name": "Box Breathing",
        "phases": [
            {"label": "Inhale", "seconds": 4},
            {"label": "Hold", "seconds": 4},
            {"label": "Exhale", "seconds": 4},
            {"label": "Hold", "seconds": 4},
        ],
    },
    {
        "name": "4-7-8 Relaxation",
        "phases": [
            {"label": "Inhale", "seconds": 4},
            {"label": "Hold", "seconds": 7},
            {"label": "Exhale", "seconds": 8},
        ],
    },
    {
        "name": "Diaphragmatic Breathing",
        "phases": [
            {"label": "Inhale deeply", "seconds": 5},
            {"label": "Exhale slowly", "seconds": 7},
        ],
    },
]


def get_track_routine(tracks: dict, track_id: str, level: int) -> dict | None:
    """Get the routine for a specific track and level (0-indexed)."""
    track = tracks.get(track_id)
    if not track:
        return None
    routines = track["routines"]
    if level < 0 or level >= len(routines):
        return None
    return routines[level]


def get_track_names(tracks: dict) -> list[tuple[str, str]]:
    """Get list of (track_id, display_name) tuples."""
    return [(tid, t["name"]) for tid, t in tracks.items()]


def get_breathing_exercise() -> dict:
    """Get a random breathing exercise."""
    return random.choice(BREATHING_EXERCISES)


def _random_routine(tracks: dict) -> dict:
    """Get a random routine from any track."""
    all_routines = []
    for track in tracks.values():
        all_routines.extend(track["routines"])
    return random.choice(all_routines)


def get_walk_routine() -> dict:
    """Get a random walk routine."""
    return _random_routine(WALK_TRACKS)


def get_lie_down_routine() -> dict:
    """Get a random lie-down routine."""
    return _random_routine(LIE_DOWN_TRACKS)


_TIP_SOURCES = {
    "walk": WALK_TIPS + GENERAL_TIPS,
    "lie_down": LIE_DOWN_TIPS + GENERAL_TIPS,
    "position_switch": POSITION_SWITCH_TIPS + GENERAL_TIPS,
    "water": WATER_TIPS,
    "physio": PHYSIO_TIPS,
}


def get_tip(tip_type: str) -> str:
    """Get a random tip for the given break/reminder type."""
    return random.choice(_TIP_SOURCES[tip_type])


def get_supplement_tip(morning: bool) -> str:
    """Get a supplement reminder for morning or evening."""
    return random.choice(SUPPLEMENT_MORNING if morning else SUPPLEMENT_EVENING)
