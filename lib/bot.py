"""
The bot's main logic
"""
import json

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from lib.logger import LOGGER_NAME, Logger, get_logger, trace
from lib.practice import Practice
from lib.user import UserManager


class Bot:
    """
    The bot's class that handles telegram`s communication
    and all interaction with an end user
    """

    (
        MENU,
        ABOUT,
        PRACTICE_RESPONSE,
        PRACTICE,
        STATS,
        PRE_ACTION,
        PRACTICE_MENU,
        SETTINGS_MENU,
        SETTINGS,
    ) = range(9)

    def __init__(self):
        self.bot = None
        self.session_manager = {}
        # load json config
        self.settings = None
        with open("./config/settings.json", "r") as f:
            self.settings = json.load(f)

        # init logger
        self.logger = Logger(
            self.settings["logger"]["path"] + "/" + self.settings["logger"]["name"],
            self.settings["logger"]["file"],
            self.settings["logger"]["console"],
            self.settings["logger"]["level"],
            self.settings["logger"]["max_size"],
            self.settings["logger"]["backup_count"],
            self.settings["logger"]["name_date_format"],
            LOGGER_NAME,
        )

        self.log = get_logger()

    @trace
    def cleanup_messages(self, chat_id: int) -> None:
        """
        Delete selected messages from a chat
        """
        self.log.debug("cleanup ids: {}".format(self.session_manager[chat_id]["msg_ids"]))
        for i in self.session_manager[chat_id]["msg_ids"]:
            try:
                self.bot.delete_message(chat_id, i)
            except Exception as e:
                self.log.exception(f"msg_id {i}, ex:\n{e}")
        self.session_manager[chat_id]["msg_ids"] = []

    @trace
    def remove_msg(self, chat_id: int, msg_id: int) -> None:
        """
        Add a message to into "to delete" list
        """
        if msg_id not in self.session_manager[chat_id]["msg_ids"]:
            self.session_manager[chat_id]["msg_ids"].append(msg_id)

    @trace
    def start(self, update: Update, context: CallbackContext) -> int:
        """
        The entry point for the chat
        """
        self.log.info("start {}".format(update.message.chat_id))

        # load user information
        if update.message.chat_id not in self.session_manager:
            um = UserManager()
            user = um.load_user(update.message.chat_id)
            self.session_manager[update.message.chat_id] = {
                "user": user,
                "msg_ids": [],
                "loc": "start",
                "practice": None,
            }

        self.log.info(
            f"userid: {update.message.from_user.id}, username: {update.message.from_user.username}"
        )

        update.message.reply_text("Welcome to Music Learning and Practice Bot!\n")

        return self.menu(update, context)

    @trace
    def pre_process(
        self,
        update: Update,
        loc: str,
        remove_msg: bool = False,
        cleanup_msg: bool = False,
    ) -> None:
        """
        Perform pre-processing routines:
        store previous location and delete old messages
        """
        self.log.info(
            f"pre_process({update.message.chat_id}, {loc}, {remove_msg}, {cleanup_msg})"
        )
        self.session_manager[update.message.chat_id]["loc"] = loc

        if cleanup_msg:
            self.cleanup_messages(update.message.chat_id)

        if remove_msg:
            self.remove_msg(update.message.chat_id, update.message.message_id)

    @trace
    def post_process(
        self, update: Update, kb_text: str, kb_items: list, remove_msg: bool = True
    ) -> None:
        """
        Peform post-processing routines:
        display ui elements and mark a message for removal
        """
        self.log.info(
            f"post_process({update.message.chat_id}, {kb_text}, {kb_items}, {remove_msg})"
        )

        msg = update.message.reply_text(
            kb_text,
            reply_markup=ReplyKeyboardMarkup(
                kb_items, one_time_keyboard=True, resize_keyboard=True
            ),
        )

        if remove_msg:
            self.remove_msg(update.message.chat_id, msg.message_id)

    @trace
    def send_image(self, chat_id: int, url: str) -> None:
        """
        Send an image url to the chat
        """
        msg = self.bot.send_photo(chat_id=chat_id, photo=url)
        self.remove_msg(chat_id, msg.message_id)

    @trace
    def send_audio(self, chat_id: int, url: str) -> None:
        """
        Send an audio url to the chat
        """
        msg = self.bot.send_audio(chat_id=chat_id, audio=url)
        self.remove_msg(chat_id, msg.message_id)

    @trace
    def pre_action(self, update: Update, context: CallbackContext) -> int:
        """
        Peform specific actions before handling user input and ui
        """
        self.pre_process(update, "pre_action", True, True)

        proxies = {
            "STATS": self.stats,
            "PRACTICE": self.practice_menu,
            "SETTINGS": self.settings_menu,
            "BACK": self.settings_menu,
        }
        if update.message.text in proxies:
            return proxies[update.message.text](update, context)
        return self.menu(update, context)

    @trace
    def practice_menu(self, update: Update, context: CallbackContext) -> int:
        """
        The practice menu handler
        """
        self.pre_process(update, "p_menu", False, False)

        # TODO: add 'KEYS' and 'INTERVALS'
        self.post_process(
            update,
            "Practice Menu:\n\nNote: go to SETTINGS to setup your practice.",
            [["MODES", "CHORDS", "MENU"]],
        )
        return self.PRACTICE

    @trace
    def practice(self, update: Update, context: CallbackContext) -> int:
        """
        The practice (chords and modes) handler
        """
        self.pre_process(update, "p", False, False)

        if update.message.text == "MENU":
            return self.pre_action(update, context)

        # TODO : Can we remove the message in pre_process for ^^^ MENU ???
        self.remove_msg(update.message.chat_id, update.message.message_id)

        s = self.session_manager[update.message.chat_id]
        if update.message.text == "NEXT":
            update.message.text = s["practice"]
        if update.message.text in ["CHORDS", "MODES"]:
            s["practice"] = update.message.text
            s["user"].settings.data["HOST"] = self.settings["HOST"]
            s["pm"] = Practice(s["user"].settings, update.message.text)
        else:
            raise NotImplementedError

        s["pi"] = s["pm"].generate()

        self.send_audio(update.message.chat_id, s["pi"].url_audio)

        self.post_process(
            update,
            f"Please listen and guess the {s['practice'].lower()[:-1]} (in {s['pi'].scale_text})\n",
            [s["pi"].keyboard],
        )
        return self.PRACTICE_RESPONSE

    @trace
    def practice_response(self, update: Update, context: CallbackContext) -> int:
        """
        Handle a user`s reponce for a give practice item
        """
        self.pre_process(update, "p_resp", True, True)
        s = self.session_manager[update.message.chat_id]

        # display music notation
        if 0 in s["user"].settings.data["display"]:
            self.send_image(update.message.chat_id, s["pi"].url_img2)
        # display piano keyboard
        if 1 in s["user"].settings.data["display"]:
            self.send_image(update.message.chat_id, s["pi"].url_img)

        item = ""
        if s["practice"] == "CHORDS":
            item = "{}{} ({})".format(
                s["pi"].scale_text, s["pi"].answer_text, s["pi"].answer2_text
            )
        elif s["practice"] == "MODES":
            item = "{} ({}) on {}".format(
                s["pi"].answer_text, s["pi"].answer2_text, s["pi"].scale_text
            )

        result = s["pi"].answer_text == update.message.text
        s["user"].stats.result(
            result, s["practice"].lower(), s["pi"].answer_text, s["pi"].answer2_text
        )

        um = UserManager()
        um.save_user(update.message.chat_id, s["user"])

        self.post_process(
            update,
            f"Correct! {item}" if result else f"No, that was {item}",
            [["NEXT"], ["MENU"]],
        )
        return self.PRACTICE

    @trace
    def stats(self, update: Update, context: CallbackContext) -> int:
        """
        Display user`s practice statistics
        """
        self.pre_process(update, "stats", False, False)

        if update.message.text == "MENU":
            return self.pre_action(update, context)

        self.post_process(
            update,
            self.session_manager[update.message.chat_id]["user"].stats.prepare_stats(),
            [["MENU"]],
        )
        return self.STATS

    @trace
    def menu(self, update: Update, context: CallbackContext) -> int:
        """
        Display main menu
        """
        self.pre_process(update, "menu", False, False)
        # TODO: add 'THEORY'
        self.post_process(update, "Menu:", [["PRACTICE"], ["STATS"], ["SETTINGS"]])
        return self.PRE_ACTION

    @trace
    def settings_menu(self, update: Update, context: CallbackContext) -> int:
        """
        Display settings
        """
        self.pre_process(update, "s_menu", False, True)
        # TODO: add 'INTERVALS' and 'KEYS'
        self.post_process(
            update,
            "Parctice Settings:",
            [["CHORDS"], ["MODES"], ["DISPLAY"], ["ABOUT"], ["MENU"]],
        )
        return self.SETTINGS

    @trace
    def settings_action(self, update: Update, context: CallbackContext) -> int:
        """
        Handle user`s selection in settings
        """
        self.pre_process(update, "s_action", True, False)
        s = self.session_manager[update.message.chat_id]

        proxies = {
            "MENU": self.menu,
            "BACK": self.menu,
            "CHORDS": self.settings_chords,
            "MODES": self.settings_modes,
            "DISPLAY": self.settings_display,
        }
        if update.message.text in proxies.keys():
            return proxies[update.message.text](update, context)

        if update.message.text == "ABOUT":
            self.post_process(
                update,
                "This telegram bot was built to help learn and practice in music theory.\nCoderOK @ 2023\nhttps://github.com/2CoderOK/",
                [["BACK"]],
            )
        elif "/add" in update.message.text or "/remove" in update.message.text:
            settings_proxies = {
                "_0": ["chords", self.settings_chords],
                "_1": ["chord_inversions", self.settings_chords],
                "_2": ["modes", self.settings_modes],
                "_3": ["modes_types", self.settings_modes],
            }
            for k, v in settings_proxies.items():
                if k in update.message.text:
                    action, id = update.message.text.split(k)
                    if "add" in action:
                        s["user"].settings.add_item(v[0], int(id))
                    else:
                        s["user"].settings.remove_item(v[0], int(id))
                    return v[1](update, context)
        elif "/show" in update.message.text or "/hide" in update.message.text:
            if "_0" in update.message.text:
                action, id = update.message.text.split("_0")
                if "show" in action:
                    s["user"].settings.add_item("display", int(id))
                else:
                    s["user"].settings.remove_item("display", int(id))
                return self.settings_display(update, context)

        return self.PRE_ACTION

    @trace
    def settings_chords(self, update: Update, context: CallbackContext) -> int:
        """
        Handle Chords settings
        """
        self.pre_process(update, "s_chords", True, False)
        self.post_process(
            update,
            self.session_manager[update.message.chat_id][
                "user"
            ].settings.print_chord_settings(),
            [["BACK"]],
        )
        return self.SETTINGS

    @trace
    def settings_modes(self, update: Update, context: CallbackContext) -> int:
        """
        Handle Modes settings
        """
        self.pre_process(update, "s_modes", True, False)
        self.post_process(
            update,
            self.session_manager[update.message.chat_id][
                "user"
            ].settings.print_modes_settings(),
            [["BACK"]],
        )
        return self.SETTINGS

    @trace
    def settings_display(self, update: Update, context: CallbackContext) -> int:
        """
        Handle Practice Display settings
        """
        self.pre_process(update, "s_display", True, False)
        self.post_process(
            update,
            self.session_manager[update.message.chat_id][
                "user"
            ].settings.print_display_settings(),
            [["BACK"]],
        )
        return self.SETTINGS

    @trace
    def cancel(self, update: Update, context: CallbackContext) -> int:
        """
        Stop the chat
        """
        self.pre_process(update, "cancel", False, False)
        return ConversationHandler.END

    @trace
    def main(self) -> None:
        """
        The bot`s state machine setup
        """
        updater = Updater(self.settings["TOKEN"])

        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.MENU: [
                    MessageHandler(Filters.update.message, self.menu, run_async=True)
                ],
                self.PRACTICE_MENU: [
                    MessageHandler(
                        Filters.update.message, self.practice_menu, run_async=True
                    )
                ],
                self.PRE_ACTION: [
                    MessageHandler(
                        Filters.update.message, self.pre_action, run_async=True
                    )
                ],
                self.PRACTICE: [
                    MessageHandler(Filters.update.message, self.practice, run_async=True)
                ],
                self.PRACTICE_RESPONSE: [
                    MessageHandler(
                        Filters.update.message, self.practice_response, run_async=True
                    )
                ],
                self.STATS: [
                    MessageHandler(Filters.update.message, self.stats, run_async=True)
                ],
                self.SETTINGS: [
                    MessageHandler(
                        Filters.update.message, self.settings_action, run_async=True
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            run_async=True,
        )

        dispatcher.add_handler(conv_handler)

        self.bot = updater.bot
        updater.start_polling()
        updater.idle()
