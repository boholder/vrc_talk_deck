import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="VRChat's listening IP")
    parser.add_argument("--send-port", type=int, default=9000, help="VRChat's receive port")
    parser.add_argument("--recv-port", type=int, default=9001, help="VRChat's send port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(args)
