import os.path
from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

from tests.conftest import DEFAULT_IP
from vrc_talk_deck.main import AvatarParameter, ParamType, bind_server, build_server, parse_config_file, prepare, set_chat_box_address


def test_send(test_server, random_port_pair):
    c = SimpleUDPClient(DEFAULT_IP, random_port_pair.send)
    send_to_chat_box = set_chat_box_address(c)
    msg = ("hello", True)
    result = False

    def check(*actual):
        nonlocal result
        result = msg == actual

    server = test_server({"/chatbox/input": check}, random_port_pair.send)
    send_to_chat_box(msg)
    server.handle_request()
    assert result


def test_bind_server(random_port_pair):
    c = SimpleUDPClient(DEFAULT_IP, random_port_pair.send)
    send_to_chat_box = set_chat_box_address(c)
    msg = ("hello", "b", "n")
    result = False

    def assertion(_, *actual):
        nonlocal result
        result = msg == actual

    server = bind_server(DEFAULT_IP, random_port_pair.send, {"/chatbox/input": assertion})
    send_to_chat_box(msg)
    server.handle_request()
    assert result


def test_config_parse(test_files_dir):
    general_config, _ = parse_config_file(Path(os.path.join(test_files_dir, "config.toml")), {})
    assert general_config.ip == "0.0.0.0"
    assert general_config.send_port == 111
    assert general_config.receive_port == 222


class TestAvatarParameter(AvatarParameter):
    param_key = "test_param"
    custom_a: int

    def __call__(self, *osc_message):
        assert self.type is ParamType.Int
        assert self.custom_a == 1


def test_avatar_parameter_config_parse(test_files_dir):
    _, p_list = parse_config_file(Path(os.path.join(test_files_dir, "config.toml")), {"test_param": TestAvatarParameter})

    assert len(p_list) == 1
    assert type(p_list[0]) is TestAvatarParameter
    p_list[0]()


def test_prepare():
    actual = prepare(TestAvatarParameter)
    assert actual["test_param"] == TestAvatarParameter


class EchoAvatarParameter(AvatarParameter):
    param_key = "echo_param"
    type = ParamType.Float

    def __call__(self, osc_message: float):
        return osc_message


def test_whole_process(test_server, test_files_dir):
    server_under_test = build_server(Path(os.path.join(test_files_dir, "echo_config.toml")), EchoAvatarParameter)
    mock_client = SimpleUDPClient(DEFAULT_IP, 9001)
    result = False
    msg = 999

    def check(*actual):
        nonlocal result
        result = (msg, True) == actual

    mock_server = test_server({"/chatbox/input": check}, 9000)
    mock_client.send_message("/avatar/parameters/echo_param", msg)
    server_under_test.handle_request()
    mock_server.handle_request()
    assert result
