# Q
지금 miniproject1 폴더 안에 '비전검사 로그 통합 처리 프로그램 개발'이라는 pdf에 개요와 요구사항 등이 쓰여 있어. 일단은 이 pdf에 쓰여있는 내용을 기반으로 파이썬 코드를 써줘.



# A
PDF 요구사항(F1~F11, D1~D7, S1~S6, O1·O2)을 확인했고, 설정 파일과 읽기·저장 모듈을 작성했습니다. 이제 집계 모듈을 작성하고 있습니다.

처리 프로그램은 실행·검증을 마쳤습니다. 지금은 Dash 화면(app.py)을 정리하고 띄워서 확인하는 중입니다.

Dash 화면을 브라우저에 띄웠고, 로딩이 끝난 뒤 화면이 제대로 그려지는지 확인하는 중입니다.

Now README, then re-run the full pipeline to refresh outputs.

PDF의 요구사항대로 코드를 작성했습니다. 제공된 데이터로 처리 프로그램과 Dash 화면을 둘 다 실행했고, 정상 동작하는 것까지 확인했습니다.

## 파일 구성
- [main.py](main.py): 전체 처리를 명령 한 줄로 실행합니다 (S6).
- [app.py](app.py): Dash 화면입니다. 로그는 앱을 시작할 때 한 번만 읽고, 집계는 모듈 함수를 불러서 합니다 (D1~D7).
- [config.json](config.json): 입력 폴더, 출력 폴더, 처리 시간 기준값 같은 설정입니다. 명령 인자로도 바꿀 수 있습니다 (S2).
- [vision_log/](vision_log/): 역할별 모듈입니다 (S1).
  - `loader`: 읽기·합치기·불량코드 결합
  - `analysis`: 집계·필터·요약
  - `charts`: 그래프
  - `writer`: 저장
- [README.md](README.md): 설치 방법, 실행 방법, 설정 항목, 출력 파일 설명입니다.

## 실행 방법
```powershell
python main.py
```
```powershell
python main.py --facility A시설 C시설 --start 2026-11-17 --end 2026-11-18 --defect D01 찍힘
```
```powershell
python app.py
```

## 확인한 내용
- **처리 결과**: 전체 5,198건 중 불량 238건으로, 불량률은 4.58%입니다. 불량률이 가장 높은 시설은 A시설(5.14%), 가장 많은 불량 종류는 스크래치(77건), 이상 기록은 11건입니다. 시설별 원본 CSV에서 직접 센 숫자와 일치합니다.
- **문제 있는 파일 건너뛰기(S4)**: 열이 없는 파일, 인코딩이 깨진 파일, 빈 파일을 일부러 섞어 넣고 실행했습니다. 프로그램은 멈추지 않고 세 파일을 건너뛰었고, 그 이유가 `run_log.txt`에 기록됐습니다.
- **그래프(F10)**: PNG 두 개 모두 제목, 축 이름, 범례의 한글이 깨지지 않습니다. 맑은 고딕 글꼴을 자동으로 찾아 씁니다.
- **Dash 화면**: 시설 선택을 바꾸면 요약 숫자, 그래프, 표가 모두 다시 계산되고, 브라우저 콘솔 오류도 없었습니다.
- **Dash 설치**: 이 PC에 Dash가 없어서 `pip install dash`로 설치했습니다.

## 설계상 정한 부분
README에도 적어 두었습니다.
- **판정 불가(D99)**: 결과가 NG이므로 불량 수에 포함했습니다.
- **Dash에서 불량 종류를 골랐을 때**: 검사 수는 그대로 두고, 고른 불량 종류만 불량으로 세어 불량률을 냅니다. 이상 기록 표에는 시설과 날짜 조건만 적용합니다.
- **선택 요구사항 O2의 판단 기준**: 같은 카메라의 "그날을 뺀 나머지 날" 불량률을 평소 값으로 삼았습니다. 아래 세 조건을 모두 만족하면 급증으로 봅니다.
  - 그날 불량이 5건 이상
  - 그날 불량률이 평소의 2배 이상
  - z 점수가 3 이상 (우연으로 보기 어려운 차이)

## 데이터에서 보인 특이 사항
발표 때 쓸 수 있습니다.
- **11-20 A-CAM1**: 10시대에 판정 불가(D99)가 11건 연달아 나왔습니다. 모두 처리 시간 5000ms, 신뢰도 0이라 카메라나 시스템 장애로 보입니다. 처리 시간이 기준을 넘은 기록은 모두 이 D99 기록이었습니다.
- **11-18 B시설**: 이물이 15건 몰렸습니다.
- **11-19 C시설**: 카메라 두 대 모두에서 치수 초과가 급증했습니다.

PDF의 제출물 중 **AI 사용 기록**은 직접 정리하셔야 하는 문서라 만들지 않았습니다. 코드는 발표에서 직접 설명하셔야 하니 한 번 읽어 보시고, 궁금한 부분은 물어봐 주세요.


# Q
이제 3페이지부터 요구사항이 있어. 필수 요구사항인 F1\~F11, 화면 요구사항인 D1\~D7, 프로그램 구성 요구사항이 S1\~s6까지 있어. 혹시 각각의 요구사항을 어떻게 구현했는지 설명해줄 수 있어?

# A
요구사항 번호 순서대로 정리했습니다. 각 함수 이름을 누르면 해당 코드 위치로 이동합니다.

## 필수 기능 (F1~F11)

