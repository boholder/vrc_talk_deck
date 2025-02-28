import abc
import argparse
import dataclasses
import functools
import logging
import tomllib
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

logging.level = logging.INFO
log = logging.getLogger(__name__)


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


def bind_server(ip: str, port: int, address_handler_dict: dict[str, Callable[[Any], None]]):
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

    def post_configured_init(self):  # noqa: B027
        pass

    def __call__(self, *osc_message) -> Any:
        raise NotImplementedError


def parse_parameter_processor(raw: dict, clazz: type[AvatarParameter]) -> AvatarParameter:
    """convert raw dict to Parameter object"""
    obj = clazz()
    obj.type = ParamType(raw.pop("type"))
    obj.__dict__.update(raw)
    obj.post_configured_init()
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


def parse_config_file(path: Path, parameter_processor: dict[str, type[AvatarParameter]]) -> tuple[GeneralConfig, list[AvatarParameter]]:
    with path.open("rb") as f:
        parsed = tomllib.load(f)
    if not parsed:
        raise ValueError("config file is empty")

    config = GeneralConfig()
    config.update(parsed)

    parameters = []
    for param_name, param_config in parsed.items():
        if param_name in parameter_processor:
            parameters.append(parse_parameter_processor(param_config, parameter_processor[param_name]))

    return config, parameters


def prepare(
    *classes: type[AvatarParameter],
) -> dict[
    str,
    type[AvatarParameter],
]:
    return {clazz.param_key: clazz for clazz in classes}


def handle_and_send_chat(handler: Callable[[Any], Any], sender: Callable[[Any], None], *message):
    log.info("receive: %s", message)
    # remove first address param
    result = handler(*message[1:])
    log.info("send: ", result)
    # True: send the text immediately, bypassing the keyboard
    # ref: https://docs.vrchat.com/docs/osc-as-input-controller#chatbox
    sender((result, True))


def build_server(config_path: Path, *processors: type[AvatarParameter]):
    general_config, parameters = parse_config_file(config_path, prepare(*processors))

    c = SimpleUDPClient(general_config.ip, general_config.send_port)
    send_to_chat_box = set_chat_box_address(c)
    address_handler_dict = {p.address: functools.partial(handle_and_send_chat, p, send_to_chat_box) for p in parameters}

    server = bind_server(general_config.ip, general_config.receive_port, address_handler_dict)
    return server
