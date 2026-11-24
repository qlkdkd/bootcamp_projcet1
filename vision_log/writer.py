"""결과 파일 저장. (S3, S5)

CSV는 엑셀에서 한글이 깨지지 않도록 UTF-8 BOM(utf-8-sig)으로 저장한다.
"""
from pathlib import Path

CSV_ENCODING = "utf-8-sig"
TEXT_ENCODING = "utf-8"


def ensure_dir(path):
    """폴더가 없으면 만든다. (S3)"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_csv(df, output_dir, filename, index=False):
    '''
    데이터프레임을 csv 파일로 output_dir 경로에 저장
    '''
    path = ensure_dir(output_dir) / filename
    df.to_csv(path, index=index, encoding=CSV_ENCODING)
    return path


def save_text(text, output_dir, filename):
    '''summary.txt에 사용할 폴더'''
    path = ensure_dir(output_dir) / filename
    with open(path, "w", encoding=TEXT_ENCODING) as f:
        f.write(text)
    return path
