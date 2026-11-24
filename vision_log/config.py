"""설정 파일(JSON)을 읽고 명령 인자로 덮어쓴다. (S2)"""
import copy
import json
from pathlib import Path


DEFAULT_CONFIG = {
    "input_dir": ".",
    "output_dir": "output",
    "log_file_prefix": "facility_",
    "defect_code_file": "defect_codes.csv",
    "process_ms_threshold": 1000,
    "run_log_file": "run_log.txt",
    "filter": {
        "facilities": None,
        "start_date": None,
        "end_date": None,
        "defect_codes": None,
    },
    "spike": {"min_defects": 5, "rate_ratio": 2.0, "z_score": 3.0},
    "dash": {"host": "127.0.0.1", "port": 8050},
}
'''기본 설정 딕셔너리'''


def _deep_update(base, new):
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def load_config(path="config.json", overrides=None):
    """**기본설정 함수**
    - 기본값 <- 설정 파일 <- 명령 인자(overrides) 순서로 합친 설정을 돌려준다.

    overrides 안의 값이 None이면 무시한다(인자를 주지 않은 경우).
    """
    config = copy.deepcopy(DEFAULT_CONFIG)
    path = Path(path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            _deep_update(config, json.load(f))

    if overrides:
        for key, value in overrides.items():
            if value is None:
                continue
            if key == "filter":
                for fkey, fvalue in value.items():
                    if fvalue is not None:
                        config["filter"][fkey] = fvalue
            else:
                config[key] = value
    return config
