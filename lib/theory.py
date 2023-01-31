"""
A music theory configuration file that holds 
information about scales, modes and chords
"""
SCALES = {
    0: "C",
    1: "Db",
    2: "D",
    3: "Eb",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "Ab",
    9: "A",
    10: "Bb",
    11: "B",
}

MODES = {
    0: "Ionian",
    1: "Dorian",
    2: "Phrygian",
    3: "Lydian",
    4: "Mixolydian",
    5: "Aeolian",
    6: "Loerian",
}

MODES_LONG = {
    0: "Ionian (W,W,H,W,W,W,H)",
    1: "Dorian (W,H,W,W,W,H,W)",
    2: "Phrygian (H,W,W,W,H,W,W)",
    3: "Lydian (W,W,W,H,W,W,H)",
    4: "Mixolydian (W,W,H,W,W,H,W)",
    5: "Aeolian (W,H,W,W,H,W,W)",
    6: "Loerian (H,W,W,H,W,W,W)",
}

MODES_TYPES = {0: "ascending", 1: "descending"}

CHORDS = {
    0: "maj7",
    1: "min7",
    2: "min7/b5",
    3: "7",
    4: "dim",
    5: "aug",
    6: "7/#11",
    7: "maj7/#5",
    8: "minM7",
    9: "sus4/7",
    10: "6",
    11: "min6",
}

CHORD_INVERSIONS = {
    0: "root - chord",
    1: "root - 2nd inv. chord",
    2: "root - 3rd inv. chord",
    3: "root - notes asc",
    4: "root - notes desc",
    5: "1st inv. - chord",
    6: "1st inv. - notes asc",
    7: "1st inv. - notes desc",
    8: "2nd inv. - chord",
    9: "2nd inv. - notes asc",
    10: "2nd inv. - notes desc",
    11: "3rd inv. - chord",
    12: "3rd inv. - notes asc",
    13: "3rd inv. - notes desc",
}
