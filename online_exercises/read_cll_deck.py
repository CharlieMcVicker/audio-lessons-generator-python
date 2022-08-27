from io import TextIOWrapper
import os
from pathlib import Path
from csv import DictReader
import shutil
from typing import Dict, List, Tuple
import unicodedata
from tqdm import tqdm

from config import Config

from .structs import OnlineExercisesCard
from tts import TTSBatchEntry, get_mp3_chr, get_mp3_en, tts_en, AMZ_VOICES, IMS_VOICES
from main import fix_english_sex_genders # feels like these should live in TTS module

COLUMN_NAMES = ["ID", "PSET", "ALT_PRONOUNCE", "PRONOUN", "VERB", "GENDER", "SYLLABARY", "PRONOUNCE", "ENGLISH", "INTRO NOTE", "END NOTE", "APP_FILE"]

def get_app_filename(filename: str):
    # change cache/en/foo.wav --> source/en/foo.wav
    return filename.replace('cache/', 'source/', 1)

def get_cache_filename_from_app_filename(app_filename: str):
    # change source/en/foo.wav --> cache/en/foo.wav
    return app_filename.replace('source/', 'cache/', 1)

def filter_cll_lines(f: TextIOWrapper):
    """
    Remove empty lines and chapter markers from file line iterator
    """
    first_line = True
    for line in f:
        # skip header line
        if first_line:
            first_line = False
            continue

        chomped = line.strip()
        if chomped.startswith('#'):
            continue
        if chomped == '':
            continue
        yield unicodedata.normalize("NFC", line).strip()

def get_all_pronunciations(row: Dict[str, str]) -> List[str]:
    primary_pronunciation = row["PRONOUNCE"].split(';')
    alternate_pronunciatons = row["ALT_PRONOUNCE"].split(';')
    return [pronounce.strip() for pronounce in (primary_pronunciation + alternate_pronunciatons) if pronounce.strip()]

def get_cherokee_audio(cfg: Config, pronunciations: List[str]) -> Tuple[List[str], List[TTSBatchEntry]]:
    audio_file_names: List[str] = []
    tts_calls: List[TTSBatchEntry] = []

    for pronunciation in pronunciations:
        for voice in IMS_VOICES:
            audio_file_names.append(get_app_filename(get_mp3_chr(voice, ensure_punctuated(pronunciation), cfg.alpha)))
            tts_calls.append(TTSBatchEntry(
                voice=voice,
                text=pronunciation
            ))

    return audio_file_names, tts_calls

def generate_english_audio(english: str) -> List[str]:
    audio_file_names: List[str] = []
    for voice in AMZ_VOICES:
        audio_file_names.append(get_app_filename(get_mp3_en(voice, english)))
        # tts_en(voice, english)

    return audio_file_names
        

def ensure_punctuated(src: str):
    """
    Make sure a string ends with a punctuation mark
    """
    return src if src[-1] in ",.?!" else src + "."

def remove_contractions(text: str):
    """
    Remove common contractions from a string of English text.
    """
    # remove contractions
    if "'s" in text:
        text = text.replace("he's", "he is")
        text = text.replace("she's", "she is")
        text = text.replace("it's", "it is")
        text = text.replace("He's", "He is")
        text = text.replace("She's", "She is")
        text = text.replace("It's", "It is")
    if "'re" in text:
        text = text.replace("'re", " are")

    return text

def process_english_text(english: str):
    english_text = english.strip()

    # turn semicolon separated list into something that's nice to listen to
    english_text = " Or. ".join([ensure_punctuated(text.strip()) for text in english_text.split(";")])

    # make text more clear for reading
    english_text = remove_contractions(english_text)

    # capitalize like a sentence
    english_text = english_text[0].upper() + english_text[1:]

    # he -> he or she, etc.
    english_text = fix_english_sex_genders(english_text)

    return english_text


def create_cards_and_batch_tts_for_cll_deck(cfg: Config, dataset_path: Path) -> Tuple[List[OnlineExercisesCard], List[TTSBatchEntry]]:
    cards: List[OnlineExercisesCard] = []
    tts_batch: List[TTSBatchEntry] = []
    with open(dataset_path, 'r') as f:
        data_lines = filter_cll_lines(f)

        reader = DictReader(data_lines, delimiter="|", fieldnames=COLUMN_NAMES)
        for row in reader:
            pronunciations = get_all_pronunciations(row)
            syllabary = [entry.strip().upper() for entry in row["SYLLABARY"].split(';')]
            
            cherokee_audio, tts_calls = get_cherokee_audio(cfg, pronunciations)
            tts_batch.extend(tts_calls)

            english = process_english_text(row["ENGLISH"])
            english_audio = generate_english_audio(english)

            cards.append(
                OnlineExercisesCard(
                    cherokee=pronunciations[0],
                    alternate_pronunciations=pronunciations[1:],
                    cherokee_audio=cherokee_audio,
                    syllabary=syllabary[0],
                    alternate_syllabary=syllabary[1:],
                    english=english,
                    english_audio=english_audio
                )
            )
    
    return cards, tts_batch

def collect_audio_for_cards(cards: List[OnlineExercisesCard], out_dir: str):
    dest_audio: str = os.path.join(out_dir, "source")
    dest_en = os.path.join(dest_audio, "en")
    os.makedirs(dest_en, exist_ok=True)
    dest_chr = os.path.join(dest_audio, "chr")
    os.makedirs(dest_chr, exist_ok=True)
    for card in tqdm(cards):
        for file in card.cherokee_audio:
            shutil.copy(get_cache_filename_from_app_filename(file), dest_chr)
        for file in card.english_audio:
            shutil.copy(get_cache_filename_from_app_filename(file), dest_en)