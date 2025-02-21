from pythonosc.udp_client import SimpleUDPClient

from tests.conftest import DEFAULT_PARAMS
from vrc_talk_deck.main import bind_server, set_chat_box_address


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
