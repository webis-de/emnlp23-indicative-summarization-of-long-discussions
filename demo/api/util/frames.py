import re

frame_names = {
    "economic": ["financial"],
    "capacity and resources": [],
    "morality": ["moral", "ethic"],
    "fairness and equality": [],
    "legality, constitutionality and jurisprudence": ["legality", "legal"],
    "policy prescription and evaluation": [],
    "crime and punishment": [],
    "security and defense": ["security"],
    "health and safety": [
        "safety and danger",
        "healthcare",
        "safety",
        "health",
        "medicine",
    ],
    "quality of life": [],
    "cultural identity": ["cultural"],
    "public opinion": [],
    "political": ["politics"],
    "external regulation and reputation": [],
}

alt_frame_names = {}
for frame, alt_frames in frame_names.items():
    for alt_frame in alt_frames:
        alt_frame_names[alt_frame] = frame

new_frames = [
    "environmental",
    "technology and innovation",
    "emotional valence",
    "professionalism",
    "sport",
    "gender",
    "social norms",
    "education",
    "immigration",
    "superheroes",
    "abilities",
    "science and technology",
    "religion and belief",
    "scientific rigor",
]

frame_regex = re.compile("|".join(frame_names))
alt_frame_regex = re.compile("|".join(alt_frame_names))
left_regex = re.compile(r'^[ \n\t,"]*$')


def parse_frames(labels):
    left = labels.lower()
    parsed = frame_regex.findall(left)
    left = frame_regex.sub("", left)
    alt_frames = alt_frame_regex.findall(left)
    parsed.extend([alt_frame_names[alt_frame] for alt_frame in alt_frames])
    left = alt_frame_regex.sub("", left)
    unique = []
    for e in parsed:
        if e not in unique:
            unique.append(e)
    return unique