| 번호 | 구현 위치 | 방법 |
|---|---|---|
| F1 | [find_log_files](vision_log/loader.py:40), [read_all_logs](vision_log/loader.py:80) | `Path(input_dir).glob("facility_*.csv")`로 입력 폴더에서 이름이 맞는 파일을 모두 찾습니다. 파일 이름이나 개수는 코드에 적지 않았습니다. 앞부분 `facility_`도 config의 `log_file_prefix`에서 가져옵니다. 그래서 `facility_D_log.csv`를 넣기만 해도 자동으로 읽힙니다. |
| F2 | [merge_logs](vision_log/loader.py:90), [main.py:36](main.py:36) | `pd.concat`으로 합친 뒤 `timestamp` 기준으로 정렬합니다. 시각이 같으면 시설, 카메라 순으로 정렬합니다. 정렬 전에 [read_log_file](vision_log/loader.py:47)에서 timestamp를 datetime으로 바꿔 두므로 문자열이 아니라 실제 시각 순서로 정렬됩니다. 결과는 `all_facility_log.csv`로 저장합니다. |
| F3 | [attach_defect_info](vision_log/loader.py:112) | `defect_code`를 키로 불량코드표를 `merge(how="left")`합니다. 그러면 `defect_name`, `category`, `severity` 열이 붙습니다. left join이므로 OK 기록(코드가 빈칸)도 빠지지 않습니다. 불량코드표에 없는 코드는 '미등록'으로 표시하고 실행 로그에 경고를 남깁니다. |
| F4 | [facility_summary](vision_log/analysis.py:68) | 공통 함수 [_rate_table](vision_log/analysis.py:50)이 `groupby` 뒤 `size`(검사 수)와 `sum`(NG 개수)을 구합니다. 불량률은 [defect_rate](vision_log/analysis.py:41)에서 `불량수/검사수*100`을 계산하고 `round(2)`합니다. 검사 수가 0이면 0%로 둡니다. 맨 아래에 합계 행을 붙입니다. |
| F5 | [facility_defect_table](vision_log/analysis.py:81), [category_table](vision_log/analysis.py:101) | NG 행만 골라 `pd.crosstab(시설, 불량이름)`으로 시설 x 불량 종류 표를 만듭니다. 열은 불량 코드 순서(D01→D99)로 정렬하고 합계 행과 열을 붙입니다. 분류별 표는 `groupby("category")`로 건수와 비율을 냅니다. |
| F6 | [daily_facility_summary](vision_log/analysis.py:122) | timestamp에서 날짜 문자열을 만든 뒤 F4와 같은 `_rate_table`을 `[날짜, 시설]` 키로 호출합니다. |
| F7 | [camera_summary](vision_log/analysis.py:127) | 같은 `_rate_table`을 `[시설, 카메라]` 키로 호출합니다. F4, F6, F7이 함수 하나를 함께 쓰므로 불량률 계산 방식이 항상 같습니다. |
| F8 | [find_anomalies](vision_log/analysis.py:133) | `defect_code == "D99"` 또는 `process_ms > 기준값`인 행을 고릅니다. 기준값은 인자로 받습니다. 왜 이상 기록인지 알 수 있도록 맨 앞에 `이상 사유` 열을 붙입니다. |
| F9 | [filter_records](vision_log/analysis.py:147), [main.py:62](main.py:62) | 처음에는 모든 행이 True인 마스크를 만듭니다. 그다음 값이 주어진 조건만 `&`로 더합니다. 그래서 조건을 일부만 주어도 동작합니다. 끝 날짜는 그날 하루 전체를 포함하도록 `< 끝날짜+1일`로 비교합니다. 불량 종류는 코드(D01)나 이름(찍힘) 어느 쪽으로 줘도 됩니다. 조건은 명령 인자 `--facility --start --end --defect`나 config에서 받습니다. |
| F10 | [charts.py](vision_log/charts.py:25) | matplotlib으로 묶은 막대그래프와 꺾은선그래프를 그려 PNG로 저장합니다. 한글 깨짐은 [set_korean_font](vision_log/charts.py:14)에서 막습니다. 설치된 글꼴 중 맑은 고딕(Windows)이나 AppleGothic(Mac)을 찾아 지정하고, `axes.unicode_minus=False`로 음수 부호도 깨지지 않게 했습니다. |
| F11 | [build_summary](vision_log/analysis.py:167), [format_summary](vision_log/analysis.py:200) | 요약 숫자는 위의 집계 함수들을 다시 써서 만듭니다. 최고 불량률 시설은 F4 결과를 정렬해서, 최다 불량 종류는 [defect_type_counts](vision_log/analysis.py:110) 결과에서 구합니다. 텍스트로 만든 요약은 `summary.txt`로 저장하고 `print`로 화면에도 출력합니다. |

## 화면 (D1~D7)

