"""
A practice module that contains all practice related information and functionality
"""
from dataclasses import dataclass
from enum import Enum
from random import choice, randint, sample

from lib.logger import get_logger, trace
from lib.theory import (CHORD_INVERSIONS, CHORDS, MODES, MODES_LONG,
                        MODES_TYPES, SCALES)


@dataclass
class PracticeItem:
    """
    Practice Item dataclass that holds information
    about a given practice item (scale, mode, chord, image and audio url)
    """

    p_type: str
    url_audio: str
    url_img: str
    url_img2: str
    scale: int
    scale_text: str
    keyboard: list
    answer: int
    answer_text: str
    answer2: int
    answer2_text: str
    question: int
    question_text: str


class PracticeSettings:
    """
    Practice Settings class that holds information
    about items that should be used during a practice
    """

    def __init__(self):
        self.log = get_logger()
        self.data = {
            "chords": [0, 1, 3],
            "chord_inversions": [0, 3],
            "modes": [0, 1, 2, 3, 4, 5, 6],
            "modes_types": [0],
            "display": [0, 1],
            "HOST": "https://",
        }

    @trace
    def add_item(self, item_name: str, item_value: int) -> None:
        """
        Add a new practice element (e.g. chord, mode and etc) to the practice
        """
        if item_value not in self.data[item_name]:
            self.data[item_name].append(item_value)

    @trace
    def remove_item(self, item_name: str, item_value: int) -> None:
        """
        Remove an existing practice element from the practice
        """
        if item_value in self.data[item_name]:
            self.data[item_name].remove(item_value)
        if len(self.data[item_name]) == 0:
            self.data[item_name].append(0)

    @trace
    def print_add_remove(self, name: str, desc: str, data: dict, id: int) -> str:
        """
        Prepare a text for a user to see which practice elements can be added or removed
        """
        text = f"Add or remove {desc} for your practice:\n\n"
        for d in data.keys():
            text += "{}{}".format(data[d], " " * (30 - len(data[d])))
            if d in self.data[name]:
                text += f"/remove_{id}{d}\n"
            else:
                text += f"/add_{id}{d}\n"
        return text

    @trace
    def print_chord_settings(self) -> str:
        """
        Prepare a text for chords in practice settings
        """
        text = self.print_add_remove("chords", "chords", CHORDS, 0)
        text += "\n"
        text += self.print_add_remove(
            "chord_inversions", "chord inversions", CHORD_INVERSIONS, 1
        )
        return text

    @trace
    def print_modes_settings(self) -> str:
        """
        Prepare a text for modes in practice settings
        """
        text = self.print_add_remove("modes", "modes", MODES, 2)
        text += "\n"
        text += self.print_add_remove("modes_types", "modes directions", MODES_TYPES, 3)
        return text

    @trace
    def print_display_settings(self) -> str:
        """
        Prepare a text for display settings (show/hide piano keyboard or music notation)
        """
        text = "Show or hide items for your practice:\n\n"
        options = {0: "Musical Notation", 1: "Piano Keyboard"}

        for k, v in options.items():
            text += "{}{}".format(v, " " * (30 - len(v)))
            if k in self.data["display"]:
                text += f"/hide_0{k}\n"
            else:
                text += f"/show_0{k}\n"
        return text


class Practice:
    """
    Practice class generates PracticeItem based on practice settings
    """

    def __init__(self, settings: PracticeSettings, item_type: str):
        self.log = get_logger()
        self.settings = settings
        self.item_type = item_type

    def generate(self) -> PracticeItem:
        """
        Generate a ParcticeItem (mode or chord) based on user`s practice settings
        """
        selected_item = selected_type = item_id = text = None

        if self.item_type == "MODES":
            selected_items = (
                self.settings.data["modes"]
                if len(self.settings.data["modes"]) < 5
                else sample(self.settings.data["modes"], 5)
            )
            selected_item = choice(selected_items)
            selected_type = choice(self.settings.data["modes_types"])
            item_id = "03"
            text = {
                0: [str(MODES[i]) for i in selected_items],
                1: MODES[selected_item],
                2: MODES_TYPES[selected_type],
                3: MODES_LONG[selected_item],
            }
        elif self.item_type == "CHORDS":
            selected_items = (
                self.settings.data["chords"]
                if len(self.settings.data["chords"]) < 5
                else sample(self.settings.data["chords"], 5)
            )
            selected_item = choice(selected_items)
            selected_type = choice(self.settings.data["chord_inversions"])
            item_id = "04"
            text = {
                0: [str(CHORDS[i]) for i in selected_items],
                1: CHORDS[selected_item],
                2: CHORD_INVERSIONS[selected_type],
                3: CHORDS[selected_item],
            }
        else:
            raise NotImplementedError

        self.log.debug(f"{self.item_type} selected: {selected_item}")
        self.log.debug(f"{self.item_type} type selected: {selected_type}")

        sd = randint(0, len(SCALES) - 1)
        self.log.debug("scale selected: {}({})".format(SCALES[sd], sd))

        file_id = f"{item_id}{sd:02}{selected_item:02}"

        audio_file_id = f"{file_id}{selected_type:02}.mp3"
        self.log.debug(f"generate audio id:{audio_file_id}")

        audio_url = (
            f"{self.settings.data['HOST']}/audio/{item_id}/{sd + 1:02}/{audio_file_id}"
        )
        self.log.debug(f"audio url:{audio_url}")

        img_file_id = f"{file_id}00.jpg"
        self.log.debug(f"generate keyboard img id:{img_file_id}")

        img_url = f"{self.settings.data['HOST']}/img/{item_id}/{sd + 1:02}/{img_file_id}"
        self.log.debug(f"keyboard img url:{img_url}")

        img_url2 = f"{img_url[:-5]}1.png"
        self.log.debug(f"notes img url:{img_url2}")

        return PracticeItem(
            self.item_type,
            audio_url,
            img_url,
            img_url2,
            sd,
            SCALES[sd],
            list(text[0]),
            selected_item,
            str(text[1]),
            selected_type,
            str(text[2]),
            selected_item,
            str(text[3]),
        )
