from pythonosc.udp_client import SimpleUDPClient

from tests.conftest import DEFAULT_PARAMS
from vrc_talk_deck.main import set_chat_box_client


def test_send(test_server):
    c = SimpleUDPClient(DEFAULT_PARAMS["ip"], DEFAULT_PARAMS["send-port"])
    send_to_chat_box = set_chat_box_client(c)
    msg = ("hello", "b", "n")

    def check(*actual):
        assert msg == actual

    server = test_server({"/chatbox/input": check})
    send_to_chat_box(msg)
    server.handle_request()
