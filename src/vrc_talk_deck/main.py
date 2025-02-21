import argparse

from pythonosc.udp_client import SimpleUDPClient


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="VRChat's listening IP")
    parser.add_argument("--send-port", type=int, default=9000, help="VRChat's receive port")
    parser.add_argument("--recv-port", type=int, default=9001, help="VRChat's send port")
    return parser.parse_args()


def bind(client: SimpleUDPClient, address: str):
    def send(*message):
        client.send_message(address, *message)

    return send


def set_chat_box_client(client: SimpleUDPClient):
    # ref: https://docs.vrchat.com/docs/osc-as-input-controller#chatbox
    return bind(client, "/chatbox/input")


if __name__ == "__main__":
    args = parse_args()
    print(args)
