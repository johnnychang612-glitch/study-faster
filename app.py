import os
import random
import sqlite3
from functools import wraps

from flask import Flask, jsonify, request, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Change this when publishing.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "study-faster-change-this-before-publishing"
)

DATABASE = "study_faster.db"


# ============================================================
# GCSE CONTENT
# ============================================================

SUBJECTS = {
    "Maths": {
        "Number": {
            "notes": [
                "Number includes integers, decimals, fractions, percentages, powers and standard form.",
                "When working with fractions, keep answers exact where possible and simplify them.",
                "Index laws help simplify powers. For example, a^m × a^n = a^(m+n).",
                "Standard form is written as A × 10^n where 1 ≤ A < 10."
            ],
            "questions": [
                ("What is 25% of 80?", ["15", "20", "25", "30"], "20"),
                ("Write 0.0045 in standard form.", ["4.5 × 10^-3", "45 × 10^-3", "4.5 × 10^3", "0.45 × 10^-2"], "4.5 × 10^-3"),
                ("Simplify 2³ × 2⁴.", ["2⁷", "2¹²", "4⁷", "2⁸"], "2⁷"),
            ]
        },
        "Algebra": {
            "notes": [
                "Algebra uses letters to represent unknown values or variables.",
                "To solve equations, use inverse operations to isolate the unknown.",
                "To expand a bracket, multiply every term inside the bracket.",
                "Factorising reverses expansion. Look for common factors first."
            ],
            "questions": [
                ("Solve 3x + 7 = 22.", ["3", "5", "7", "9"], "5"),
                ("Expand 3(x + 4).", ["3x + 4", "3x + 12", "x + 12", "7x"], "3x + 12"),
                ("Factorise 6x + 18.", ["6(x + 3)", "3(x + 6)", "6(x + 18)", "x(6 + 18)"], "6(x + 3)"),
                ("Solve x² = 49.", ["7 only", "-7 only", "7 or -7", "49"], "7 or -7"),
            ]
        },
        "Ratio & Proportion": {
            "notes": [
                "Ratio compares quantities using the same units.",
                "Simplify ratios by dividing every part by the same factor.",
                "Direct proportion means two quantities change at a constant rate.",
                "Scale factors are used with similar shapes and proportional quantities."
            ],
            "questions": [
                ("Simplify 12:18.", ["2:3", "3:2", "4:5", "6:12"], "2:3"),
                ("Share £40 in the ratio 3:5. What is the smaller share?", ["£12", "£15", "£20", "£25"], "£15"),
                ("5 pens cost £2.50. How much is one pen?", ["£0.25", "£0.50", "£1", "£1.25"], "£0.50"),
            ]
        },
        "Percentages": {
            "notes": [
                "To find a percentage of an amount, multiply by the percentage as a decimal.",
                "A 10% increase uses the multiplier 1.10.",
                "A 25% decrease uses the multiplier 0.75.",
                "Percentage change can be calculated using change ÷ original × 100."
            ],
            "questions": [
                ("What is 20% of 80?", ["12", "16", "20", "24"], "16"),
                ("Increase £50 by 10%.", ["£55", "£60", "£45", "£50.10"], "£55"),
                ("Decrease £60 by 25%.", ["£35", "£40", "£45", "£50"], "£45"),
            ]
        },
        "Geometry": {
            "notes": [
                "Angles on a straight line total 180°.",
                "Angles around a point total 360°.",
                "The interior angles of a triangle total 180°.",
                "Area measures the space inside a shape and uses squared units."
            ],
            "questions": [
                ("What is the sum of angles in a triangle?", ["90°", "180°", "270°", "360°"], "180°"),
                ("Find the area of a rectangle 8 cm by 5 cm.", ["13 cm²", "26 cm²", "40 cm²", "80 cm²"], "40 cm²"),
                ("Angles on a straight line add to...", ["90°", "180°", "270°", "360°"], "180°"),
            ]
        },
        "Pythagoras": {
            "notes": [
                "Pythagoras' theorem applies to right-angled triangles.",
                "The formula is a² + b² = c².",
                "c is the hypotenuse, which is opposite the right angle.",
                "A 3-4-5 triangle is a common example."
            ],
            "questions": [
                ("A right triangle has sides 3 and 4. Find the hypotenuse.", ["5", "6", "7", "8"], "5"),
                ("The hypotenuse is 13 and one side is 5. Find the other side.", ["8", "10", "12", "14"], "12"),
                ("Which is Pythagoras' theorem?", ["a+b=c", "a²+b²=c²", "2a+2b=c", "ab=c²"], "a²+b²=c²"),
            ]
        },
        "Probability": {
            "notes": [
                "Probability measures how likely an event is.",
                "0 means impossible and 1 means certain.",
                "For equally likely outcomes, probability = favourable outcomes ÷ total outcomes.",
                "Probabilities can be represented as fractions, decimals or percentages."
            ],
            "questions": [
                ("What is the probability of rolling a 6 on a fair die?", ["1/2", "1/3", "1/6", "1/12"], "1/6"),
                ("A probability of 1 means an event is...", ["impossible", "unlikely", "certain", "random"], "certain"),
            ]
        },
        "Statistics": {
            "notes": [
                "The mean is the total divided by the number of values.",
                "The median is the middle value when data is ordered.",
                "The mode is the most common value.",
                "The range is maximum minus minimum."
            ],
            "questions": [
                ("What is the mean of 2, 4 and 6?", ["3", "4", "5", "6"], "4"),
                ("What is the range of 3, 7, 8 and 12?", ["5", "7", "9", "12"], "9"),
                ("Which is the middle value of ordered data?", ["Mean", "Median", "Mode", "Range"], "Median"),
            ]
        },
        "Graphs": {
            "notes": [
                "Graphs show relationships between quantities.",
                "A straight-line graph can often be described using y = mx + c.",
                "The gradient describes the rate of change.",
                "Coordinates are written as (x, y)."
            ],
            "questions": [
                ("Coordinates are written in which order?", ["x then y", "y then x", "x only", "y only"], "x then y"),
            ]
        }
    },

    "Biology": {
        "Cell Biology": {
            "notes": [
                "The nucleus contains genetic material and controls cell activities.",
                "Mitochondria are the site of aerobic respiration.",
                "Ribosomes are where proteins are made.",
                "Plant cells also contain chloroplasts, a cell wall and a large permanent vacuole."
            ],
            "questions": [
                ("Which organelle controls cell activities?", ["Nucleus", "Ribosome", "Vacuole", "Cell wall"], "Nucleus"),
                ("Where does aerobic respiration mainly occur?", ["Nucleus", "Mitochondria", "Chloroplasts", "Ribosomes"], "Mitochondria"),
                ("Where are proteins made?", ["Ribosomes", "Vacuoles", "Cell walls", "Chloroplasts"], "Ribosomes"),
            ]
        },
        "Organisation": {
            "notes": [
                "Cells form tissues, tissues form organs and organs form organ systems.",
                "The digestive system breaks large food molecules into smaller soluble molecules.",
                "Enzymes are biological catalysts.",
                "Different organs are adapted to their functions."
            ],
            "questions": [
                ("A group of similar cells working together is a...", ["tissue", "organ", "system", "organism"], "tissue"),
                ("What do enzymes do?", ["Speed up reactions", "Stop reactions", "Destroy cells", "Make DNA"], "Speed up reactions"),
            ]
        },
        "Infection & Response": {
            "notes": [
                "Pathogens are microorganisms that can cause disease.",
                "Bacteria and viruses are examples of pathogens.",
                "The immune system protects the body from pathogens.",
                "Vaccination helps the immune system develop memory against a pathogen."
            ],
            "questions": [
                ("What can cause an infectious disease?", ["Pathogen", "Vitamin", "Enzyme", "Hormone"], "Pathogen"),
                ("What is one purpose of vaccination?", ["Train the immune response", "Stop digestion", "Increase body temperature", "Remove all cells"], "Train the immune response"),
            ]
        },
        "Bioenergetics": {
            "notes": [
                "Photosynthesis transfers light energy into chemical energy stored in glucose.",
                "The word equation is carbon dioxide + water → glucose + oxygen.",
                "Chlorophyll absorbs light energy.",
                "Aerobic respiration releases energy from glucose using oxygen."
            ],
            "questions": [
                ("Which gas is needed for photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "Carbon dioxide"),
                ("Where is chlorophyll found?", ["Chloroplasts", "Nuclei", "Ribosomes", "Vacuoles"], "Chloroplasts"),
                ("Which gas is produced by photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Methane"], "Oxygen"),
            ]
        },
        "Homeostasis": {
            "notes": [
                "Homeostasis means maintaining stable internal conditions.",
                "The nervous system coordinates rapid responses.",
                "Hormones are chemical messengers carried in the blood.",
                "The endocrine system controls slower, longer-lasting responses."
            ],
            "questions": [
                ("What does homeostasis mean?", ["Stable internal conditions", "Cell division", "Energy release", "Digestion"], "Stable internal conditions"),
            ]
        },
        "Inheritance": {
            "notes": [
                "DNA contains genetic information.",
                "Genes are sections of DNA.",
                "Alleles are different versions of a gene.",
                "Genetic information is passed from parents to offspring."
            ],
            "questions": [
                ("Where is genetic information stored?", ["DNA", "Starch", "Fat", "Water"], "DNA"),
                ("Different versions of a gene are called...", ["Alleles", "Organs", "Enzymes", "Tissues"], "Alleles"),
            ]
        },
        "Ecology": {
            "notes": [
                "An ecosystem contains organisms and the physical environment they interact with.",
                "Food chains show how energy moves through organisms.",
                "Producers usually make food using photosynthesis.",
                "Biodiversity means the variety of living organisms."
            ],
            "questions": [
                ("What is usually the first trophic level?", ["Producer", "Primary consumer", "Secondary consumer", "Decomposer"], "Producer"),
                ("What does biodiversity mean?", ["Variety of living organisms", "Amount of rainfall", "Number of rocks", "Soil temperature"], "Variety of living organisms"),
            ]
        }
    },

    "Chemistry": {
        "Atomic Structure": {
            "notes": [
                "Atoms contain protons, neutrons and electrons.",
                "Protons have a positive charge, neutrons have no charge and electrons have a negative charge.",
                "Atomic number is the number of protons.",
                "Mass number is protons plus neutrons."
            ],
            "questions": [
                ("What charge does a proton have?", ["+1", "0", "-1", "+2"], "+1"),
                ("Atomic number equals the number of...", ["protons", "neutrons", "electrons + neutrons", "atoms"], "protons"),
                ("Which particle has no charge?", ["Proton", "Electron", "Neutron", "Ion"], "Neutron"),
            ]
        },
        "Periodic Table": {
            "notes": [
                "Elements are arranged by atomic number.",
                "Elements in the same group have similar properties.",
                "Group 1 contains reactive metals.",
                "Group 0 contains the noble gases."
            ],
            "questions": [
                ("The periodic table is arranged by increasing...", ["atomic number", "density", "melting point", "mass only"], "atomic number"),
                ("Which group contains noble gases?", ["Group 1", "Group 2", "Group 7", "Group 0"], "Group 0"),
            ]
        },
        "Bonding": {
            "notes": [
                "Ionic bonding involves transfer of electrons.",
                "Ionic compounds commonly form between metals and non-metals.",
                "Covalent bonding involves sharing electrons.",
                "Metallic bonding involves positive metal ions and delocalised electrons."
            ],
            "questions": [
                ("Ionic bonding commonly occurs between a...", ["metal and non-metal", "metal and metal", "two noble gases", "two metals only"], "metal and non-metal"),
                ("Covalent bonding involves...", ["sharing electrons", "sharing protons", "sharing neutrons", "losing atoms"], "sharing electrons"),
            ]
        },
        "Chemical Changes": {
            "notes": [
                "Acids have a pH below 7 and alkalis have a pH above 7.",
                "Neutralisation occurs when an acid reacts with an alkali.",
                "Electrolysis uses electricity to break down ionic substances.",
                "The reactivity series helps predict displacement reactions."
            ],
            "questions": [
                ("A solution with pH 3 is...", ["acidic", "neutral", "alkaline", "pure water"], "acidic"),
                ("Acid + alkali commonly produces...", ["salt and water", "oxygen only", "metal", "carbon"], "salt and water"),
            ]
        },
        "Energy Changes": {
            "notes": [
                "Exothermic reactions release energy to the surroundings.",
                "Endothermic reactions take in energy from the surroundings.",
                "Breaking chemical bonds requires energy.",
                "Making chemical bonds releases energy."
            ],
            "questions": [
                ("Which type of reaction releases energy?", ["Exothermic", "Endothermic", "Neutral", "Physical"], "Exothermic"),
            ]
        },
        "Quantitative Chemistry": {
            "notes": [
                "Relative formula mass is calculated by adding relative atomic masses.",
                "The mole is a unit used to measure amount of substance.",
                "Chemical equations must conserve atoms.",
                "Balanced equations contain the same number of each type of atom on both sides."
            ],
            "questions": [
                ("What must be the same on both sides of a balanced equation?", ["Number of each type of atom", "Temperature", "Colour", "Volume"], "Number of each type of atom"),
            ]
        }
    },

    "Physics": {
        "Forces": {
            "notes": [
                "A force is a push or pull that can change motion or shape.",
                "Newton's second law is F = ma.",
                "Weight is calculated using W = mg.",
                "Balanced forces give a resultant force of zero."
            ],
            "questions": [
                ("What is the equation linking force, mass and acceleration?", ["F = ma", "F = m/a", "F = a/m", "F = m+a"], "F = ma"),
                ("What is force measured in?", ["Newton", "Joule", "Watt", "Pascal"], "Newton"),
            ]
        },
        "Energy": {
            "notes": [
                "Kinetic energy is energy stored due to movement.",
                "KE = ½mv².",
                "Gravitational potential energy is GPE = mgh.",
                "Energy is measured in joules and is conserved."
            ],
            "questions": [
                ("What is the unit of energy?", ["Joule", "Newton", "Watt", "Volt"], "Joule"),
                ("Which equation gives kinetic energy?", ["½mv²", "mv", "mgh", "Fd"], "½mv²"),
            ]
        },
        "Electricity": {
            "notes": [
                "Current is the rate of flow of charge.",
                "Potential difference is energy transferred per unit charge.",
                "Resistance measures how difficult it is for current to flow.",
                "Ohm's law is V = IR for suitable components."
            ],
            "questions": [
                ("What is the equation V = IR used for?", ["Electrical circuits", "Kinetic energy", "Density", "Pressure"], "Electrical circuits"),
                ("What is current measured in?", ["Amperes", "Volts", "Ohms", "Joules"], "Amperes"),
            ]
        },
        "Waves": {
            "notes": [
                "Waves transfer energy without transferring matter overall.",
                "Transverse waves oscillate perpendicular to their direction of travel.",
                "Longitudinal waves oscillate parallel to their direction of travel.",
                "Wave speed = frequency × wavelength."
            ],
            "questions": [
                ("What is the wave equation?", ["v = fλ", "v = f/λ", "v = λ/f", "v = IR"], "v = fλ"),
                ("Sound waves are...", ["longitudinal", "transverse only", "electromagnetic", "stationary"], "longitudinal"),
            ]
        },
        "Particle Model": {
            "notes": [
                "Solids have particles in fixed positions that vibrate.",
                "Liquids contain particles that can move past each other.",
                "Gas particles are far apart and move randomly.",
                "Temperature is related to average particle kinetic energy."
            ],
            "questions": [
                ("In a solid, particles mainly...", ["vibrate in fixed positions", "move far apart", "stop existing", "float freely"], "vibrate in fixed positions"),
            ]
        },
        "Atomic Physics": {
            "notes": [
                "Atoms have a small central nucleus containing protons and neutrons.",
                "Some nuclei are unstable and undergo radioactive decay.",
                "Alpha, beta and gamma are types of nuclear radiation.",
                "Radioactivity has medical and industrial uses as well as risks."
            ],
            "questions": [
                ("Which particles are found in the nucleus?", ["Protons and neutrons", "Electrons only", "Photons only", "Electrons and neutrons"], "Protons and neutrons"),
            ]
        }
    },

    "Geography": {
        "Natural Hazards": {
            "notes": [
                "Natural hazards include tectonic hazards, weather hazards and climate-related hazards.",
                "Tropical storms form over warm oceans.",
                "Hazard management includes preparation, response, recovery and adaptation.",
                "Risk is affected by exposure and vulnerability."
            ],
            "questions": [
                ("Tropical storms need...", ["warm ocean water", "frozen oceans", "no water", "snow"], "warm ocean water"),
            ]
        },
        "The Living World": {
            "notes": [
                "Ecosystems contain living organisms and their physical environment.",
                "Tropical rainforests are hot and wet with high biodiversity.",
                "Deserts receive very little rainfall.",
                "Human activity can cause habitat loss and deforestation."
            ],
            "questions": [
                ("Which biome has high rainfall and biodiversity?", ["Tropical rainforest", "Desert", "Tundra", "Polar ice"], "Tropical rainforest"),
            ]
        },
        "Rivers": {
            "notes": [
                "Rivers shape landscapes through erosion, transportation and deposition.",
                "Upper-course rivers often have steep gradients.",
                "Meanders can develop in the middle and lower courses.",
                "Deposition happens when a river loses energy and drops sediment."
            ],
            "questions": [
                ("What process drops sediment?", ["Deposition", "Erosion", "Weathering", "Evaporation"], "Deposition"),
                ("What process wears away rock?", ["Erosion", "Condensation", "Deposition", "Infiltration"], "Erosion"),
            ]
        },
        "Coasts": {
            "notes": [
                "Coasts are shaped by erosion, transportation and deposition.",
                "Constructive waves generally have stronger swash than backwash.",
                "Destructive waves generally have stronger backwash.",
                "Management strategies include hard and soft engineering."
            ],
            "questions": [
                ("Which process wears away the coastline?", ["Erosion", "Deposition", "Condensation", "Precipitation"], "Erosion"),
            ]
        },
        "Urban Issues": {
            "notes": [
                "Urbanisation is the growth in the proportion of people living in urban areas.",
                "Rapid urban growth can put pressure on housing, transport and services.",
                "Urban regeneration aims to improve places socially, economically and environmentally.",
                "Sustainable planning considers both present and future needs."
            ],
            "questions": [
                ("Urbanisation is...", ["growth of urban populations", "growth of forests", "river movement", "decline of cities"], "growth of urban populations"),
            ]
        },
        "Climate Change": {
            "notes": [
                "The enhanced greenhouse effect is linked to increased greenhouse gases.",
                "Carbon dioxide and methane are important greenhouse gases.",
                "Climate change can affect sea levels, ecosystems and agriculture.",
                "Mitigation reduces causes while adaptation prepares for impacts."
            ],
            "questions": [
                ("Which is a greenhouse gas?", ["Carbon dioxide", "Oxygen", "Argon", "Helium"], "Carbon dioxide"),
            ]
        }
    },

    "History": {
        "Medicine Through Time": {
            "notes": [
                "Ideas about disease changed as observation, science and technology developed.",
                "Louis Pasteur provided evidence supporting germ theory.",
                "Edward Jenner developed an early vaccination against smallpox.",
                "Public health improvements included sanitation and clean water."
            ],
            "questions": [
                ("Who developed an early smallpox vaccination?", ["Edward Jenner", "Louis Pasteur", "Isaac Newton", "Charles Darwin"], "Edward Jenner"),
                ("Who is strongly associated with germ theory?", ["Louis Pasteur", "Edward Jenner", "Galileo", "Newton"], "Louis Pasteur"),
            ]
        },
        "Elizabethan England": {
            "notes": [
                "Elizabeth I ruled England from 1558 to 1603.",
                "Her reign included religious tensions and threats from abroad.",
                "The Spanish Armada was defeated in 1588.",
                "Elizabethan society was strongly hierarchical."
            ],
            "questions": [
                ("When did Elizabeth I become queen?", ["1558", "1603", "1588", "1509"], "1558"),
                ("The Spanish Armada was defeated in...", ["1588", "1603", "1558", "1642"], "1588"),
            ]
        },
        "Conflict & Tension": {
            "notes": [
                "Conflicts can have political, economic, social and ideological causes.",
                "Treaties can change borders and political relationships.",
                "Historians use sources to investigate causes and consequences.",
                "Evidence and interpretation should be kept distinct."
            ],
            "questions": [
                ("Which can be a historical cause?", ["Political factors", "Magic", "Random events only", "Nothing"], "Political factors"),
            ]
        },
        "Power & the People": {
            "notes": [
                "Political rights and representation have changed over time.",
                "Reform movements have campaigned for changes to political and social systems.",
                "Change can happen through legislation, protest or conflict.",
                "Different historical interpretations can use the same evidence differently."
            ],
            "questions": [
                ("Political representation relates to...", ["having a voice in government", "weather", "river erosion", "crop growth"], "having a voice in government"),
            ]
        }
    },

    "Computer Science": {
        "Programming": {
            "notes": [
                "Variables store values used by programs.",
                "Selection lets programs make decisions using conditions.",
                "Iteration repeats instructions using loops.",
                "Algorithms should be clear, correct and efficient."
            ],
            "questions": [
                ("What does a variable store?", ["A value", "Electricity", "A monitor", "A keyboard"], "A value"),
                ("What does a loop usually do?", ["Repeats instructions", "Deletes code", "Turns off a computer", "Prints electricity"], "Repeats instructions"),
            ]
        },
        "Algorithms": {
            "notes": [
                "An algorithm is a sequence of instructions for solving a problem.",
                "Flowcharts can represent processes and decisions.",
                "Searching and sorting are common algorithmic tasks.",
                "Efficiency can involve considering time and memory."
            ],
            "questions": [
                ("What is an algorithm?", ["A sequence of instructions", "A monitor", "A cable", "A password"], "A sequence of instructions"),
            ]
        },
        "Data Representation": {
            "notes": [
                "Computers represent data using binary.",
                "One byte contains 8 bits.",
                "Images can be represented using pixels.",
                "Sound can be digitised by sampling an analogue signal."
            ],
            "questions": [
                ("How many bits are in one byte?", ["4", "8", "16", "32"], "8"),
            ]
        },
        "Computer Systems": {
            "notes": [
                "The CPU processes instructions.",
                "RAM is volatile working memory.",
                "Storage retains data when the power is off.",
                "Operating systems manage hardware and provide services to applications."
            ],
            "questions": [
                ("What does RAM provide?", ["Temporary working memory", "Permanent paper storage", "Power", "Internet"], "Temporary working memory"),
            ]
        },
        "Networks": {
            "notes": [
                "A LAN covers a relatively small area such as a school.",
                "A WAN covers a much larger geographical area.",
                "Routers forward data between networks.",
                "Protocols are agreed rules for communication."
            ],
            "questions": [
                ("What does LAN stand for?", ["Local Area Network", "Large Access Node", "Linked Application Network", "Local Algorithm Number"], "Local Area Network"),
            ]
        },
        "Cyber Security": {
            "notes": [
                "Cyber security protects systems, networks and data.",
                "Malware includes viruses, worms, ransomware and spyware.",
                "Strong authentication can reduce security risks.",
                "Phishing attempts to trick users into revealing information."
            ],
            "questions": [
                ("What is phishing?", ["A deceptive attempt to obtain information", "A monitor", "A sorting algorithm", "A storage device"], "A deceptive attempt to obtain information"),
            ]
        }
    },

    "English Language": {
        "Language Techniques": {
            "notes": [
                "A metaphor describes something as if it were something else.",
                "Personification gives human qualities to non-human things.",
                "A simile commonly compares using 'like' or 'as'.",
                "Always explain the effect and meaning of a writer's language choices."
            ],
            "questions": [
                ("Which technique gives human qualities to non-human things?", ["Personification", "Alliteration", "Rhyme", "Dialogue"], "Personification"),
                ("A direct comparison without 'like' or 'as' is a...", ["metaphor", "simile", "question", "fact"], "metaphor"),
            ]
        },
        "Structure": {
            "notes": [
                "Structure means how a text is organised.",
                "Writers can change focus, pace and the order information is revealed.",
                "Openings can establish setting, character or conflict.",
                "Endings can resolve or challenge ideas introduced earlier."
            ],
            "questions": [
                ("Structure mainly refers to...", ["how a text is organised", "spelling", "font", "handwriting"], "how a text is organised"),
            ]
        },
        "Creative Writing": {
            "notes": [
                "Good descriptive writing uses precise vocabulary and controlled sentences.",
                "Vary sentence lengths to control pace and emphasis.",
                "Use sensory detail where it adds meaning.",
                "Plan a clear beginning, development and ending."
            ],
            "questions": [
                ("What can help control pace?", ["Sentence length", "Font", "Paper size", "Page colour"], "Sentence length"),
            ]
        },
        "Reading Skills": {
            "notes": [
                "Inference means working out ideas from evidence.",
                "Use short quotations and analyse specific words.",
                "Compare texts using similarities and differences.",
                "Support interpretations with evidence."
            ],
            "questions": [
                ("What is inference?", ["Working out an idea from evidence", "Copying a sentence", "Counting words", "Changing font"], "Working out an idea from evidence"),
            ]
        }
    },

    "English Literature": {
        "Shakespeare": {
            "notes": [
                "Analyse Shakespeare through character, theme, language, structure and context.",
                "Context should support your interpretation rather than replace textual analysis.",
                "Consider what characters say, do and how others respond.",
                "Track how themes develop throughout the play."
            ],
            "questions": [
                ("What should context do?", ["Support an interpretation", "Replace evidence", "Ignore the text", "Replace analysis"], "Support an interpretation"),
            ]
        },
        "19th-Century Novel": {
            "notes": [
                "19th-century novels can explore class, poverty, education and social change.",
                "Analyse the writer's choices and connect them to characters and themes.",
                "Use evidence, methods and interpretation together.",
                "Context is most useful when it helps explain a writer's choices."
            ],
            "questions": [
                ("What should you do with a quotation?", ["Explain its meaning and the writer's choices", "Copy it only", "Ignore it", "Count its words"], "Explain its meaning and the writer's choices"),
            ]
        },
        "Poetry": {
            "notes": [
                "Poetry can be analysed through language, structure, form and sound.",
                "Consider why the poet chose particular words and images.",
                "Compare poems through ideas and methods.",
                "Explain why similarities or differences are significant."
            ],
            "questions": [
                ("Which can be analysed in poetry?", ["Language and structure", "Only punctuation", "Only titles", "Only line length"], "Language and structure"),
            ]
        },
        "Modern Texts": {
            "notes": [
                "Modern texts can explore identity, relationships, conflict and power.",
                "Track character and theme development across the whole text.",
                "Use precise evidence and explain its significance.",
                "Consider alternative interpretations where appropriate."
            ],
            "questions": [
                ("What should you track across a whole text?", ["Character and theme development", "Only the first page", "Only punctuation", "Only titles"], "Character and theme development"),
            ]
        }
    }
}


