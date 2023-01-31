"""
The main file
"""
from lib.bot import Bot
import os
import sys


try:
    import fcntl
except ImportError:
    fcntl = None


LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "lock")


class SingleInstance:
    """Bot launcher class - which is Singleton.

    Attributes:
        is_running: The boolean status
    [True - is running, False - is not running].
    """
    def __init__(self):
        self.is_running = False
        self.validate()

    def validate(self) -> None:
        """Locks a file to make sure that only one instance of the bot will be running
        """
        try:
            if os.path.exists(LOCK_PATH):
                os.unlink(LOCK_PATH)
            os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except EnvironmentError as err:
            if err.errno == 13:
                self.is_running = True
            else:
                raise


if __name__ == "__main__":
    """Initializes logger and starts the main application.
    """
    try:
        si = SingleInstance()
        if si.is_running:
            sys.exit("Another instance of the bot is already running!")
        else:
            app = Bot()
            app.main()
    except Exception as e:
        print(e)
