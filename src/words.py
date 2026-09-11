"""Auditable 256-word vocabulary for memorable passphrase generation.

Every word is neutral, familiar, ASCII-only, and distinct. A 256-word pool
provides exactly eight bits per independently selected word.
"""

WORDS = (
    "acorn", "amber", "anchor", "apple", "apron", "archer", "arrow", "atlas",
    "autumn", "badger", "bamboo", "beacon", "berry", "birch", "bison", "bloom",
    "blue", "breeze", "brick", "brook", "button", "cabin", "cactus", "camera",
    "candle", "canvas", "caramel", "castle", "cedar", "cherry", "circle", "citrus",
    "cloud", "clover", "cobalt", "coffee", "comet", "copper", "coral", "cosmos",
    "crane", "cricket", "crystal", "daisy", "delta", "denim", "dolphin", "dune",
    "eagle", "earth", "ember", "emerald", "falcon", "feather", "fern", "field",
    "finch", "flame", "forest", "fossil", "frost", "galaxy", "garden", "ginger",
    "glacier", "globe", "gold", "granite", "grape", "grove", "harbor", "hazel",
    "heron", "honey", "horizon", "indigo", "island", "ivory", "jade", "jasmine",
    "juniper", "kettle", "kiwi", "lagoon", "lantern", "lark", "laurel", "lemon",
    "linen", "lotus", "lunar", "mango", "maple", "marble", "meadow", "meteor",
    "mint", "mist", "moon", "moss", "nectar", "north", "nova", "oasis",
    "ocean", "olive", "onyx", "orbit", "orchid", "otter", "peach", "pearl",
    "pepper", "pine", "planet", "plum", "pond", "prairie", "quartz", "rain",
    "raven", "reef", "river", "robin", "rocket", "rose", "ruby", "saffron",
    "sage", "sail", "sand", "scarlet", "shadow", "shell", "silver", "sky",
    "snow", "solar", "sparrow", "spring", "spruce", "star", "stone", "storm",
    "summit", "sunset", "swift", "tangerine", "thistle", "tiger", "timber", "topaz",
    "trail", "tulip", "valley", "velvet", "violet", "willow", "wind", "winter",
    "wren", "zephyr", "acoustic", "alpine", "aurora", "avenue", "balloon", "basket",
    "bell", "blossom", "bridge", "bronze", "bubble", "canyon", "cardinal", "carpet",
    "cascade", "celery", "chalk", "chestnut", "cinnamon", "compass", "cotton", "cove",
    "creek", "crown", "drift", "echo", "elm", "evergreen", "fable", "ferry",
    "flint", "flower", "fog", "fox", "fresco", "harvest", "hawk", "heather",
    "hill", "iceberg", "iris", "jewel", "lake", "lilac", "lime", "magnet",
    "marine", "mercury", "mesa", "midnight", "mirror", "morning", "mountain", "mural",
    "nebula", "nutmeg", "opal", "orange", "owl", "panda", "paper", "parrot",
    "pebble", "penguin", "pesto", "petal", "pigeon", "pixel", "plaza", "polar",
    "poppy", "rainbow", "ripple", "rosemary", "satin", "savanna", "shore", "signal",
    "slate", "spark", "spice", "splash", "steel", "straw", "surf", "teal",
    "temple", "thunder", "toast", "torch", "tower", "tundra", "turtle", "walnut",
)
