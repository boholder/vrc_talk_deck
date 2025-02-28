import os.path
from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

from tests.conftest import DEFAULT_PARAMS
from vrc_talk_deck.main import AvatarParameter, ParamType, bind_server, parse_config_file, set_chat_box_address


def test_send(test_server):
    c = SimpleUDPClient(DEFAULT_PARAMS["ip"], DEFAULT_PARAMS["send-port"])
    send_to_chat_box = set_chat_box_address(c)
    msg = ("hello", "b", "n")
    result = False

    def check(*actual):
        nonlocal result
        result = msg == actual

    server = test_server({"/chatbox/input": check})
    send_to_chat_box(msg)
    server.handle_request()
    assert result


def test_bind_server():
    c = SimpleUDPClient(DEFAULT_PARAMS["ip"], DEFAULT_PARAMS["send-port"])
    send_to_chat_box = set_chat_box_address(c)
    msg = ("hello", "b", "n")
    result = False

    def assertion(_, *actual):
        nonlocal result
        result = msg == actual

    server = bind_server(DEFAULT_PARAMS["ip"], DEFAULT_PARAMS["send-port"], {"/chatbox/input": assertion})
    send_to_chat_box(msg)
    server.handle_request()
    assert result


def test_config_parse(test_files_dir):
    general_config, _ = parse_config_file(Path(os.path.join(test_files_dir, "config.toml")), {})
    assert general_config.ip == "0.0.0.0"
    assert general_config.send_port == 111
    assert general_config.receive_port == 222


def test_avatar_parameter_config_parse(test_files_dir):
    class TestAvatarParameter(AvatarParameter):
        param_key = "test_param"
        custom_a: int

        def __call__(self, *osc_message):
            assert self.type is ParamType.Int
            assert self.custom_a == 1

    _, p_list = parse_config_file(
        Path(os.path.join(test_files_dir, "config.toml")), {"test_param": TestAvatarParameter}
    )

    assert len(p_list) == 1
    assert type(p_list[0]) is TestAvatarParameter
    p_list[0]()
