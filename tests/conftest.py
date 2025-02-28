import os
import random
from collections import namedtuple
from collections.abc import Callable
from typing import Any

import pytest
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

DEFAULT_IP = "127.0.0.1"

PortPair = namedtuple("PortPair", ["send", "receive"])


@pytest.fixture
def random_port_pair():
    return PortPair(random.randint(10000, 15000), random.randint(15001, 20000))


@pytest.fixture
def assertion_handler():
    def wrapper(assertion: Callable[[Any], None]):
        def handle(_, *args):
            assertion(*args)

        return handle

    return wrapper


@pytest.fixture
def test_server(assertion_handler):
    def fail_on_address_mismatch(_, __):
        raise AssertionError("address mismatched")

    def built_server(address_assertion_dict: dict[str, Callable[[Any], None]], bind_port):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(fail_on_address_mismatch)
        for address, assertion in address_assertion_dict.items():
            dispatcher.map(address, assertion_handler(assertion))

        return BlockingOSCUDPServer((DEFAULT_IP, bind_port), dispatcher)

    return built_server


@pytest.fixture
def test_files_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "test_files")
