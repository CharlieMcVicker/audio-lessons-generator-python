from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional
import unicodedata
import json

from config import Config
from .structs import VocabCollection, VocabSet

CLL1_COLLECTION_ID = 'CLL1'

def clean_terms(terms: List[str]) -> List[str]:
    return [term.split(';')[0].strip() for term in terms];

def create_and_dump_vocab_collection(cfg: Config, dataset: str, out_dir: Path):
    cll_collection = create_vocab_collection_from_dataset(Path(f"./cherokee-vocab-data/{dataset}.txt"))
    json.dump(asdict(cll_collection), open(out_dir / "cll1.json", "w"), ensure_ascii=False, sort_keys=True) 


def create_vocab_collection_from_dataset(dataset: Path) -> VocabCollection:
    terms_by_chapter: Dict[str, List[str]] = {}
    current_chapter: Optional[str] = None
    with open(dataset, "r") as r:
        first_line = True
        for line in r:
            line = unicodedata.normalize("NFC", line)
            if first_line:
                first_line = False
                continue
            if line.startswith("#"):
                if line.startswith('#Chapter'):
                    current_chapter = line[1:].strip().strip('|')
                continue
            
            if line == "\n":
                continue

            if current_chapter is None:
                raise ValueError("File should have a chatper marker before any terms")

            pronounce = line.strip().split('|')[7]
            if not current_chapter in terms_by_chapter:
                terms_by_chapter[current_chapter] = [pronounce]
            else:
                terms_by_chapter[current_chapter].append(pronounce)
    


    return VocabCollection(
        id=CLL1_COLLECTION_ID,
        title="Cherokee Language Lessons 1",
        sets=[VocabSet(
                id=f"{CLL1_COLLECTION_ID}:{chapters}",
                title=chapters,
                terms=clean_terms(terms)) for chapters, terms in terms_by_chapter.items()]
    )