| 번호 | 구현 위치 | 방법 |
|---|---|---|
| D1 | [app.py:236](app.py:236) | `python app.py`를 실행하면 `app.run()`으로 서버가 뜹니다. 접속 주소는 화면에 출력됩니다. |
| D2 | [app.py:96~106](app.py:96) | 시설은 `dcc.Checklist`(여러 개 선택), 날짜는 `dcc.DatePickerRange`, 불량 종류는 `dcc.Dropdown(multi=True)`로 골라야 합니다. 선택지는 하드코딩하지 않고 읽은 데이터와 불량코드표에서 만듭니다. CSS `position: sticky`를 써서 스크롤을 내려도 선택 영역이 위에 붙어 있습니다. |
| D3 | [app.py:112](app.py:112) | 카드 네 개(검사 수, 불량 수, 불량률, 이상 기록 수)에 콜백 결과를 넣습니다. |
| D4 | [app.py:120](app.py:120) | plotly로 시설별 불량 종류 막대그래프와 날짜별 불량률 꺾은선그래프를 표시합니다. |
| D5 | [app.py:125](app.py:125) | `dash_table.DataTable`로 시설 x 불량 종류 표와 이상 기록 표를 보여 줍니다. 두 표 모두 정렬과 페이지 넘김이 됩니다. |
| D6 | [update 콜백](app.py:155) | 선택 요소 네 개(시설, 시작일, 종료일, 불량 종류)를 `Input`으로 받습니다. 카드, 그래프, 표 전부를 `Output`으로 묶었으므로, 무엇을 바꿔도 함수 하나가 다시 실행되어 전부 새로 계산됩니다. |
| D7 | [app.py:35](app.py:35), [update](app.py:178) | 로그는 모듈 최상단에서 `load_dataset()`으로 한 번만 읽어 `DF`에 둡니다. 콜백은 `analysis.filter_records`, `facility_summary` 같은 모듈 함수만 부릅니다. |

## 프로그램 구성 (S1~S6)

| 번호 | 구현 위치 | 방법 |
|---|---|---|
| S1 | [vision_log/](vision_log/) 패키지 | 역할별로 파일을 나눴습니다. 읽기와 합치기는 `loader.py`, 집계는 `analysis.py`, 저장은 `writer.py`, 그래프는 `charts.py`에 있습니다. 실행 파일 `main.py`와 `app.py`는 이 함수들을 순서대로 부르기만 합니다. |
| S2 | [load_config](vision_log/config.py:33), [main.py:16](main.py:16) | 설정 값은 "기본값 ← config.json ← 명령 인자" 순서로 덮어씁니다. 그래서 `--input`, `--output`, `--threshold`를 주면 config 값보다 우선합니다. |
| S3 | [ensure_dir](vision_log/writer.py:11) | `mkdir(parents=True, exist_ok=True)`를 씁니다. CSV, 텍스트, PNG, 로그 파일을 저장할 때마다 이 함수를 거치므로 출력 폴더가 없어도 자동으로 만들어집니다. |
| S4 | [read_log_file](vision_log/loader.py:47), [setup_logger](vision_log/loader.py:23) | 읽기를 `try/except`로 감싸서 인코딩 오류, 빈 파일, 파싱 오류가 나면 None을 돌려주고 건너뜁니다. 필요한 열이 빠진 파일도 건너뜁니다. 건너뛴 파일과 이유는 `logging`으로 `run_log.txt`에 남깁니다. 지난번에 깨진 파일 세 개를 섞어 넣고 실제로 확인했습니다. |
| S5 | 모든 `read_csv`, `to_csv`, `open`, `FileHandler` | 모든 파일 입출력에 인코딩을 지정했습니다. 입력은 `utf-8-sig`(BOM 포함)로 읽습니다. CSV 저장도 [`utf-8-sig`](vision_log/writer.py:20)로 해서 엑셀에서 한글이 깨지지 않습니다. 텍스트, 설정, 로그 파일은 `utf-8`입니다. |
| S6 | [main.py](main.py) | `python main.py` 한 줄로 F1~F11 전체가 순서대로 실행됩니다. |

## 발표 전에 알아 두면 좋은 점
질문이 나올 수 있는 부분입니다.

- **불량 종류를 골랐을 때(D3, D6)**: 검사 수는 시설·날짜 기준으로 그대로 두고, 고른 종류만 불량으로 셉니다. 불량 종류로 행 자체를 걸러 내면 남는 행이 모두 불량이라 불량률이 항상 100%가 되기 때문입니다. 이 동작은 각 집계 함수의 `defect_codes` 인자와 [defect_mask](vision_log/analysis.py:32)가 처리합니다.
- **app.py에 남은 데이터 처리(D7)**: 집계는 아니지만 표를 그래프용으로 바꾸는 `melt`와 DataTable용 변환(`to_table`)이 app.py 안에 있습니다. 화면에 맞게 모양만 바꾸는 코드이므로 집계는 아니라고 설명하시면 됩니다. 더 엄격하게 맞추려면 이것도 모듈로 옮길 수 있습니다.
- **S4의 빈틈**: 건너뛰기는 시설 로그 파일에만 적용됩니다. 불량코드표(`defect_codes.csv`) 자체가 없거나 깨져 있으면 결과를 낼 수 없으므로, 오류를 로그에 남기고 종료합니다.


# Q
그러면 이제 모든 파일의 함수에 대한 설명을 하나하나씩 해줄 수 있어?


# A
파일별로, 각 함수가 **무엇을 받아서(입력) 무엇을 돌려주는지(출력)**, 그리고 **안에서 어떻게 동작하는지** 순서로 설명하겠습니다. 다른 파일에 기대지 않는 아래 계층부터 올라갑니다.

---

## 1. `vision_log/config.py` — 설정 처리 (S2)

파일 맨 위의 **`DEFAULT_CONFIG`**는 모든 설정의 기본값을 담은 dict입니다. config.json이 없거나 일부 항목이 빠져 있어도 프로그램이 돌아가게 하는 안전장치입니다.

