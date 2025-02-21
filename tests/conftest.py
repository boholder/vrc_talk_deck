from collections.abc import Callable
from typing import Any

import pytest
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

DEFAULT_PARAMS = {"ip": "127.0.0.1", "send-port": 9000, "recv-port": 9001}


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

    def built_server(address_assertion_dict: dict[str, Callable[[Any], None]]):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(fail_on_address_mismatch)
        for address, assertion in address_assertion_dict.items():
            dispatcher.map(address, assertion_handler(assertion))

        return BlockingOSCUDPServer((DEFAULT_PARAMS["ip"], DEFAULT_PARAMS["send-port"]), dispatcher)

    return built_server
