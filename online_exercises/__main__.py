import json
import os
from pathlib import Path
from dataclasses import asdict

from config import Config
from .read_cll_deck import create_cards_and_batch_tts_for_cll_deck
from .create_cll_vocab_set import create_and_dump_vocab_collection

def load_config(dataset: str):
    os.makedirs("configs", exist_ok=True)
    cfg_file: str = f"configs/{dataset}-cfg.json"
    if os.path.exists(cfg_file):
        with open(cfg_file, "r") as f:
            cfg = Config.load(f)
    else:
        cfg = Config()
        with open(cfg_file, "w") as w:
            Config.save(w, cfg)
    
    return cfg

def get_out_dir(cfg: Config, dataset: str):
    # get the run dir for the file
    if cfg.alpha and cfg.alpha != 1.0:
        run_dir = Path(os.path.join(os.path.realpath("."), "output", f"{dataset}_{cfg.alpha:.2f}"))
    else:
        run_dir = Path(os.path.join(os.path.realpath("."), "output", dataset))

    out_dir = run_dir / "online_exercises"
    os.makedirs(out_dir, exist_ok=True)

    return out_dir

if __name__ == '__main__':
    dataset = 'cll1-v3'
    cfg = load_config(dataset)
    out_dir = get_out_dir(cfg, dataset)
    # read_deck_from_csv(cfg, Path('cherokee-vocab-data/cll1-v3.txt'))
    create_and_dump_vocab_collection(cfg, dataset, out_dir)
    cards, tts_batch = create_cards_and_batch_tts_for_cll_deck(cfg, Path('cherokee-vocab-data', f'{dataset}.txt'))
    # TODO: run tts if needed
    json.dump(
        [asdict(card) for card in cards],
        open(out_dir / "cll1-cards.json", "w"),
        ensure_ascii=False,
        sort_keys=True # better for diffing
    )
