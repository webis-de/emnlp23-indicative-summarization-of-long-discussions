import json
from pathlib import Path

FRAMES = {
    "economic": {
        "description": "costs, benefits, or other financial implications",
        "long_description": "The costs, benefits, or monetary/financial implications of the issue (to an individual, family, community, or to the economy as a whole).",
    },
    "capacity and resources": {
        "description": "availability of physical, human or financial resources, and capacity of current systems",
        "long_description": "The lack of or availability of physical, geographical, spatial, human, and financial resources, or the capacity of existing systems and resources to implement or carry out policy goals.",
    },
    "morality": {
        "description": "religious or ethical implications",
        "long_description": "Any perspective or policy objective or action (including proposed action) that is compelled by religious doctrine or interpretation, duty, honor, righteousness or any other sense of ethics or social responsibility.",
    },
    "fairness and equality": {
        "description": "balance or distribution of rights, responsibilities, and resources",
        "long_description": "Equality or inequality with which laws, punishment, rewards, and resources are applied or distributed among individuals or groups. Also the balance between the rights or interests of one individual or group compared to another individual or group.",
    },
    "legality, constitutionality and jurisprudence": {
        "description": "rights, freedoms, and authority of individuals, corporations, and government",
        "long_description": "The constraints imposed on or freedoms granted to individuals, government, and corporations via the Constitution, Bill of Rights and other amendments, or judicial interpretation. This deals specifically with the authority of government to regulate, and the authority of individuals/corporations to act independently of government.",
    },
    "policy prescription and evaluation": {
        "description": "discussion of specific policies aimed at addressing problems",
        "long_description": "Particular policies proposed for addressing an identified problem, and figuring out if certain policies will work, or if existing policies are effective.",
    },
    "crime and punishment": {
        "description": "effectiveness and implications of laws and their enforcement",
        "long_description": "Specific policies in practice and their enforcement, incentives, and implications. Includes stories about enforcement and interpretation of laws by individuals and law enforcement, breaking laws, loopholes, fines, sentencing and punishment. Increases or reductions in crime.",
    },
    "security and defense": {
        "description": "threats to welfare of the individual, community, or nation",
        "long_description": "Security, threats to security, and protection of one's person, family, in-group, nation, etc. Generally an action or a call to action that can be taken to protect the welfare of a person, group, nation sometimes from a not yet manifested threat.",
    },
    "health and safety": {
        "description": "health care, sanitation, public safety",
        "long_description": "Healthcare access and effectiveness, illness, disease, sanitation, obesity, mental health effects, prevention of or perpetuation of gun violence, infrastructure and building safety.",
    },
    "quality of life": {
        "description": "threats and opportunities for the individual's wealth, happiness, and well-being",
        "long_description": "The effects of a policy on individuals' wealth, mobility, access to resources, happiness, social structures, ease of day-to-day routines, quality of community life, etc.",
    },
    "cultural identity": {
        "description": "traditions, customs, or values of a social group in relation to a policy issue",
        "long_description": "The social norms, trends, values and customs constituting culture(s), as they relate to a specific policy issue.",
    },
    "public opinion": {
        "description": "attitudes and opinions of the general public, including polling and demographics",
        "long_description": 'References to general social attitudes, polling and demographic information, as well as implied or actual consequences of diverging from or "getting ahead of" public opinion or polls.',
    },
    "political": {
        "description": "considerations related to politics and politicians, including lobbying, elections, and attempts to sway voters",
        "long_description": "Any political considerations surrounding an issue. Issue actions or efforts or stances that are political, such as partisan filibusters, lobbyist involvement, bipartisan efforts, deal-making and vote trading, appealing to one's base, mentions of political maneuvering. Explicit statements that a policy issue is good or bad for a particular political party.",
    },
    "external regulation and reputation": {
        "description": "international reputation or foreign policy of the U.S.",
        "long_description": "The United States' external relations with another nation; the external relations of one state with another; or relations between groups. This includes trade agreements and outcomes, comparisons of policy outcomes or desired policy outcomes.",
    },
}


ANNOTATIONS_PATH = (
    Path(__file__).absolute().parent / "data" / "labeled" / "annotations.json"
)
annotations = json.loads(ANNOTATIONS_PATH.read_text())
examples = annotations["examples"]

for frame, definition in FRAMES.items():
    key = frame.replace(",", "").replace(" ", "_")
    definition["examples"] = examples[key]


AUTHORS = 'Boydstun, Amber E. et al. "Tracking the Development of Media Frames within and across Policy Issues." (2014)'


zero_shot_extreme_input = {
    "authors": AUTHORS,
    "input_type": "list",
    "frames": json.dumps(list(FRAMES.keys()), ensure_ascii=True),
}


zero_shot_simple_input = {
    "authors": AUTHORS,
    "input_type": "json",
    "frames": json.dumps(
        {
            frame: {"description": definition["description"]}
            for frame, definition in FRAMES.items()
        },
        ensure_ascii=True,
    ),
}


zero_shot_input = {
    "authors": AUTHORS,
    "input_type": "json",
    "frames": json.dumps(
        {
            frame: {"description": definition["long_description"]}
            for frame, definition in FRAMES.items()
        },
        ensure_ascii=True,
    ),
}


few_shot_input = {
    "authors": AUTHORS,
    "input_type": "json",
    "frames": json.dumps(
        {
            frame: {
                "description": definition["long_description"],
                "examples": definition["examples"],
            }
            for frame, definition in FRAMES.items()
        },
        ensure_ascii=True,
    ),
}


INSTRUCTION_ARGUMENTS = {
    "zero_shot_extreme": zero_shot_extreme_input,
    "zero_shot_simple": zero_shot_simple_input,
    "zero_shot": zero_shot_input,
    "few_shot": few_shot_input,
}