### `_deep_update(base, new)`
- **입력**: 기본 설정 dict `base`, 덮어쓸 dict `new`
- **출력**: 덮어쓴 `base`
- **동작**: `new`의 값을 `base`에 덮어씁니다. 값이 dict이면(예: `filter`, `spike`) 통째로 바꾸지 않고 안으로 들어가 항목별로 덮어씁니다(재귀 호출).
  - 그래서 config.json에 `"spike": {"min_defects": 3}`만 적어도 `rate_ratio`와 `z_score`는 기본값이 그대로 남습니다.
  - 이름 앞의 `_`는 "모듈 안에서만 쓰는 함수"라는 파이썬 관례입니다.

### `load_config(path="config.json", overrides=None)`
- **입력**: 설정 파일 경로, 명령 인자로 받은 값 `overrides`
- **출력**: 최종 설정 dict
- **동작**: 세 단계로 합칩니다. 뒤 단계가 앞 단계를 덮어씁니다.
  1. `DEFAULT_CONFIG`를 `copy.deepcopy`로 복사합니다. 원본 기본값이 바뀌지 않게 하기 위해서입니다.
  2. 설정 파일이 있으면 `encoding="utf-8"`로 읽어 `_deep_update`로 덮어씁니다.
  3. `overrides`에서 **값이 None이 아닌 것만** 덮어씁니다. 명령 인자를 안 준 항목은 argparse가 None으로 넘기므로, 이렇게 해야 설정 파일 값이 지워지지 않습니다. `filter`는 안쪽 항목별로 따로 처리합니다.

---

## 2. `vision_log/writer.py` — 저장 (S3, S5)

파일 위의 상수 `CSV_ENCODING = "utf-8-sig"`, `TEXT_ENCODING = "utf-8"`로 저장 인코딩을 한 곳에서 관리합니다.

### `ensure_dir(path)`
- **입력**: 폴더 경로 / **출력**: `Path` 객체
- **동작**: `mkdir(parents=True, exist_ok=True)`를 씁니다.
  - `parents=True`: 중간 폴더까지 한꺼번에 만듭니다(예: `a/b/c`).
  - `exist_ok=True`: 폴더가 이미 있어도 오류를 내지 않습니다.
  - 이 함수가 S3(출력 폴더 자동 생성)의 핵심입니다.

### `save_csv(df, output_dir, filename, index=False)`
- **입력**: DataFrame, 폴더, 파일 이름 / **출력**: 저장한 경로
- **동작**: `ensure_dir`로 폴더를 보장한 뒤 `to_csv(..., encoding="utf-8-sig")`로 저장합니다.
  - `utf-8-sig`는 파일 맨 앞에 BOM(EF BB BF)을 붙입니다. 엑셀이 BOM을 보고 UTF-8로 인식하므로 한글이 깨지지 않습니다(S5).
  - `index=False`는 pandas의 행 번호(0, 1, 2…)를 저장하지 않는다는 뜻입니다.

### `save_text(text, output_dir, filename)`
- **동작**: `open(..., "w", encoding="utf-8")`로 텍스트를 저장합니다. `summary.txt`에 씁니다.

---

## 3. `vision_log/loader.py` — 읽기·합치기·결합 (F1~F3, S4)

파일 위에 상수가 넷 있습니다.
- `LOG_COLUMNS`: 시설 로그에 반드시 있어야 하는 14개 열
- `DEFECT_CODE_COLUMNS`: 불량코드표에 반드시 있어야 하는 4개 열
- `NUMERIC_COLUMNS`: 숫자로 바꿀 열
- `logger`: 프로그램 전체가 함께 쓰는 로거

### `setup_logger(output_dir, filename="run_log.txt")`
- **동작**: 로그를 **두 곳**에 동시에 남기도록 설정합니다.
  - `FileHandler(..., mode="w", encoding="utf-8")`: 실행 로그 파일입니다. `"w"`라서 실행할 때마다 새로 씁니다.
  - `StreamHandler`: 콘솔 화면입니다.
- `handlers.clear()`를 먼저 하는 이유: 같은 프로세스에서 두 번 호출되면 핸들러가 쌓여 로그가 중복 출력되기 때문입니다.
- 형식은 `시각 [수준] 메시지`입니다.

### `find_log_files(input_dir, prefix="facility_")`
- **출력**: 파일 경로 목록 (F1)
- **동작**: `Path(input_dir).glob("facility_*.csv")`로 패턴에 맞는 파일을 모두 찾고, `sorted`로 순서를 고정합니다.
  - 파일 이름을 코드에 적지 않으므로 시설 파일이 늘어도 코드를 고칠 필요가 없습니다.
  - glob은 하위 폴더를 뒤지지 않습니다. 그래서 `output/` 안의 파일이 섞여 들어오지 않습니다.