YEARS = ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            premium INTEGER NOT NULL DEFAULT 0,
            year_level TEXT NOT NULL DEFAULT 'Year 10'
        );

        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT DEFAULT '',
            topic TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY(deck_id) REFERENCES decks(id)
        );
    """)

    conn.commit()
    conn.close()


def get_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    return user


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not get_user():
            return jsonify({"error": "Please log in first."}), 401

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# HELPERS
# ============================================================

def create_test(subject, topic, difficulty):
    topic_data = SUBJECTS[subject][topic]

    questions = list(topic_data["questions"])

    random.shuffle(questions)

    questions = questions[:5]

    output = []

    for number, question in enumerate(questions, start=1):
        text, options, answer = question

        options = list(options)
        random.shuffle(options)

        output.append({
            "id": number,
            "question": text,
            "options": options,
            "answer": answer
        })

    return output


# ============================================================
# API
# ============================================================

@app.get("/api/me")
def me():
    user = get_user()

    if not user:
        return jsonify({"logged_in": False})

    return jsonify({
        "logged_in": True,
        "username": user["username"],
        "premium": bool(user["premium"]),
        "year": user["year_level"]
    })


@app.post("/api/register")
def register():
    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    year = data.get("year", "Year 10")

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if year not in YEARS:
        year = "Year 10"

    conn = get_db()

    try:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password, year_level)
            VALUES (?, ?, ?)
            """,
            (
                username,
                generate_password_hash(password),
                year
            )
        )

        conn.commit()

        user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "That username is already taken."
        }), 409

    conn.close()

    session["user_id"] = user_id

    return jsonify({"success": True})


