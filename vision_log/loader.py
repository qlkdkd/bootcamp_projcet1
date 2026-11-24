"""로그 읽기·합치기·불량코드 결합. (F1, F2, F3, S4)"""
import logging
from pathlib import Path

import pandas as pd

from .writer import ensure_dir

INPUT_ENCODING = "utf-8-sig"  # 제공 파일은 UTF-8(BOM 포함)

LOG_COLUMNS = [
    "timestamp", "facility", "camera_id", "product_code", "serial_no",
    "result", "defect_code", "confidence",
    "box_x1", "box_y1", "box_x2", "box_y2",
    "process_ms", "image_file",
]
DEFECT_CODE_COLUMNS = ["defect_code", "defect_name", "category", "severity"]
NUMERIC_COLUMNS = ["confidence", "box_x1", "box_y1", "box_x2", "box_y2", "process_ms"]

logger = logging.getLogger("vision_log")


def setup_logger(output_dir, filename="run_log.txt"):
    """
    실행 로그를 화면과 텍스트 파일에 함께 남기도록 설정한다. (S4)
    형식: 시각[수준] 메시지
    """
    ensure_dir(output_dir)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(Path(output_dir) / filename, mode="w", encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
    return logger


def find_log_files(input_dir, prefix="facility_"):
    """입력 폴더에서 이름이 prefix로 시작하는 CSV 파일을 모두 찾는다. (F1)"""
    files = sorted(Path(input_dir).glob(f"{prefix}*.csv"))
    logger.info("시설 로그 파일 %d개 발견: %s", len(files), ", ".join(f.name for f in files))
    return files # 파일 경로 목록


def read_log_file(path):
    """시설 로그 CSV 하나를 읽는다. 읽을 수 없거나 필요한 열이 없으면 None을 돌려준다. (S4)"""
    path = Path(path)

    # 파일을 읽을 수 없는 경우
    try:
        df = pd.read_csv(path, encoding=INPUT_ENCODING, dtype=str)
    except Exception as e:  # 인코딩 오류, 빈 파일, 파싱 오류, 권한 문제 등
        logger.warning("건너뜀: %s - 파일을 읽을 수 없음 (%s: %s)", path.name, type(e).__name__, e)
        return None

    df.columns = df.columns.str.strip() #문자열 공백 제거
    missing = [c for c in LOG_COLUMNS if c not in df.columns]
    if missing:
        logger.warning("건너뜀: %s - 필요한 열 없음 %s", path.name, missing)
        return None

    df = df[LOG_COLUMNS].copy()
    for col in ["facility", "camera_id", "product_code", "serial_no", "result", "defect_code", "image_file"]:
        df[col] = df[col].str.strip()
    df["result"] = df["result"].str.upper() # "ng"처럼 섞여도 안전하게 처리하기 위해 대문자 변환
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    ) # datetime 형식으로 변환

    # 열이 NUMERIC_COLUMNS에 해당하면 수치형으로 변환
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    bad_ts = df["timestamp"].isna().sum()
    if bad_ts:
        logger.warning("%s - 검사 시각을 해석할 수 없는 %d줄 제외", path.name, bad_ts)
        df = df.dropna(subset=["timestamp"])

    df["source_file"] = path.name
    logger.info("읽음: %s (%d줄)", path.name, len(df))
    return df


def read_all_logs(input_dir, prefix="facility_"):
    """입력 폴더의 시설 로그를 모두 읽어 DataFrame 목록으로 돌려준다. (F1)"""
    frames = []
    for path in find_log_files(input_dir, prefix):
        df = read_log_file(path)
        if df is not None:
            frames.append(df)
    return frames


def merge_logs(frames):
    """여러 시설 로그를 하나로 합치고 검사 시각 순으로 정렬한다. (F2)"""
    if not frames:
        raise ValueError("읽을 수 있는 시설 로그가 없습니다.")
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(["timestamp", "facility", "camera_id"], kind="stable").reset_index(drop=True)
    logger.info("합친 로그: %d줄", len(merged))
    return merged


def read_defect_codes(path):
    """불량코드표를 읽는다."""
    path = Path(path)
    df = pd.read_csv(path, encoding=INPUT_ENCODING, dtype=str)
    df.columns = df.columns.str.strip()
    missing = [c for c in DEFECT_CODE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"불량코드표 {path.name}에 필요한 열이 없습니다: {missing}")
    df = df[DEFECT_CODE_COLUMNS].apply(lambda s: s.str.strip())
    return df.sort_values("defect_code").reset_index(drop=True)


def attach_defect_info(logs, defect_codes):
    """전체 로그에 불량 이름·분류·심각도 열을 붙인다. (F3)"""
    merged = logs.merge(defect_codes, on="defect_code", how="left")
    unknown = merged["defect_code"].notna() & merged["defect_name"].isna()
    if unknown.any():
        codes = sorted(merged.loc[unknown, "defect_code"].unique())
        logger.warning("불량코드표에 없는 코드 %s (%d건) - '미등록'으로 표시", codes, unknown.sum())
        merged.loc[unknown, "defect_name"] = "미등록(" + merged.loc[unknown, "defect_code"] + ")"
        merged.loc[unknown, "category"] = "미등록"
    return merged


def load_dataset(config):
    """설정에 따라 로그를 읽고, 합치고, 불량코드를 결합한 전체 로그와 불량코드표를 돌려준다."""
    input_dir = Path(config["input_dir"])
    frames = read_all_logs(input_dir, config["log_file_prefix"])
    logs = merge_logs(frames)
    codes = read_defect_codes(input_dir / config["defect_code_file"])
    return attach_defect_info(logs, codes), codes