### `read_log_file(path)` — S4의 핵심
- **출력**: 정리된 DataFrame, 또는 건너뛸 때 `None`
- **동작 순서**:
  1. `pd.read_csv(..., encoding="utf-8-sig", dtype=str)`로 읽습니다.
     - `utf-8-sig`는 BOM을 자동으로 떼어 줍니다. BOM이 남으면 첫 열 이름이 `\ufefftimestamp`가 되어 열 검사에 실패합니다.
     - `dtype=str`로 일단 전부 문자열로 읽습니다. 숫자 변환은 뒤에서 직접 통제하기 위해서입니다.
  2. `try/except Exception`으로 읽기를 감쌉니다. 인코딩 오류, 빈 파일(`EmptyDataError`), 형식 오류 같은 문제가 생기면 경고 로그를 남기고 `None`을 돌려줍니다. 프로그램은 멈추지 않습니다.
  3. 열 이름의 공백을 `strip`으로 지운 뒤, 필요한 열 중 없는 열 목록을 구합니다. 하나라도 빠졌으면 경고 로그를 남기고 `None`을 돌려줍니다.
  4. 정리 작업을 합니다.
     - 문자열 열의 앞뒤 공백을 제거합니다.
     - `result`를 대문자로 바꿉니다. "ng"처럼 섞여 들어와도 처리하기 위해서입니다.
     - `timestamp`를 `pd.to_datetime(format=..., errors="coerce")`로 바꿉니다. 형식이 틀린 값은 오류 대신 `NaT`가 됩니다.
     - 숫자 열은 `pd.to_numeric(errors="coerce")`로 바꿉니다. 빈칸은 `NaN`이 됩니다.
  5. 시각을 해석할 수 없는 줄은 개수를 로그에 남기고 제외합니다.
  6. 어느 파일에서 왔는지 `source_file` 열에 기록합니다.

### `read_all_logs(input_dir, prefix)`
- **동작**: `find_log_files`로 찾은 파일마다 `read_log_file`을 호출하고, `None`이 아닌 것만 목록에 모아 돌려줍니다. 건너뛰는 처리가 여기서 완성됩니다.

### `merge_logs(frames)` (F2)
- **동작**:
  - 목록이 비어 있으면, 즉 읽을 수 있는 파일이 하나도 없으면 `ValueError`를 냅니다.
  - `pd.concat(ignore_index=True)`로 위아래로 합칩니다. 행 번호는 새로 매깁니다.
  - `sort_values(["timestamp", "facility", "camera_id"], kind="stable")`로 정렬합니다. 시각이 같으면 시설, 카메라 순입니다. `stable`은 값이 완전히 같은 행끼리 원래 순서를 유지하는 정렬 방식입니다.

### `read_defect_codes(path)`
- **동작**: 불량코드표를 읽고 열을 검사한 뒤, 모든 값의 공백을 제거하고 코드 순으로 정렬합니다.
  - 이 파일은 없으면 결과를 낼 수 없으므로, 시설 로그와 달리 건너뛰지 않고 오류를 냅니다.

### `attach_defect_info(logs, defect_codes)` (F3)
- **동작**:
  - `logs.merge(defect_codes, on="defect_code", how="left")`로 불량 이름, 분류, 심각도 열을 붙입니다.
  - `how="left"`인 이유: 로그 쪽 행을 하나도 잃지 않기 위해서입니다. OK 기록은 코드가 빈칸이라 짝이 없지만, left join이라 남고 새 열만 빈칸이 됩니다.
  - 불량코드표에 없는 코드(코드는 있는데 이름이 빈칸)는 `미등록(Dxx)`로 채우고 경고 로그를 남깁니다.

### `load_dataset(config)`
- **출력**: (전체 로그, 불량코드표)
- **동작**: 위 함수들을 순서대로 부르는 묶음 함수입니다. 읽기 → 합치기 → 코드표 읽기 → 결합 순입니다. `main.py`와 `app.py`가 둘 다 이 함수 하나만 부르면 됩니다.

---

## 4. `vision_log/analysis.py` — 집계 (F4~F9, F11, O1, O2)

파일 위의 상수는 둘로 나뉩니다.
- `COL_FACILITY="시설"`, `COL_RATE="불량률(%)"` 등은 결과 표의 열 이름입니다. 오타를 막고, `app.py`나 `charts.py`에서도 같은 이름을 쓰기 위해 상수로 뒀습니다.
- `IMAGE_WIDTH/HEIGHT`는 사진 크기(1280×1024)입니다.

### 공통 함수

**`_as_list(value)`**
- 사용자가 조건을 `"A시설"`처럼 하나만 주거나 `["A시설", "B시설"]`처럼 여러 개 줄 수 있어서, 항상 리스트로 통일합니다.
- None이나 빈 리스트는 `None`으로 돌려줍니다. 뒤에서 "조건 없음"으로 판단하기 위해서입니다.

**`defect_mask(df, defect_codes=None)`**
- **출력**: 행마다 불량인지 아닌지를 담은 True/False Series
- **동작**:
  - 기본은 `result == "NG"`입니다.
  - `defect_codes`를 주면, 그 코드나 이름에 해당하는 행만 True로 남도록 `&`로 조건을 더합니다.
  - `defect_code.isin(...) | defect_name.isin(...)`로 비교하므로 `D01`이나 `스크래치` 어느 쪽으로 줘도 됩니다.
- 모든 집계가 이 함수로 "불량"을 판단하므로, 불량의 정의가 한 곳에만 있습니다.

**`defect_rate(defects, inspections)`**
- **동작**: `불량/검사×100`을 계산하고 `np.round(..., 2)`로 소수 둘째 자리까지 반올림합니다.
  - 검사 수가 0이면 0으로 둡니다(`np.where`). Dash에서 시설을 하나도 고르지 않았을 때 0으로 나누는 오류를 막습니다.
  - 숫자 하나든 열 전체든 모두 처리할 수 있도록 numpy 배열로 바꿔 계산합니다.

**`_rate_table(df, keys, key_names, defect_codes=None)`** — F4, F6, F7이 함께 쓰는 엔진
- **동작**:
  1. `_ng` 열(불량 여부)을 임시로 붙입니다.
  2. `groupby(keys)["_ng"].agg(검사수="size", 불량수="sum")`로 집계합니다. `size`는 행 수, `sum`은 True의 개수(True=1)입니다.
  3. 영어 키 열 이름을 한글로 바꾸고, 불량률 열을 추가합니다.