@app.post("/api/login")
def login():
    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({
            "error": "Incorrect username or password."
        }), 401

    session["user_id"] = user["id"]

    return jsonify({"success": True})


@app.post("/api/logout")
def logout():
    session.clear()

    return jsonify({"success": True})


@app.get("/api/subjects")
def subjects():
    return jsonify({
        "subjects": list(SUBJECTS.keys()),
        "years": YEARS,
        "difficulties": DIFFICULTIES
    })


@app.get("/api/topics/<path:subject>")
def topics(subject):
    if subject not in SUBJECTS:
        return jsonify({"error": "Subject not found."}), 404

    result = []

    for topic, data in SUBJECTS[subject].items():
        result.append({
            "topic": topic,
            "questions": len(data["questions"])
        })

    return jsonify({
        "subject": subject,
        "topics": result
    })


@app.post("/api/start-test")
def start_test():
    data = request.get_json() or {}

    subject = data.get("subject")
    topic = data.get("topic")
    difficulty = data.get("difficulty", "Medium")

    if subject not in SUBJECTS:
        return jsonify({"error": "Subject not found."}), 404

    if topic not in SUBJECTS[subject]:
        return jsonify({"error": "Topic not found."}), 404

    if difficulty not in DIFFICULTIES:
        difficulty = "Medium"

    questions = create_test(subject, topic, difficulty)

    session["current_test"] = {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "questions": questions
    }

    safe_questions = []

    for question in questions:
        safe_questions.append({
            "id": question["id"],
            "question": question["question"],
            "options": question["options"]
        })

    return jsonify({
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "questions": safe_questions
    })


