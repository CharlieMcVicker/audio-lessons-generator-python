from dataclasses import asdict
from json import load, dump
from sys import argv

from tts import AMZ_VOICES, get_mp3_en, tts_en

from .structs import OnlineExercisesCard

def generate_audio_for_voice(voice: str, text: str) -> str:
    """
    Create English audio mp3 and return path.
    """
    tts_en(voice, text)
    return get_mp3_en(voice, text)

def generate_english_audio(card : OnlineExercisesCard) -> OnlineExercisesCard:
    return OnlineExercisesCard(
        cherokee=card.cherokee,
        cherokee_audio=card.cherokee_audio,
        syllabary=card.syllabary,
        alternate_pronunciations=card.alternate_pronunciations,
        alternate_syllabary=card.alternate_syllabary,
        english=card.english,
        english_audio=[generate_audio_for_voice(voice, card.english) for voice in AMZ_VOICES]
    )

def main():
    deck_src = argv[2]
    deck_out = argv[3]

    with open(deck_src) as f:
        json_deck = load(f)
        deck = [OnlineExercisesCard(**card) for card in json_deck]

    deck_with_audio = [generate_english_audio(card) for card in deck]
    with open(deck_out, 'w') as f:
        dump([asdict(card) for card in deck_with_audio], f, ensure_ascii=False, sort_keys=True)