- 키만 바꾸면 시설별, 날짜·시설별, 카메라별 집계가 모두 나옵니다.

**`_with_date(df)`**
- timestamp에서 `"2026-11-16"` 형식의 `date` 열을 만들어 붙인 복사본을 돌려줍니다.

### 필수 기능

**`facility_summary(df, defect_codes=None)`** (F4)
- `_rate_table(df, ["facility"], ...)`로 시설별 표를 만듭니다.
- 합계 행은 검사 수와 불량 수를 더한 뒤 불량률을 **다시 계산**합니다. 시설별 불량률의 평균을 내면 검사 수가 다를 때 값이 틀리기 때문입니다.

**`facility_defect_table(df, defect_codes=None)`** (F5)
- **동작**:
  1. 불량 행만 고릅니다.
  2. `pd.crosstab(시설, 불량이름)`으로 교차표를 만듭니다.
  3. `reindex`로 행과 열을 맞춥니다.
     - 행: 불량이 0건인 시설도 표에 나오도록 모든 시설을 넣습니다.
     - 열: 불량 코드 순서(D01→D99)로 정렬합니다. 이름순이면 가나다순이 되어 버리기 때문입니다.
  4. `sum(axis=1)`로 합계 열을, `sum(axis=0)`으로 합계 행을 붙입니다.

**`category_table(df, defect_codes=None)`** (F5)
- 불량 행을 `category`로 묶어 건수를 세고, 많은 순으로 정렬한 뒤 전체 대비 비율(%)을 붙입니다.

**`defect_type_counts(df, defect_codes=None)`**
- 불량 종류별 건수를 코드, 이름, 분류, 심각도와 함께 많은 순으로 정렬합니다.
- F11의 "가장 많이 발생한 불량 종류"를 구하는 데 씁니다.
- `dropna=False`는 미등록 코드처럼 분류가 빈칸인 행도 빠뜨리지 않기 위한 설정입니다.

**`daily_facility_summary(df, defect_codes=None)`** (F6)
- `_with_date`로 날짜 열을 만든 뒤 `_rate_table`을 `[date, facility]` 키로 호출합니다.

**`camera_summary(df, defect_codes=None)`** (F7)
- `_rate_table`을 `[facility, camera_id]` 키로 호출합니다.

**`find_anomalies(df, threshold_ms=1000)`** (F8)
- **동작**:
  1. 조건 마스크 두 개를 만듭니다: `is_d99`(D99 여부), `is_slow`(처리 시간 > 기준값)
  2. 둘 중 하나라도 해당하는 행을 고릅니다(`|`).
  3. `이상 사유` 문자열을 만듭니다. D99 문구와 지연 문구를 만들고, **둘 다 해당하는 행만** 사이에 `", "`를 넣어 이어 붙입니다.
  4. `insert(0, ...)`로 이 열을 맨 앞에 넣습니다.
- 처음에는 `apply`로 만들었는데, 결과가 0건일 때 오류가 나서 numpy 배열 방식으로 바꿨습니다. Dash에서 B시설만 고르면 0건이 됩니다. AI 사용 기록에 쓸 만한 수정 사례입니다.

**`filter_records(df, facilities, start_date, end_date, defect_codes)`** (F9)
- **동작**:
  - 처음에는 모든 행이 True인 마스크로 시작합니다. 주어진 조건만 `&=`로 하나씩 더해 갑니다. 그래서 조건 일부만 줘도 동작합니다.
  - 시작일 비교: `>= 시작일 00:00`
  - 종료일 비교: `< 종료일+1일 00:00`. 그냥 `<= 종료일`로 비교하면 그날 00:00:00까지만 포함되어 하루치가 통째로 빠지기 때문입니다.
  - 불량 종류 조건은 `defect_mask`를 재사용합니다.

**`build_summary(df, threshold_ms, spikes=None)`** (F11)
- 요약 숫자를 dict로 모읍니다. 직접 세지 않고 위 함수들을 재사용합니다.
  - 전체 검사 수: `len(df)`
  - 불량 수: `defect_mask(df).sum()`
  - 최고 불량률 시설: `facility_summary` 결과에서 합계 행을 빼고 불량률로 정렬한 첫 행
  - 최다 불량 종류: `defect_type_counts`의 첫 행
  - 이상 기록 수: `find_anomalies` 결과의 행 수
  - 기간: 최소~최대 timestamp
- 데이터가 비어 있을 때를 대비해 기본값은 None과 0으로 둡니다.

**`format_summary(summary, threshold_ms)`** (F11)
- dict를 사람이 읽을 텍스트 줄들로 만들어 `"\n".join`으로 합칩니다.
- `:,`는 천 단위 쉼표, `:.2f`는 소수 둘째 자리 표시입니다.
- 급증 감지 결과가 있으면 한 줄씩 덧붙입니다.

### 선택 기능

**`add_box_features(df)`** (O1)
- **동작**:
  1. 박스 좌표가 있는 행만 남깁니다(`dropna`). OK나 D99 행은 좌표가 없습니다.
  2. 너비 = `x2-x1`, 높이 = `y2-y1`, 면적 = 너비×높이, 중심 = `((x1+x2)/2, (y1+y2)/2)`를 계산합니다.
  3. `pd.cut`으로 중심 좌표를 3등분 구간에 넣어 가로(좌/중/우)와 세로(상/중/하)를 정하고, `"중-우"` 같은 위치 이름을 붙입니다.

