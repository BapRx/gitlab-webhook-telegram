#!/usr/bin/env python3

"""
gitlab-webhook-telegram
"""

import json
import logging
import sys
from typing import List, Tuple

MODE_NONE = 0


class Context:
    """
    A class to pass all the parameters and shared values
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.button_mode = MODE_NONE
        self.wait_for_verification = False
        self.config = None
        self.verified_chats = None
        self.table = None

    def get_config(self) -> Tuple[dict, List[int], dict]:
        """
        Load the config file and transform it into a python usable var
        """
        try:
            with open(f"{self.directory}config.json") as config_file:
                self.config = json.load(config_file)
        except Exception as e:
            print(f"Unable to read {self.directory}config.json. Exception follows")
            print(str(e))
            sys.exit()

        if not all(
            required_key in self.config
            for required_key in ("gitlab-projects", "passphrase", "telegram-token")
        ):
            print(
                f"{self.directory}config.json seems to be misconfigured, please follow"
                " the README instructions."
            )
            sys.exit()

        logging.basicConfig(
            level=self.config.get("log-level", "INFO"),
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        try:
            with open(f"{self.directory}verified_chats.json") as verified_chats_file:
                self.verified_chats = json.load(verified_chats_file)
        except FileNotFoundError:
            logging.warning(f"File {self.directory}verified_chats.json not found. Assuming empty")
            self.verified_chats = []
        except Exception as e:
            logging.critical(
                f"Unable to read {self.directory}verified_chats.json. Exception follows"
            )
            logging.critical(str(e))
            sys.exit()
        try:
            with open(f"{self.directory}chats_projects.json") as table_file:
                self.table = {}
                data = json.load(table_file)
                for token, users in data.items():
                    self.table[token] = {"users": {}}
                    for chat_id, preferences in users.get("users", {}).items():
                        self.table[token]["users"][int(chat_id)] = preferences
        except FileNotFoundError:
            logging.warning(f"File {self.directory}chats_projects.json not found. Assuming empty")
            self.table = {}
        except Exception as e:
            logging.critical(
                f"Unable to read {self.directory}chats_projects.json. Exception follows"
            )
            logging.critical(str(e))
            sys.exit()
        return self.config, self.verified_chats, self.table

    def migrate_table_config(self) -> dict:
        """
        Add missing keys to table config file if needed
        """
        for token in self.table:
            for kind in ("jobs", "pipelines", "merge_requests"):
                if kind not in self.table[token]:
                    self.table[token][kind] = {}
        return self.table

    def write_verified_chats(self) -> None:
        """
        Save the verified chats file
        """
        with open(self.directory + "verified_chats.json", "w+") as outfile:
            json.dump(self.verified_chats, outfile)

    def write_table(self) -> None:
        """
        Save the verified chats file
        """
        with open(self.directory + "chats_projects.json", "w+") as outfile:
            json.dump(self.table, outfile)

    def is_authorized_project(self, token: str) -> bool:
        """
        Test if the token is in the configuration
        """
        for projet in self.config["gitlab-projects"]:
            if token == projet["token"]:
                return True
        return False
