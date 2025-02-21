import abc
import argparse
import dataclasses
import tomllib
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="config file path", type=Path, required=True)
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


class ParamType(Enum):
    Int = "Int"
    bool = "bool"
    Float = "Float"


@dataclasses.dataclass
class AvatarParameter(abc.ABC):
    name: str
    type: ParamType
    config: dict

    @property
    def address(self):
        return f"/avatar/parameters/{self.name}"

    def __call__(self, *osc_message):
        raise NotImplementedError


def pick_parameter(raw: dict):
    """convert raw dict to Parameter object"""
    pass


@dataclasses.dataclass
class GeneralConfig:
    ip: str = "127.0.0.1"
    send_port: int = 9000
    receive_port: int = 9001


def parse_config_file(path: Path) -> tuple[GeneralConfig, list[AvatarParameter]]:
    with path.open("rb") as f:
        parsed = tomllib.load(f)
    if not parsed:
        raise ValueError("config file is empty")

    config = GeneralConfig()
    for field_name, field_value in vars(GeneralConfig).items():
        if field_name in parsed and type(parsed[field_name]) is type(field_value):
            setattr(config, field_name, parsed[field_name])

    return config, []


if __name__ == "__main__":
    command_args = parse_args()
    print(command_args)