@app.post("/api/submit-test")
def submit_test():
    test = session.get("current_test")

    if not test:
        return jsonify({
            "error": "There is no active test."
        }), 400

    data = request.get_json() or {}
    answers = data.get("answers", {})

    score = 0
    results = []

    for question in test["questions"]:

        selected = answers.get(str(question["id"]))
        correct_answer = question["answer"]

        correct = selected == correct_answer

        if correct:
            score += 1

        results.append({
            "id": question["id"],
            "correct": correct,
            "selected": selected,
            "answer": correct_answer
        })

    return jsonify({
        "score": score,
        "total": len(test["questions"]),
        "results": results,
        "subject": test["subject"],
        "topic": test["topic"],
        "difficulty": test["difficulty"]
    })


@app.get("/api/notes/<path:subject>/<path:topic>")
def get_notes(subject, topic):
    if subject not in SUBJECTS:
        return jsonify({"error": "Subject not found."}), 404

    if topic not in SUBJECTS[subject]:
        return jsonify({"error": "Topic not found."}), 404

    return jsonify({
        "subject": subject,
        "topic": topic,
        "notes": SUBJECTS[subject][topic]["notes"]
    })


# ============================================================
# FLASHCARDS
# ============================================================

@app.get("/api/decks")
@login_required
def get_decks():
    user = get_user()

    conn = get_db()

    decks = conn.execute(
        """
        SELECT
            d.id,
            d.name,
            d.subject,
            d.topic,
            COUNT(f.id) AS cards
        FROM decks d
        LEFT JOIN flashcards f
            ON f.deck_id = d.id
        WHERE d.user_id = ?
        GROUP BY d.id
        ORDER BY d.id DESC
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    return jsonify({
        "decks": [dict(deck) for deck in decks]
    })


@app.post("/api/decks")
@login_required
def create_deck():
    user = get_user()
    data = request.get_json() or {}

    name = str(data.get("name", "")).strip()
    subject = str(data.get("subject", "")).strip()
    topic = str(data.get("topic", "")).strip()

    if not name:
        return jsonify({
            "error": "Enter a deck name."
        }), 400

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO decks
        (user_id, name, subject, topic)
        VALUES (?, ?, ?, ?)
        """,
        (
            user["id"],
            name,
            subject,
            topic
        )
    )

    conn.commit()

    deck_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "id": deck_id
    })


