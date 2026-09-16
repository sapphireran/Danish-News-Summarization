from pathlib import Path

from danish_news_sum.config import DA_EN, EN_DA, MT5_LARGE, MT5_SMALL, dump_json, load_json


def test_translation_margin_matches_original_scripts():
    assert DA_EN.max_length == 512
    assert DA_EN.text_max_length == 460
    assert DA_EN.source_model.endswith("opus-mt-da-en")
    assert EN_DA.source_model.endswith("opus-mt-en-da")


def test_finetune_defaults_match_finetune_py():
    assert MT5_LARGE.model_name == "google/mt5-large"
    assert MT5_LARGE.num_train_epochs == 20
    assert MT5_LARGE.learning_rate == 3e-4
    assert MT5_LARGE.optim == "adafactor"
    assert MT5_LARGE.metric_for_best_model == "rouge_1_mid_fmeasure"


def test_small_config_points_at_small_checkpoint_dir():
    assert MT5_SMALL.save_dir == "./small_model"
    assert MT5_SMALL.model_name == "google/mt5-small"


def test_json_roundtrip(tmp_path: Path):
    path = tmp_path / "mt5.json"
    dump_json(MT5_LARGE, path)
    payload = load_json(path)
    assert payload["model_name"] == "google/mt5-large"
    assert payload["warmup_steps"] == 1000
