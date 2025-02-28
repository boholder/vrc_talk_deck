import os
from pathlib import Path

from vrc_talk_deck.boholder_talk_deck import BoholderTalkDeck
from vrc_talk_deck.main import parse_config_file, prepare


def test_boholder_talk_deck(test_files_dir):
    config_path = Path(os.path.join(test_files_dir, "talk_deck_config.toml"))
    _, p_list = parse_config_file(config_path, prepare(BoholderTalkDeck))
    processor = p_list[0]
    assert type(processor) is BoholderTalkDeck
    assert processor(0) == "你好！ | Hello!"  # noqa: RUF001
    assert processor(1) == "太长了"
