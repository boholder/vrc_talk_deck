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


class AvatarParameter(abc.ABC):
    param_key: str
    type: ParamType

    @property
    def address(self):
        return f"/avatar/parameters/{self.param_key}"

    def __call__(self, *osc_message):
        raise NotImplementedError


def parse_parameter(raw: dict, clazz: type[AvatarParameter]) -> AvatarParameter:
    """convert raw dict to Parameter object"""
    obj = clazz()
    obj.type = ParamType(raw.pop("type"))
    obj.__dict__.update(raw)
    return obj


@dataclasses.dataclass
class GeneralConfig:
    ip: str = "127.0.0.1"
    send_port: int = 9000
    receive_port: int = 9001

    def update(self, config: dict):
        for field_name, field_value in vars(GeneralConfig).items():
            if field_name in config and type(config[field_name]) is type(field_value):
                setattr(self, field_name, config[field_name])


def parse_config_file(path: Path, parameter_templates: dict[str, type[AvatarParameter]]) -> tuple[GeneralConfig, list[AvatarParameter]]:
    with path.open("rb") as f:
        parsed = tomllib.load(f)
    if not parsed:
        raise ValueError("config file is empty")

    config = GeneralConfig()
    config.update(parsed)

    parameters = []
    for param_name, param_config in parsed.items():
        if param_name in parameter_templates:
            parameters.append(parse_parameter(param_config, parameter_templates[param_name]))

    return config, parameters


if __name__ == "__main__":
    command_args = parse_args()
    print(command_args)
