import argparse
from collections.abc import Callable
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="VRChat's listening IP")
    parser.add_argument("--send-port", type=int, default=9000, help="VRChat's receive port")
    parser.add_argument("--recv-port", type=int, default=9001, help="VRChat's send port")
    return parser.parse_args()


def bind_client(client: SimpleUDPClient, address: str):
    def send(*message):
        client.send_message(address, *message)

    return send


def set_chat_box_address(client: SimpleUDPClient):
    # ref: https://docs.vrchat.com/docs/osc-as-input-controller#chatbox
    return bind_client(client, "/chatbox/input")


def bind_server(ip: str, port: int, address_handler_dict: dict[str, Callable[[str, Any], None]]):
    dispatcher = Dispatcher()
    for address, handler in address_handler_dict.items():
        dispatcher.map(address, handler)
    return BlockingOSCUDPServer((ip, port), dispatcher)


if __name__ == "__main__":
    args = parse_args()
    print(args)