**`box_stats(df)`** (O1)
- 불량 종류별로 묶어 다음을 계산하고 소수 첫째 자리로 반올림합니다.
  - 건수
  - 평균 너비, 높이, 면적
  - 중심점의 평균과 표준편차. 표준편차는 위치가 얼마나 퍼져 있는지를 보여 줍니다.
  - 가장 많이 나온 위치(`value_counts().idxmax()`)

**`box_region_table(df)`** (O1)
- 불량 종류 × 9개 구역 교차표입니다. 건수가 0인 구역도 열로 나오게 `reindex`합니다.

**`detect_spikes(df, min_defects, rate_ratio, z_score, defect_codes)`** (O2)
- **동작**:
  1. 날짜·시설·카메라별 검사 수 `n`과 불량 수 `ng`를 셉니다.
  2. `groupby(...).transform("sum")`으로 카메라별 5일 전체 합계를 **각 행 옆에** 붙입니다.
  3. 평소 불량률 `p0` = (전체 불량 − 그날 불량) / (전체 검사 − 그날 검사)입니다. 그날을 빼는 이유는, 그날의 급증이 기준값까지 끌어올려 급증이 작게 보이는 것을 막기 위해서입니다.
  4. z 점수 = `(p − p0) / √(p0(1−p0)/n)`입니다. 평소 불량률이 p0일 때 그날 n건을 검사하면 우연히 생기는 변동 폭(표준오차)에 비해 실제 차이가 몇 배인지를 나타냅니다.
  5. 세 조건을 모두 만족하는 행만 남깁니다: 불량 5건 이상, 평소의 2배 이상, z 3 이상.
  6. 그날 많이 나온 불량 종류 상위 3개를 `주요 불량` 열로 붙여서 원인 단서를 줍니다.
  7. 열 이름을 한글로 바꾸고 배수 열을 추가한 뒤 정렬합니다.

---

## 5. `vision_log/charts.py` — 그래프 (F10)

`matplotlib.use("Agg")`는 창을 띄우지 않고 파일로만 그리는 백엔드입니다. 서버나 콘솔 환경에서도 오류 없이 저장하려고 지정했습니다.

### `set_korean_font()`
- **동작**:
  - matplotlib에 등록된 글꼴 목록에서 `KOREAN_FONTS` 후보를 순서대로 찾아 처음 발견한 것을 기본 글꼴로 지정합니다. 후보는 맑은 고딕(Windows), AppleGothic(Mac), 나눔고딕 등입니다.
  - `axes.unicode_minus=False`도 설정합니다. 한글 글꼴에는 유니코드 마이너스 기호(−)가 없어 네모로 깨지는 경우가 있기 때문입니다.

### `plot_facility_defects(table, output_dir, filename)`
- **입력**: `facility_defect_table`의 결과
- **동작**:
  1. 합계 행과 열을 빼고 시설을 인덱스로 둡니다.
  2. `data.plot(kind="bar")`로 그립니다. pandas가 열(불량 종류)마다 막대를 하나씩 그려 묶은 막대그래프가 됩니다.
  3. 제목, 축 이름, 범례 제목을 붙입니다. 범례는 막대를 가리지 않도록 그래프 바깥 오른쪽(`bbox_to_anchor`)에 둡니다.
  4. `savefig(dpi=150)`로 저장하고 `plt.close(fig)`로 메모리를 해제합니다.

### `plot_daily_rate(daily, output_dir, filename)`
- **입력**: `daily_facility_summary`의 결과
- **동작**:
  1. `pivot`으로 행=날짜, 열=시설, 값=불량률인 표로 바꿉니다.
  2. 시설마다 꺾은선을 하나씩 그립니다(`marker="o"`로 점 표시).
  3. `ylim(bottom=0)`으로 y축을 0부터 시작합니다. 변화가 과장되어 보이지 않게 하기 위해서입니다.

---

## 6. `main.py` — 전체 처리 실행 (S6)

### `parse_args(argv=None)`
- argparse로 명령 인자를 정의합니다.
  - `--config`, `--input`, `--output`, `--threshold`
  - F9 조건 그룹: `--facility`, `--start`, `--end`, `--defect`
- `nargs="+"`는 값을 여러 개 받는다는 뜻입니다(예: `--facility A시설 C시설`).
- `dest=`로 인자 이름을 config 키와 맞췄습니다.
- `argv` 인자를 받게 해 둔 것은 테스트할 때 인자 목록을 직접 넣을 수 있게 하기 위해서입니다.

### `run(config)`
- 요구사항 순서대로 함수를 부르는 처리 흐름 전체입니다.
  1. `setup_logger`로 실행 로그를 시작합니다.
  2. `load_dataset`으로 F1~F3을 처리합니다. 전체 로그는 `source_file` 열을 빼고 저장합니다.
  3. F4~F8과 O1, O2의 집계 결과를 `{파일이름: 표}` dict로 모은 뒤, 반복문 하나로 전부 저장합니다. 저장 코드를 반복해 쓰지 않으려는 구조입니다.
  4. F9: 조건이 하나라도 있을 때만 `filtered_records.csv`를 만듭니다. 조건이 없으면 만들지 않은 이유를 로그에 남깁니다.
  5. F10: 그래프 두 개를 저장합니다.
  6. F11: 요약을 만들어 파일로 저장하고 `print`로 화면에도 출력합니다.

