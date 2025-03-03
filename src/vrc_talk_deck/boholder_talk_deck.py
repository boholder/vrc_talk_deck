from collections import namedtuple

from vrc_talk_deck.main import AvatarParameter

_Question = namedtuple("_Question", ["zh", "zh_len", "en", "en_len"])


class BoholderTalkDeck(AvatarParameter):
    param_key = "boholder_talk_deck"
    lang: list[str]
    """what language to send"""
    response: list[dict[str, str | int]]
    questions: dict[int, _Question]

    def post_configured_init(self):
        self.questions = {}
        for i, r in enumerate(self.response):
            _id = i
            if "id" in r:
                _id = r["id"]

            self.questions[_id] = _Question(r["zh"], len(r["zh"]), r["en"], len(r["en"]))

    def __call__(self, request_id: int) -> str:
        q: _Question = self.questions[request_id]
        sentences = []
        total_len = 0
        for language in self.lang:
            # max length is 144
            # ref: https://docs.vrchat.com/docs/osc-as-input-controller#chatbox
            length_of_sentence = getattr(q, f"{language}_len")
            if total_len + length_of_sentence >= 144 - (len(self.lang) * 3):
                break
            sentences.append(getattr(q, language))
            total_len += length_of_sentence

        if len(sentences) == 1:
            return sentences[0]
        else:
            return " | ".join(sentences)
