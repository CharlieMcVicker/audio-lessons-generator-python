#!/usr/bin/env python3
from dataclasses import dataclass
from typing import TextIO

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Config:
    final_review_session_count: int = 0
    data_dir: str = "walc1"
    prerecorded_audio: bool = True
    max_session_length: float = 30 * 60
    griffin_lim: bool = False
    debug_deck: bool = False
    debug_deck_size: int = 20
    sessions_to_create: int = 99
    create_all_sessions: bool = True
    review_card_max_tries: int = 7
    review_card_tries_decrement: int = 0
    new_card_max_tries: int = 7
    new_card_tries_decrement: int = 0
    new_cards_per_session: int = 7
    new_cards_increment: int = 0
    review_cards_per_session_max: int = 21
    temp_dir: str = "tmp"
    output_dir: str = "output"
    sort_deck_by_size: bool = False

    @classmethod
    def load(cls, file: TextIO):
        return Config.from_json(file)

    @classmethod
    def save(cls, config, file: TextIO) -> None:
        file.write(config.to_json(indent=4, sort_keys=True))
        file.write("\n")


if __name__ == "__main__":
    cfg: Config = Config()
    with open("text-config.json", "w") as f:
        Config.save(cfg, f)
