from dataclasses import dataclass
import re
from typing import List

from LeitnerAudioDeck import AudioCard

def normalizePronunciation(cherokee: str):
    return re.sub(r"[\.\?\,]", cherokee.strip().lower(), "")

def cleanSyllabary(syllabary: str):
    return syllabary.strip().upper()

@dataclass
class OnlineExercisesCard:
    cherokee: str
    cherokee_audio: List[str]
    syllabary: str

    alternate_pronunciations: List[str]
    alternate_syllabary: List[str]

    english: str
    english_audio: List[str]

    @staticmethod
    def from_audio_card(card: AudioCard) -> "OnlineExercisesCard":

        return OnlineExercisesCard(
            cherokee=normalizePronunciation(card.data.challenge),
            cherokee_audio=[f.file for f in card.data.challenge_files],
            syllabary=cleanSyllabary(card.data.syllabary.split(';')[0]),

            alternate_pronunciations=[normalizePronunciation(cherokee) for cherokee in card.data.challenge_alts],
            alternate_syllabary=[cleanSyllabary(syllabary) for syllabary in card.data.syllabary.split(';')[1:]],

            english=card.data.answer,
            english_audio=[f.file for f in card.data.answer_files]
        )

@dataclass
class VocabSet:
    id: str
    title: str
    terms: List[str] # cherokee pronunciation

@dataclass
class VocabCollection:
    id: str
    title: str
    sets: List[VocabSet]