### `main(argv=None)`
- **동작**:
  1. 인자를 파싱하고, `overrides` dict를 만들어 `load_config`에 넘깁니다.
  2. `run`을 `try/except`로 감쌉니다. 예상하지 못한 오류가 나면 `logger.exception`으로 오류 위치(traceback)까지 실행 로그에 남기고 종료 코드 1을 돌려줍니다.
- `sys.exit(main())`은 성공하면 0, 실패하면 1을 운영체제에 알립니다.

---

## 7. `app.py` — Dash 화면 (D1~D7)

### 모듈 최상단 (함수 밖) — D7의 "한 번만 읽기"
- `parse_args()`로 인자를 받습니다. `main.py`와 같은 방식이고 `--port`가 추가로 있습니다.
- `load_config`로 설정을 합친 뒤, `load_dataset`을 **여기서 한 번만** 호출해 `DF`, `CODES`에 둡니다.
  - 콜백은 이 전역 변수만 읽습니다. 그래서 선택을 바꿔도 파일을 다시 읽지 않습니다.
- 선택지도 데이터에서 만듭니다.
  - `FACILITIES`: 시설 목록
  - `MIN_DATE`, `MAX_DATE`: 날짜 범위
  - `DEFECT_OPTIONS`: `"D01 스크래치"` 형태의 불량 종류 목록

### `card(title, value_id)` / `table(table_id)` / `section(title, *children)`
- 화면 부품을 만드는 작은 도우미 함수입니다.
  - `card`: 요약 숫자 카드. 값 자리는 `"-"`로 두고, 콜백이 `id`로 채웁니다.
  - `table`: 공통 스타일(정렬 가능, 페이지당 10줄, 가로 스크롤)을 적용한 `DataTable`
  - `section`: 제목이 달린 흰 상자
- 같은 모양을 여러 번 쓰니 함수로 뺐습니다.

### `app.layout`
- 화면 배치를 위에서 아래 순서로 정의합니다.
  1. 선택 요소 (D2)
  2. 카드 4개 (D3)
  3. 그래프 2개 (D4)
  4. 표 2개 (D5)
  5. O1, O2 영역
- 각 요소에 붙인 `id`(예: `"f-facility"`, `"v-rate"`)가 콜백과 연결되는 이름입니다.
- `app.index_string`을 고쳐 CSS를 넣었습니다. 한글 글꼴과 카드 배치, 선택 영역 고정(sticky)이 여기서 정해집니다.

### `to_table(df)`
- DataFrame을 DataTable이 받는 형식 두 가지로 바꿉니다.
  - `data`: dict 목록(`to_dict("records")`)
  - `columns`: 열 정의
- timestamp는 datetime 그대로 넘기면 표시가 어색해서 문자열로 바꿉니다.
- 반환값이 두 개라서 콜백의 return에서 `*to_table(...)`로 펼쳐 씁니다.

### `update(facilities, start_date, end_date, defects)` — D6의 핵심
- `@app.callback`이 이 함수에 연결을 지정합니다.
  - **Input 4개**: 시설, 시작일, 종료일, 불량 종류
  - **Output 17개**: 카드 4개, 그래프 3개, 표 5개(표마다 data와 columns 두 개씩)
- 선택이 하나라도 바뀌면 Dash가 이 함수를 자동으로 다시 실행해 모든 Output을 갱신합니다.
- **동작**:
  1. 범위를 정합니다.
     - `scoped` = 시설·날짜로 거른 데이터
     - `picked` = 거기서 불량 종류까지 거른 데이터
     - 시설을 하나도 고르지 않으면 존재하지 않는 시설 이름 `["__none__"]`을 넘겨 빈 결과를 만듭니다. 빈 리스트를 넘기면 `filter_records`가 "조건 없음"으로 보고 전체를 돌려주기 때문입니다.
  2. 카드: `facility_summary(scoped, defects)`의 합계 행을 꺼냅니다. 불량 종류는 행을 거르지 않고 `defects` 인자로만 넘기므로, 검사 수는 유지되고 불량 수만 바뀝니다.
  3. 막대그래프: `facility_defect_table`의 넓은 표를 `melt`로 길게 펼쳐 `px.bar`에 넣습니다. plotly는 "시설, 불량 종류, 건수"처럼 긴 형식을 받기 때문입니다.
  4. 꺾은선그래프: `daily_facility_summary`의 결과를 `px.line`에 넣습니다. x축을 `category`로 지정해 날짜가 5개 눈금으로만 나오게 했습니다.
  5. O1 산점도: `add_box_features(picked)`로 중심점을 구해 그립니다. 점 크기는 면적입니다. y축을 `[1024, 0]`으로 뒤집은 이유는 사진 좌표계에서 위쪽이 0이기 때문입니다.
  6. O2: `detect_spikes`에 불량 종류 조건을 넘깁니다.
  7. 17개 값을 Output 순서대로 돌려줍니다.

### `if __name__ == "__main__":` (D1)
- `python app.py`로 직접 실행했을 때만 서버를 띄웁니다. 접속 주소를 출력하고 `app.run()`을 호출합니다.
- `debug=False`로 둔 이유: debug 모드에서는 자동 재시작 때문에 데이터를 두 번 읽게 되어 "한 번만 읽기"가 깨지기 때문입니다.

---

이 설명을 발표 자료나 AI 사용 기록에 쓰실 거라면 `docs/functions.md` 파일로도 정리해 드릴 수 있습니다.