@app.delete("/api/decks/<int:deck_id>")
@login_required
def delete_deck(deck_id):
    user = get_user()

    conn = get_db()

    deck = conn.execute(
        """
        SELECT *
        FROM decks
        WHERE id = ?
        AND user_id = ?
        """,
        (deck_id, user["id"])
    ).fetchone()

    if not deck:
        conn.close()

        return jsonify({
            "error": "Deck not found."
        }), 404

    conn.execute(
        "DELETE FROM flashcards WHERE deck_id = ?",
        (deck_id,)
    )

    conn.execute(
        "DELETE FROM decks WHERE id = ?",
        (deck_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.get("/api/decks/<int:deck_id>/cards")
@login_required
def get_cards(deck_id):
    user = get_user()

    conn = get_db()

    deck = conn.execute(
        """
        SELECT *
        FROM decks
        WHERE id = ?
        AND user_id = ?
        """,
        (deck_id, user["id"])
    ).fetchone()

    if not deck:
        conn.close()

        return jsonify({
            "error": "Deck not found."
        }), 404

    cards = conn.execute(
        """
        SELECT id, question, answer
        FROM flashcards
        WHERE deck_id = ?
        ORDER BY id
        """,
        (deck_id,)
    ).fetchall()

    conn.close()

    return jsonify({
        "deck": dict(deck),
        "cards": [dict(card) for card in cards]
    })


@app.post("/api/flashcards")
@login_required
def add_flashcard():
    user = get_user()

    data = request.get_json() or {}

    deck_id = data.get("deck_id")
    question = str(data.get("question", "")).strip()
    answer = str(data.get("answer", "")).strip()

    if not deck_id or not question or not answer:
        return jsonify({
            "error": "Fill in all flashcard fields."
        }), 400

    conn = get_db()

    deck = conn.execute(
        """
        SELECT id
        FROM decks
        WHERE id = ?
        AND user_id = ?
        """,
        (deck_id, user["id"])
    ).fetchone()

    if not deck:
        conn.close()

        return jsonify({
            "error": "Deck not found."
        }), 404

    cursor = conn.execute(
        """
        INSERT INTO flashcards
        (deck_id, question, answer)
        VALUES (?, ?, ?)
        """,
        (
            deck_id,
            question,
            answer
        )
    )

    conn.commit()

    card_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "id": card_id
    })


# ============================================================
# PAGE
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>
   <meta name="google-site-verification" content="6UsZCYhWi-8ryfg4oktCx2A>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Study Faster</title>

<style>

* {
    box-sizing: border-box;
}
</head>
body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    color: #ffffff;

    background:
        radial-gradient(
            circle at 20% 0%,
            #302267 0%,
            #111528 35%,
            #080a12 70%
        );

    min-height: 100vh;
}

button,
input,
select {
    font: inherit;
}

button {
    cursor: pointer;
}

.hidden {
    display: none !important;
}


/* ============================================================
   TOP BAR
============================================================ */

.topbar {

    position: sticky;
    top: 0;
    z-index: 100;

    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 18px 30px;

    background: rgba(8, 10, 18, 0.90);

    backdrop-filter: blur(15px);

    border-bottom: 1px solid #242a3d;
}

.logo {

    font-size: 23px;

    font-weight: 900;

    letter-spacing: -0.8px;
}

.logo span {
    color: #8068ff;
}

.nav {
    display: flex;
    gap: 8px;
}

.nav button {

    background: transparent;

    color: white;

    border: 1px solid #2a3045;

    border-radius: 10px;

    padding: 9px 13px;
}

.nav button:hover {
    background: #171b2c;
}


/* ============================================================
   LAYOUT
============================================================ */

.container {

    width: min(1150px, calc(100% - 30px));

    margin: auto;

    padding: 35px 0 80px;
}


/* ============================================================
   CARDS
============================================================ */

.card {

    background: rgba(17, 22, 36, 0.94);

    border: 1px solid #272e43;

    border-radius: 20px;

    padding: 25px;

    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.25);

    margin-bottom: 20px;
}


/* ============================================================
   TITLE / HERO BACKGROUND
============================================================ */

.hero {

    padding: 55px 45px;

    border-radius: 25px;

    margin-bottom: 22px;

    background:
        radial-gradient(
            circle at 85% 15%,
            rgba(128, 104, 255, 0.30),
            transparent 35%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(77, 105, 255, 0.20),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #17182f,
            #0d1220
        );

    border: 1px solid #2e3450;

    overflow: hidden;
}

.hero h1 {

    font-size: clamp(40px, 7vw, 70px);

    line-height: 0.95;

    margin: 18px 0;

    letter-spacing: -3px;
}

.hero h1 span {
    color: #8973ff;
}

.hero p {

    max-width: 650px;

    color: #aab3c7;

    font-size: 17px;

    line-height: 1.7;
}


/* ============================================================
   BUTTONS
============================================================ */

.primary {

    border: none;

    color: white;

    font-weight: 800;

    padding: 12px 17px;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            #8068ff,
            #526fff
        );

    box-shadow:
        0 8px 25px rgba(101, 82, 255, 0.25);
}

.primary:hover {
    transform: translateY(-1px);
}

.secondary {

    background: transparent;

    color: white;

    border: 1px solid #30374e;

    padding: 11px 15px;

    border-radius: 12px;
}


/* ============================================================
   BADGES
============================================================ */

.badge {

    display: inline-block;

    padding: 6px 10px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 900;

    letter-spacing: .5px;

    background: #191532;

    color: #aa9dff;

    border: 1px solid #40377a;
}

.coming {

    margin-left: 7px;

    color: #ffd76a;

    background: #302817;

    border: 1px solid #655225;

    border-radius: 999px;

    padding: 4px 7px;

    font-size: 10px;
}


/* ============================================================
   GRIDS
============================================================ */

.grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 13px;
}

.topic-card {

    padding: 18px;

    background: #0d121e;

    border: 1px solid #283046;

    border-radius: 15px;

    cursor: pointer;

    transition: .15s;
}

.topic-card:hover {

    transform: translateY(-2px);

    border-color: #6959d4;

    background: #111728;
}

.topic-card h3 {
    margin: 0 0 7px;
}

.small {
    color: #8994aa;
    font-size: 13px;
}


/* ============================================================
   CONTROLS
============================================================ */

.controls {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 12px;

    margin: 20px 0;
}

label {

    display: block;

    color: #919cb1;

    font-size: 13px;

    margin-bottom: 7px;
}

input,
select {

    width: 100%;

    background: #0a0f19;

    color: white;

    border: 1px solid #293146;

    padding: 12px;

    border-radius: 11px;

    outline: none;
}

input:focus,
select:focus {
    border-color: #7965ee;
}


/* ============================================================
   TEST
============================================================ */

.question {

    padding: 19px;

    margin-bottom: 13px;

    background: #0b1019;

    border: 1px solid #293146;

    border-radius: 15px;
}

.question-title {

    font-weight: 800;

    line-height: 1.5;
}

.answers {

    display: grid;

    gap: 8px;

    margin-top: 13px;
}

.answer {

    text-align: left;

    background: #121927;

    color: white;

    border: 1px solid #293146;

    padding: 12px;

    border-radius: 10px;
}

.answer.selected {
    border-color: #8068ff;
    background: #211c48;
}

.answer.correct {
    border-color: #36d399;
    background: #102d25;
}

.answer.wrong {
    border-color: #ff6078;
    background: #351721;
}

.result {

    padding: 20px;

    border-radius: 15px;

    background: #0c131f;

    border: 1px solid #293146;

    margin-top: 18px;
}


/* ============================================================
   NOTES
============================================================ */

.notes {

    display: grid;

    gap: 12px;
}

.note {

    padding: 18px;

    background: #0d131f;

    border-left: 3px solid #8068ff;

    border-radius: 10px;

    line-height: 1.7;

    color: #dce3ef;
}


/* ============================================================
   FLASHCARDS
============================================================ */

.flashcard {

    min-height: 230px;

    display: grid;

    place-items: center;

    text-align: center;

    padding: 30px;

    background: #0a101a;

    border: 1px solid #293146;

    border-radius: 20px;

    font-size: 27px;

    font-weight: 800;
}


/* ============================================================
   PREMIUM
============================================================ */

.premium {

    background:
        radial-gradient(
            circle at top right,
            rgba(128,104,255,.2),
            transparent 40%
        ),
        #111525;

    border-color: #5143a0;
}


/* ============================================================
   AUTH
============================================================ */

.auth {

    min-height: 100vh;

    display: grid;

    place-items: center;

    padding: 20px;
}

.auth-box {

    width: min(430px, 100%);
}

