"""
A user realted storage and functionality
"""
import json
from dataclasses import dataclass

from lib.logger import get_logger, trace
from lib.practice import PracticeSettings


class UserStats:
    """
    User`s statistic class that stores guessed or not guessed chords and modes
    """

    success_answers: dict = {"chords": {}, "modes": {}}
    failed_answers: dict = {"chords": {}, "modes": {}}

    def __init__(self):
        self.log = get_logger()

    @trace
    def add_new(self, name: str, chord: int) -> None:
        """
        Add a new element (chord or mode) to the statistics if not exists
        """
        if chord not in self.success_answers[name]:
            self.success_answers[name][chord] = self.failed_answers[name][chord] = 0

    @trace
    def result(self, succeess: bool, name: str, chord: int, ctype: int) -> None:
        """
        Fail or pass a given chord or mode
        """
        for c in [chord, f"{chord}:{ctype}"]:
            self.add_new(name, c)
            if succeess:
                self.success_answers[name][c] += 1
            else:
                self.failed_answers[name][c] += 1

    @trace
    def prepare_stats(self) -> str:
        """
        Prepare the statistics information for a user to display
        """
        txt = ""
        for name, stats in self.success_answers.items():
            txt += f"{name}:\n"
            for k, v in stats.items():
                if ":" in str(k):
                    continue
                right = f"right:{v} wrong:{self.failed_answers[name][k]}"
                txt += "{:<20} {:>20}\n".format(k, right)
            txt += "\n"
        return txt


@dataclass
class UserProfile:
    """
    A User Profile dataclass
    For now contains only a user name.
    """

    user_name: str


@dataclass
class User:
    """
    The main User dataclass
    Holds a user`s profile, statsistic and practice settings information
    """

    id: int
    profile: UserProfile
    stats: UserStats
    settings: PracticeSettings

    def __init__(self, user_id: int, user_name: str) -> None:
        self.id = user_id
        self.stats = UserStats()
        self.profile = UserProfile(user_name)
        self.settings = PracticeSettings()


class UserManager:
    """
    A manager class that handles load and save of a user`s profile
    """

    def __init__(self):
        self.log = get_logger()

    @trace
    def load_user(self, user_id: int) -> User:
        """
        Load a user profile from a json file or create a new one if not exists
        """
        data = None
        try:
            with open(f"users/{str(user_id)}", "r") as f:
                rd = f.read()
                dict_data = json.loads(rd)
                data = User(user_id, dict_data["profile"]["user_name"])
                data.profile = UserProfile(dict_data["profile"]["user_name"])
                data.profile.user_name = dict_data["profile"]["user_name"]
                data.stats = UserStats()
                data.stats.failed_answers = dict_data["failed_answers"]
                data.stats.success_answers = dict_data["success_answers"]
                data.settings = PracticeSettings()
                data.settings.data["modes"] = dict_data["practice_modes"]
                data.settings.data["modes_types"] = dict_data["practice_modes_types"]
                data.settings.data["chords"] = dict_data["practice_chords"]
                data.settings.data["chord_inversions"] = dict_data[
                    "practice_chord_inversions"
                ]
                data.settings.data["display"] = dict_data["practice_display"]
        except Exception as e:
            # Unable to load a profile.Will create a default one
            self.log.exception(e)
            self.log.warning(f"nothing to load. creating a new user {user_id}")
            data = User(user_id, "default")

        return data

    @trace
    def save_user(self, user_id: int, data: User) -> None:
        """
        Save user`s profile to a json file
        """
        dict_data = {
            "success_answers": data.stats.success_answers,
            "failed_answers": data.stats.failed_answers,
            "id": user_id,
            "profile": {"user_name": data.profile.user_name},
            "practice_modes": data.settings.data["modes"],
            "practice_modes_types": data.settings.data["modes_types"],
            "practice_chords": data.settings.data["chords"],
            "practice_chord_inversions": data.settings.data["chord_inversions"],
            "practice_display": data.settings.data["display"],
        }
        json_data = json.dumps(dict_data)

        with open(f"users/{str(user_id)}", "w") as f:
            f.write(json_data)
