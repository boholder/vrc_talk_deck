from vrc_talk_deck.boholder_talk_deck import BoholderTalkDeck
from vrc_talk_deck.main import build_server, parse_args

if __name__ == "__main__":
    command_args = parse_args()
    # WARNING: Be careful of security issues, check processors' logic to avoid malicious operations
    server = build_server(command_args.c, BoholderTalkDeck)
    server.serve_forever()