.form {

    display: grid;

    gap: 11px;
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media(max-width: 800px) {

    .grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .controls {
        grid-template-columns: 1fr;
    }

    .hero {
        padding: 40px 25px;
    }
}

@media(max-width: 550px) {

    .topbar {
        padding: 14px;
    }

    .nav button {
        padding: 8px;
        font-size: 12px;
    }

    .container {
        width: min(100% - 20px, 1150px);
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .hero h1 {
        font-size: 45px;
    }
}

</style>

</head>

<body>


<!-- ============================================================
     LOGIN
============================================================ -->

<div id="authScreen" class="auth">

    <div class="card auth-box">

        <div class="logo">
            Study <span>Faster</span>
        </div>

        <h2 style="margin-top:25px">
            Welcome back
        </h2>

        <p class="small">
            Log in or create your revision account.
        </p>


        <div class="form">

            <input
                id="username"
                placeholder="Username"
            >

            <input
                id="password"
                type="password"
                placeholder="Password"
            >

            <select id="year">

                <option>Year 7</option>
                <option>Year 8</option>
                <option>Year 9</option>
                <option selected>Year 10</option>
                <option>Year 11</option>

            </select>

            <button
                class="primary"
                onclick="register()"
            >
                Create account
            </button>

            <button
                class="secondary"
                onclick="login()"
            >
                Log in
            </button>

        </div>

        <div id="authMessage"></div>

    </div>

</div>


<!-- ============================================================
     APP
============================================================ -->

<div id="app" class="hidden">


<header class="topbar">

    <div class="logo">
        Study <span>Faster</span>
    </div>

    <div class="nav">

        <button onclick="showPage('home')">
            Home
        </button>

        <button onclick="showPage('learn')">
            Learn
        </button>

        <button onclick="showPage('flashcards')">
            Flashcards
        </button>

        <button onclick="showPage('premium')">
            Premium
        </button>

        <button onclick="logout()">
            Log out
        </button>

    </div>

</header>


<main class="container">


<!-- ============================================================
     HOME
============================================================ -->

<section id="homePage">


<div class="hero">

    <span class="badge">
        GCSE REVISION
    </span>

    <h1>
        Study smarter.<br>
        <span>Learn faster.</span>
    </h1>

    <p>
        Choose your year, pick a difficulty, select a topic,
        take a quick mini test and then get focused notes
        explaining the topic.
    </p>

    <button
        class="primary"
        onclick="showPage('learn')"
    >
        Start revising
    </button>

</div>


<div class="card">

    <h2>
        Your revision settings
    </h2>

    <div class="controls">

        <div>

            <label>
                Year
            </label>

            <select id="homeYear">

                <option>Year 7</option>
                <option>Year 8</option>
                <option>Year 9</option>
                <option selected>Year 10</option>
                <option>Year 11</option>

            </select>

        </div>


        <div>

            <label>
                Difficulty
            </label>

            <select id="homeDifficulty">

                <option>Easy</option>
                <option selected>Medium</option>
                <option>Hard</option>

            </select>

        </div>


        <div>

            <label>
                Action
            </label>

            <button
                class="primary"
                style="width:100%"
                onclick="showPage('learn')"
            >
                Choose topic
            </button>

        </div>

    </div>

</div>


<div class="card">

    <h2>
        Subjects
    </h2>

    <p class="small">
        Choose a subject to see all available topics.
    </p>

    <div
        id="subjectGrid"
        class="grid"
    ></div>

</div>


</section>


<!-- ============================================================
     LEARN
============================================================ -->

<section
    id="learnPage"
    class="hidden"
>

<div class="card">

    <span class="badge">
        LEARN
    </span>

    <h2 style="margin-top:12px">
        Choose your topic
    </h2>

    <p class="small">
        Pick a subject, year and difficulty.
        Then take a five-question mini test.
    </p>


    <div class="controls">


        <div>

            <label>
                Year
            </label>

            <select id="learnYear">

                <option>Year 7</option>
                <option>Year 8</option>
                <option>Year 9</option>
                <option selected>Year 10</option>
                <option>Year 11</option>

            </select>

        </div>


        <div>

            <label>
                Difficulty
            </label>

            <select id="learnDifficulty">

                <option>Easy</option>
                <option selected>Medium</option>
                <option>Hard</option>

            </select>

        </div>


        <div>

            <label>
                Subject
            </label>

            <select
                id="subjectSelect"
                onchange="loadTopics()"
            ></select>

        </div>


    </div>


    <div
        id="topicGrid"
        class="grid"
    ></div>

</div>

</section>


<!-- ============================================================
     TEST
============================================================ -->

<section
    id="testPage"
    class="hidden"
>

<div class="card">

    <span class="badge">
        MINI TEST
    </span>

    <h2
        id="testTitle"
        style="margin-top:12px"
    ></h2>

    <p
        id="testInfo"
        class="small"
    ></p>


    <div
        id="questions"
    ></div>


    <button
        id="submitButton"
        class="primary"
        onclick="submitTest()"
    >
        Submit test
    </button>


    <div
        id="testResult"
    ></div>

</div>

</section>


<!-- ============================================================
     NOTES
============================================================ -->

<section
    id="notesPage"
    class="hidden"
>

<div class="card">

    <span class="badge">
        TOPIC NOTES
    </span>

    <h2
        id="notesTitle"
        style="margin-top:12px"
    ></h2>

    <p
        id="notesSubject"
        class="small"
    ></p>


    <div
        id="notes"
        class="notes"
    ></div>


    <div style="
        display:flex;
        gap:10px;
        margin-top:20px;
        flex-wrap:wrap;
    ">

        <button
            class="primary"
            onclick="retryTest()"
        >
            Retry mini test
        </button>

        <button
            class="secondary"
            onclick="showPage('flashcards')"
        >
            Flashcards
        </button>

    </div>

</div>

</section>


<!-- ============================================================
     FLASHCARDS
============================================================ -->

<section
    id="flashcardsPage"
    class="hidden"
>

<div class="card">

    <span class="badge">
        FLASHCARDS
    </span>

    <h2 style="margin-top:12px">
        Your decks
    </h2>

    <p class="small">
        Create unlimited decks and flashcards.
    </p>


    <div class="controls">

        <input
            id="deckName"
            placeholder="Deck name"
        >

        <input
            id="deckSubject"
            placeholder="Subject"
        >

        <input
            id="deckTopic"
            placeholder="Topic"
        >

    </div>


    <button
        class="primary"
        onclick="createDeck()"
    >
        Create deck
    </button>


    <div
        id="decks"
        class="grid"
        style="margin-top:20px"
    ></div>

</div>


<div class="card">

    <h3>
        Add flashcard
    </h3>


    <div class="controls">

        <select id="cardDeck"></select>

        <input
            id="cardQuestion"
            placeholder="Question"
        >

        <input
            id="cardAnswer"
            placeholder="Answer"
        >

    </div>


    <button
        class="primary"
        onclick="addCard()"
    >
        Add flashcard
    </button>

</div>


<div
    id="studyCard"
    class="card hidden"
>

    <span class="badge">
        FLIP STUDY
    </span>

    <h2
        id="studyTitle"
        style="margin-top:12px"
    ></h2>


    <div
        id="flashcard"
        class="flashcard"
    ></div>


    <div style="
        display:flex;
        justify-content:center;
        gap:10px;
        margin-top:15px;
    ">

        <button
            class="primary"
            onclick="flipCard()"
        >
            Flip
        </button>

        <button
            class="secondary"
            onclick="nextCard()"
        >
            Next
        </button>

    </div>


    <p
        id="cardNumber"
        class="small"
        style="text-align:center"
    ></p>

</div>

</section>


<!-- ============================================================
     PREMIUM
============================================================ -->

<section
    id="premiumPage"
    class="hidden"
>

<div class="card premium">

    <span class="badge">
        PREMIUM
    </span>

    <h1 style="
        font-size:42px;
        margin-top:18px;
    ">
        Coming Soon
        <span class="coming">
            COMING SOON
        </span>
    </h1>

    <p>
        Premium will add extra AI-powered revision tools.
    </p>


    <div class="notes">

        <div class="note">

            <strong>
                AI Questions
            </strong>

            <br>

            Generate extra practice questions
            for your chosen topic.

        </div>


        <div class="note">

            <strong>
                AI Explanations
            </strong>

            <br>

            Get extra explanations when you need
            another way of understanding a topic.

        </div>


        <div class="note">

            <strong>
                More revision tools
            </strong>

            <br>

            More Premium features can be added here later.

        </div>

    </div>


    <p style="margin-top:20px">

        <strong>
            No payment is being taken yet.
        </strong>

        Premium is currently coming soon.

    </p>

</div>

</section>


</main>

</div>


<script>

let currentSubject = "";
let currentTopic = "";
let currentDifficulty = "Medium";

let currentTest = null;

let currentCards = [];
let currentCard = 0;
let showingAnswer = false;


/* ============================================================
   API
============================================================ */

async function api(url, options = {}) {

    const response = await fetch(url, {
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || "Something went wrong."
        );
    }

    return data;
}


/* ============================================================
   AUTH
============================================================ */

async function register() {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;

    const year =
        document.getElementById("year").value;


    try {

        await api("/api/register", {

            method: "POST",

            body: JSON.stringify({
                username,
                password,
                year
            })

        });

        enterApp();

    } catch (error) {

        document.getElementById(
            "authMessage"
        ).innerHTML =
            `<p style="color:#ff647c">${error.message}</p>`;

    }
}


async function login() {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;


    try {

        await api("/api/login", {

            method: "POST",

            body: JSON.stringify({
                username,
                password
            })

        });

        enterApp();

    } catch (error) {

        document.getElementById(
            "authMessage"
        ).innerHTML =
            `<p style="color:#ff647c">${error.message}</p>`;

    }
}


async function logout() {

    await api("/api/logout", {
        method: "POST"
    });

    location.reload();
}


async function checkLogin() {

    const user = await api("/api/me");

    if (user.logged_in) {

        enterApp(user);

    }

}


async function enterApp(user = null) {

    document
        .getElementById("authScreen")
        .classList.add("hidden");

    document
        .getElementById("app")
        .classList.remove("hidden");


    if (user) {

        document.getElementById(
            "homeYear"
        ).value = user.year;

        document.getElementById(
            "learnYear"
        ).value = user.year;

    }


    await loadSubjects();

}


/* ============================================================
   PAGES
============================================================ */

function showPage(page) {

    const pages = [
        "home",
        "learn",
        "test",
        "notes",
        "flashcards",
        "premium"
    ];


    pages.forEach(name => {

        document
            .getElementById(name + "Page")
            .classList.add("hidden");

    });


    document
        .getElementById(page + "Page")
        .classList.remove("hidden");


    if (page === "learn") {

        loadTopics();

    }


    if (page === "flashcards") {

        loadDecks();

    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* ============================================================
   SUBJECTS
============================================================ */

async function loadSubjects() {

    const data =
        await api("/api/subjects");


    const grid =
        document.getElementById("subjectGrid");


    grid.innerHTML =
        data.subjects.map(subject => `

            <div
                class="topic-card"
                onclick="chooseSubject('${escapeAttr(subject)}')"
            >

                <h3>
                    ${escapeHtml(subject)}
                </h3>

                <div class="small">
                    Click to see all topics
                </div>

            </div>

        `).join("");


    const select =
        document.getElementById("subjectSelect");


    select.innerHTML =
        data.subjects.map(subject => `

            <option value="${escapeAttr(subject)}">
                ${escapeHtml(subject)}
            </option>

        `).join("");


    await loadTopics();

}


function chooseSubject(subject) {

    document.getElementById(
        "subjectSelect"
    ).value = subject;

    showPage("learn");

}


/* ============================================================
   TOPICS
============================================================ */

async function loadTopics() {

    const subject =
        document.getElementById(
            "subjectSelect"
        ).value;


    if (!subject) return;


    const data =
        await api(
            "/api/topics/" +
            encodeURIComponent(subject)
        );


    const grid =
        document.getElementById("topicGrid");


    grid.innerHTML =
        data.topics.map(topic => `

            <div
                class="topic-card"
                onclick="startTest('${escapeAttr(subject)}','${escapeAttr(topic.topic)}')"
            >

                <h3>
                    ${escapeHtml(topic.topic)}
                </h3>

                <div class="small">
                    Mini test + topic notes
                </div>

            </div>

        `).join("");

}


/* ============================================================
   MINI TEST
============================================================ */

async function startTest(subject, topic) {

    currentSubject = subject;
    currentTopic = topic;


    currentDifficulty =
        document.getElementById(
            "learnDifficulty"
        ).value;


    const data =
        await api("/api/start-test", {

            method: "POST",

            body: JSON.stringify({
                subject,
                topic,
                difficulty: currentDifficulty
            })

        });


    currentTest = data;


    document.getElementById(
        "testTitle"
    ).textContent = topic;


    document.getElementById(
        "testInfo"
    ).textContent =
        `${subject} • ${data.difficulty} • ${data.questions.length} questions`;


    const questions =
        document.getElementById("questions");


    questions.innerHTML =
        data.questions.map((question, index) => `

            <div class="question">

                <div class="question-title">

                    ${index + 1}.
                    ${escapeHtml(question.question)}

                </div>


                <div class="answers">

                    ${question.options.map(option => `

                        <button
                            class="answer"
                            data-question="${question.id}"
                            data-answer="${escapeAttr(option)}"
                            onclick="selectAnswer(this)"
                        >

                            ${escapeHtml(option)}

                        </button>

                    `).join("")}

                </div>

            </div>

        `).join("");


    document
        .getElementById("submitButton")
        .classList.remove("hidden");


    document.getElementById(
        "testResult"
    ).innerHTML = "";


    showPage("test");

}


function selectAnswer(button) {

    const question =
        button.dataset.question;


    document
        .querySelectorAll(
            `.answer[data-question="${question}"]`
        )
        .forEach(item => {

            item.classList.remove("selected");

        });


    button.classList.add("selected");

}


async function submitTest() {

    const answers = {};


    document
        .querySelectorAll(".answer.selected")
        .forEach(button => {

            answers[
                button.dataset.question
            ] = button.dataset.answer;

        });


    const result =
        await api("/api/submit-test", {

            method: "POST",

            body: JSON.stringify({
                answers
            })

        });


    document
        .getElementById("submitButton")
        .classList.add("hidden");


    result.results.forEach(item => {

        document
            .querySelectorAll(
                `.answer[data-question="${item.id}"]`
            )
            .forEach(button => {

                if (
                    button.dataset.answer ===
                    item.answer
                ) {

                    button.classList.add("correct");

                }

                if (
                    button.classList.contains("selected") &&
                    !item.correct
                ) {

                    button.classList.add("wrong");

                }

            });

    });


    let message = "Keep practising.";

    if (
        result.score === result.total
    ) {

        message =
            "Perfect score!";

    } else if (
        result.score >=
        Math.ceil(result.total * 0.6)
    ) {

        message =
            "Good work! Review the notes to strengthen it.";

    }


    document.getElementById(
        "testResult"
    ).innerHTML = `

        <div class="result">

            <h2>
                ${result.score}/${result.total}
            </h2>

            <p>
                ${message}
            </p>

            <button
                class="primary"
                onclick="openNotes()"
            >
                Read the topic notes
            </button>

        </div>

    `;

}


/* ============================================================
   NOTES
============================================================ */

async function openNotes() {

    const data =
        await api(
            "/api/notes/" +
            encodeURIComponent(currentSubject) +
            "/" +
            encodeURIComponent(currentTopic)
        );


    document.getElementById(
        "notesTitle"
    ).textContent = data.topic;


    document.getElementById(
        "notesSubject"
    ).textContent = data.subject;


    document.getElementById(
        "notes"
    ).innerHTML =
        data.notes.map((note, index) => `

            <div class="note">

                <strong>
                    ${index + 1}.
                </strong>

                ${escapeHtml(note)}

            </div>

        `).join("");


    showPage("notes");

}


function retryTest() {

    startTest(
        currentSubject,
        currentTopic
    );

}


/* ============================================================
   FLASHCARDS
============================================================ */

async function loadDecks() {

    const data =
        await api("/api/decks");


    const grid =
        document.getElementById("decks");


    const select =
        document.getElementById("cardDeck");


    if (!data.decks.length) {

        grid.innerHTML = `
            <p class="small">
                You haven't created a deck yet.
            </p>
        `;

        select.innerHTML = `
            <option>
                Create a deck first
            </option>
        `;

        return;

    }


    grid.innerHTML =
        data.decks.map(deck => `

            <div class="topic-card">

                <h3>
                    ${escapeHtml(deck.name)}
                </h3>

                <div class="small">
                    ${escapeHtml(deck.subject || "General")}
                </div>

                <div class="small">
                    ${deck.cards} cards
                </div>

                <div style="
                    margin-top:12px;
                    display:flex;
                    gap:7px;
                ">

                    <button
                        class="primary"
                        onclick="studyDeck(${deck.id})"
                    >
                        Study
                    </button>

                    <button
                        class="secondary"
                        onclick="deleteDeck(${deck.id})"
                    >
                        Delete
                    </button>

                </div>

            </div>

        `).join("");


    select.innerHTML =
        data.decks.map(deck => `

            <option value="${deck.id}">
                ${escapeHtml(deck.name)}
            </option>

        `).join("");

}


async function createDeck() {

    const name =
        document.getElementById(
            "deckName"
        ).value.trim();

    const subject =
        document.getElementById(
            "deckSubject"
        ).value.trim();

    const topic =
        document.getElementById(
            "deckTopic"
        ).value.trim();


    if (!name) {

        alert("Enter a deck name.");

        return;

    }


    await api("/api/decks", {

        method: "POST",

        body: JSON.stringify({
            name,
            subject,
            topic
        })

    });


    document.getElementById(
        "deckName"
    ).value = "";


    await loadDecks();

}


async function deleteDeck(id) {

    if (
        !confirm(
            "Delete this deck and all its flashcards?"
        )
    ) {

        return;

    }


    await api(
        "/api/decks/" + id,
        {
            method: "DELETE"
        }
    );


    loadDecks();

}


async function addCard() {

    const deck =
        document.getElementById(
            "cardDeck"
        ).value;

    const question =
        document.getElementById(
            "cardQuestion"
        ).value.trim();

    const answer =
        document.getElementById(
            "cardAnswer"
        ).value.trim();


    if (!question || !answer) {

        alert("Enter a question and answer.");

        return;

    }


    await api("/api/flashcards", {

        method: "POST",

        body: JSON.stringify({
            deck_id: deck,
            question,
            answer
        })

    });


    document.getElementById(
        "cardQuestion"
    ).value = "";

    document.getElementById(
        "cardAnswer"
    ).value = "";


    loadDecks();

}


async function studyDeck(id) {

    const data =
        await api(
            "/api/decks/" +
            id +
            "/cards"
        );


    if (!data.cards.length) {

        alert(
            "This deck doesn't have any cards yet."
        );

        return;

    }


    currentCards = data.cards;

    currentCard = 0;

    showingAnswer = false;


    document.getElementById(
        "studyTitle"
    ).textContent =
        data.deck.name;


    document
        .getElementById("studyCard")
        .classList.remove("hidden");


    renderCard();

}


function renderCard() {

    const card =
        currentCards[currentCard];


    document.getElementById(
        "flashcard"
    ).textContent =
        showingAnswer
            ? card.answer
            : card.question;


    document.getElementById(
        "cardNumber"
    ).textContent =
        `Card ${currentCard + 1} of ${currentCards.length}`;

}


function flipCard() {

    showingAnswer =
        !showingAnswer;

    renderCard();

}


function nextCard() {

    currentCard =
        (currentCard + 1) %
        currentCards.length;

    showingAnswer = false;

    renderCard();

}


/* ============================================================
   ESCAPE HTML
============================================================ */

function escapeHtml(value) {

    return String(value)

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");

}


function escapeAttr(value) {

    return escapeHtml(value);

}


/* ============================================================
   START
============================================================ */

checkLogin();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


# ============================================================
# START SERVER
# ============================================================

setup_database()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )