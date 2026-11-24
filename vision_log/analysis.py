"""집계·필터·이상 기록·요약. (F4~F9, F11, O1, O2)

모든 집계 함수는 전체(또는 필터링된) 로그 DataFrame을 받아 결과 표를 돌려준다.
defect_codes 인자를 주면 '불량'을 그 불량 종류로만 한정해서 센다.
(검사 수는 그대로 두고 불량 수만 바뀌므로, 불량 종류별 불량률을 볼 수 있다.)
"""
import numpy as np
import pandas as pd

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 1024

COL_FACILITY = "시설"
COL_DATE = "날짜"
COL_CAMERA = "카메라"
COL_INSPECTIONS = "검사수"
COL_DEFECTS = "불량수"
COL_RATE = "불량률(%)"
TOTAL = "합계"


# ---------------------------------------------------------------- 공통
def _as_list(value):
    '''value를 [value] 형태로 반환'''
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    value = list(value)
    return value or None


def defect_mask(df, defect_codes=None):
    """**불량 여부 판정 함수**
    - 입력: 
        - `df`(검사할 데이터프레임)
        - `defect_codes`(불량 종류)
    - 출력:
        - `mask`: 불량 여부가 판정난 데이터프레임
    
    - 불량(NG) 여부. defect_codes를 주면 해당 불량 종류(코드 또는 이름)만 불량으로 본다."""
    mask = df["result"].eq("NG")
    codes = _as_list(defect_codes)
    if codes:
        mask &= df["defect_code"].isin(codes) | df["defect_name"].isin(codes)
    return mask


def defect_rate(defects, inspections):
    """**불량률 계산 함수**
    - 입력:
        - `defects`: 시설별 불량
        - `inspections`: 시설별 검사 수 
    - 출력:
        - `np.round(rate, 2)`: 불량률을 소수 둘째짜리까지 반환
    - 불량률: defects / insfections * 100
    
    불량률(%)을 소수 둘째 자리까지 계산한다. 검사 수가 0이면 0."""
    inspections = np.asarray(inspections, dtype=float) 
        # np.asarray(x, dtype=flaot): 입력을 실수형 numpy로 변경
    defects = np.asarray(defects, dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(inspections > 0, defects / inspections * 100, 0.0)
    return np.round(rate, 2)


def _rate_table(df, keys, key_names, defect_codes=None):
    '''### 집계 함수
    - 입력:
        - `df`: 집계할 데이터프레임
        - `keys`: 집계할 기준이 되는 데이터프레임의 열
        - `key_names`: 새로 집계를 할 데이터프레임의 열
    - 출력: 집계된 데이터프레임
    - groupby를 이용해 기존 데이터프레임 df를 
    - 검사 수 불량 수의 합계를 집계 후 반환
    '''

    work = df.assign(_ng=defect_mask(df, defect_codes))
    out = (
        work.groupby(keys)["_ng"]
        .agg(**{COL_INSPECTIONS: "size", COL_DEFECTS: "sum"})
        .reset_index()
        .rename(columns=dict(zip(keys, key_names)))
    )
    out[COL_DEFECTS] = out[COL_DEFECTS].astype(int)
    out[COL_RATE] = defect_rate(out[COL_DEFECTS], out[COL_INSPECTIONS])
    return out


def _with_date(df):
    '''데이터프레임의 timestamp 열을 \%Y-%\m-\%d 형식으로 반환'''
    return df.assign(date=df["timestamp"].dt.strftime("%Y-%m-%d"))


# ---------------------------------------------------------------- F4
def facility_summary(df, defect_codes=None):
    """
    시설별 검사 수, 불량 수, 불량률(%). 맨 아래에 합계 행을 붙인다."""
    out = _rate_table(df, ["facility"], [COL_FACILITY], defect_codes)
    total = pd.DataFrame([{
        COL_FACILITY: TOTAL,
        COL_INSPECTIONS: int(out[COL_INSPECTIONS].sum()),
        COL_DEFECTS: int(out[COL_DEFECTS].sum()),
    }])
    total[COL_RATE] = defect_rate(total[COL_DEFECTS], total[COL_INSPECTIONS])
    return pd.concat([out, total], ignore_index=True)


# ---------------------------------------------------------------- F5
def facility_defect_table(df, defect_codes=None):
    """시설(행) x 불량 종류(열) 불량 건수 표. 열 순서는 불량 코드 순, 합계 행·열 포함."""
    ng = df[defect_mask(df, defect_codes)]
    facilities = sorted(df["facility"].unique())
    order = (
        ng[["defect_code", "defect_name"]].drop_duplicates()
        .sort_values("defect_code")["defect_name"].tolist()
    )
    table = (
        pd.crosstab(ng["facility"], ng["defect_name"])
        .reindex(index=facilities, columns=order, fill_value=0)
        .astype(int)
    )
    table[TOTAL] = table.sum(axis=1)
    table.loc[TOTAL] = table.sum(axis=0)
    table.index.name = COL_FACILITY
    table.columns.name = None
    return table.reset_index()


def category_table(df, defect_codes=None):
    """불량 분류별 건수와 비율(%)."""
    ng = df[defect_mask(df, defect_codes)]
    out = ng.groupby("category").size().rename("불량수").reset_index()
    out = out.rename(columns={"category": "불량 분류"}).sort_values("불량수", ascending=False)
    out["비율(%)"] = defect_rate(out["불량수"], out["불량수"].sum())
    return out.reset_index(drop=True)


def defect_type_counts(df, defect_codes=None):
    """불량 종류별 건수 (코드, 이름, 분류, 심각도)."""
    ng = df[defect_mask(df, defect_codes)]
    out = (
        ng.groupby(["defect_code", "defect_name", "category", "severity"], dropna=False)
        .size().rename("불량수").reset_index()
        .sort_values(["불량수", "defect_code"], ascending=[False, True])
    )
    return out.reset_index(drop=True)


# ---------------------------------------------------------------- F6, F7
def daily_facility_summary(df, defect_codes=None):
    """날짜별·시설별 검사 수와 불량률."""
    return _rate_table(_with_date(df), ["date", "facility"], [COL_DATE, COL_FACILITY], defect_codes)


def camera_summary(df, defect_codes=None):
    """카메라별 검사 수와 불량률."""
    return _rate_table(df, ["facility", "camera_id"], [COL_FACILITY, COL_CAMERA], defect_codes)


# ---------------------------------------------------------------- F8
def find_anomalies(df, threshold_ms=1000):
    """판정 불가(D99)이거나 처리 시간이 기준값을 넘는 기록. '이상 사유' 열을 붙인다."""
    is_d99 = df["defect_code"].eq("D99")
    is_slow = df["process_ms"] > threshold_ms
    keep = is_d99 | is_slow
    out = df[keep].copy()
    d99_text = np.where(is_d99[keep], "판정 불가(D99)", "")
    slow_text = np.where(is_slow[keep], f"처리 지연(>{threshold_ms:g}ms)", "")
    sep = np.where(is_d99[keep] & is_slow[keep], ", ", "")
    out.insert(0, "이상 사유", [a + s + b for a, s, b in zip(d99_text, sep, slow_text)])
    return out.reset_index(drop=True)


# ---------------------------------------------------------------- F9
def filter_records(df, facilities=None, start_date=None, end_date=None, defect_codes=None):
    """시설, 날짜 범위(양 끝 포함), 불량 종류(코드 또는 이름)로 기록을 고른다.

    조건은 None이면 적용하지 않으므로 일부만 주어도 된다.
    불량 종류 조건을 주면 해당 불량 기록만 남는다.
    """
    mask = pd.Series(True, index=df.index)
    facilities = _as_list(facilities)
    if facilities:
        mask &= df["facility"].isin(facilities)
    if start_date:
        mask &= df["timestamp"] >= pd.Timestamp(start_date).normalize()
    if end_date:
        mask &= df["timestamp"] < pd.Timestamp(end_date).normalize() + pd.Timedelta(days=1)
    if _as_list(defect_codes):
        mask &= defect_mask(df, defect_codes)
    return df[mask]


# ---------------------------------------------------------------- F11
def build_summary(df, threshold_ms=1000, spikes=None):
    """요약 지표를 dict로 돌려준다."""
    total = len(df)
    defects = int(defect_mask(df).sum())
    by_fac = facility_summary(df)
    by_fac = by_fac[by_fac[COL_FACILITY] != TOTAL]
    by_type = defect_type_counts(df)

    summary = {
        "total_inspections": total,
        "total_defects": defects,
        "defect_rate": float(defect_rate(defects, total)),
        "worst_facility": None,
        "worst_facility_rate": None,
        "top_defect": None,
        "top_defect_count": 0,
        "anomaly_count": len(find_anomalies(df, threshold_ms)),
        "period": (
            f"{df['timestamp'].min():%Y-%m-%d} ~ {df['timestamp'].max():%Y-%m-%d}" if total else "-"
        ),
        "spikes": spikes,
    }
    if not by_fac.empty:
        worst = by_fac.sort_values(COL_RATE, ascending=False).iloc[0]
        summary["worst_facility"] = worst[COL_FACILITY]
        summary["worst_facility_rate"] = float(worst[COL_RATE])
    if not by_type.empty:
        top = by_type.iloc[0]
        summary["top_defect"] = f"{top['defect_name']}({top['defect_code']})"
        summary["top_defect_count"] = int(top["불량수"])
    return summary


def format_summary(summary, threshold_ms=1000):
    lines = [
        "===== 비전검사 로그 요약 =====",
        f"기간               : {summary['period']}",
        f"전체 검사 수       : {summary['total_inspections']:,}건",
        f"전체 불량 수       : {summary['total_defects']:,}건",
        f"전체 불량률        : {summary['defect_rate']:.2f}%",
        f"불량률 최고 시설   : {summary['worst_facility']} ({summary['worst_facility_rate']:.2f}%)"
        if summary["worst_facility"] else "불량률 최고 시설   : -",
        f"최다 불량 종류     : {summary['top_defect']} ({summary['top_defect_count']:,}건)"
        if summary["top_defect"] else "최다 불량 종류     : -",
        f"이상 기록 수       : {summary['anomaly_count']:,}건 (D99 또는 처리 시간 > {threshold_ms:g}ms)",
    ]
    spikes = summary.get("spikes")
    if spikes is not None:
        lines.append(f"불량 급증 감지     : {len(spikes)}건")
        for _, r in spikes.iterrows():
            lines.append(
                f"  - {r[COL_DATE]} {r[COL_FACILITY]} {r[COL_CAMERA]}: "
                f"{r[COL_RATE]:.2f}% (평소 {r['평소 불량률(%)']:.2f}%, "
                f"{r[COL_DEFECTS]}/{r[COL_INSPECTIONS]}건, z={r['z']:.1f})"
            )
    lines.append("==============================")
    return "\n".join(lines)


# ---------------------------------------------------------------- O1
def add_box_features(df):
    """불량 박스의 너비·높이·면적·중심점과 사진 안 위치(3x3 구역)를 계산해 붙인다."""
    out = df.dropna(subset=["box_x1", "box_y1", "box_x2", "box_y2"]).copy()
    out["box_w"] = out["box_x2"] - out["box_x1"]
    out["box_h"] = out["box_y2"] - out["box_y1"]
    out["box_area"] = out["box_w"] * out["box_h"]
    out["center_x"] = (out["box_x1"] + out["box_x2"]) / 2
    out["center_y"] = (out["box_y1"] + out["box_y2"]) / 2
    col = pd.cut(out["center_x"], [-np.inf, IMAGE_WIDTH / 3, IMAGE_WIDTH * 2 / 3, np.inf],
                 labels=["좌", "중", "우"])
    row = pd.cut(out["center_y"], [-np.inf, IMAGE_HEIGHT / 3, IMAGE_HEIGHT * 2 / 3, np.inf],
                 labels=["상", "중", "하"])
    out["region"] = row.astype(str) + "-" + col.astype(str)
    return out


def box_stats(df):
    """불량 종류별 박스 평균 크기와 평균 중심점, 가장 많이 나온 위치 구역."""
    boxes = add_box_features(df)
    if boxes.empty:
        return pd.DataFrame()
    g = boxes.groupby(["defect_code", "defect_name"])
    out = g.agg(
        건수=("box_area", "size"),
        평균너비=("box_w", "mean"),
        평균높이=("box_h", "mean"),
        평균면적=("box_area", "mean"),
        중심X평균=("center_x", "mean"),
        중심Y평균=("center_y", "mean"),
        중심X표준편차=("center_x", "std"),
        중심Y표준편차=("center_y", "std"),
        주요위치=("region", lambda s: s.value_counts().idxmax()),
    ).reset_index()
    return out.round(1)


def box_region_table(df):
    """불량 종류(행) x 사진 안 3x3 구역(열) 건수 표."""
    boxes = add_box_features(df)
    if boxes.empty:
        return pd.DataFrame()
    regions = [f"{r}-{c}" for r in ["상", "중", "하"] for c in ["좌", "중", "우"]]
    table = pd.crosstab(boxes["defect_name"], boxes["region"]).reindex(columns=regions, fill_value=0)
    table.index.name = "불량 종류"
    table.columns.name = None
    return table.reset_index()


# ---------------------------------------------------------------- O2
def detect_spikes(df, min_defects=5, rate_ratio=2.0, z_score=3.0, defect_codes=None):
    """날짜·시설·카메라 단위로 평소보다 불량이 크게 늘어난 경우를 찾는다.

    판단 기준 (세 조건을 모두 만족하면 '급증'):
      1) 그날 그 카메라의 불량 수가 min_defects건 이상 (적은 건수의 우연한 변동 제외)
      2) 그날 불량률이 평소 불량률의 rate_ratio배 이상
         - 평소 불량률 = 같은 카메라의 '그날을 뺀 나머지 날' 전체 불량 수 / 검사 수
      3) z = (그날 불량률 - 평소 불량률) / sqrt(평소 불량률 x (1 - 평소 불량률) / 그날 검사 수)
         가 z_score 이상 (이항분포 기준으로 우연이라 보기 어려운 차이)
    defect_codes를 주면 그 불량 종류만 불량으로 세어 같은 기준을 적용한다.
    """
    work = _with_date(df).assign(_ng=defect_mask(df, defect_codes))
    daily = work.groupby(["date", "facility", "camera_id"])["_ng"].agg(n="size", ng="sum").reset_index()
    totals = daily.groupby(["facility", "camera_id"])[["n", "ng"]].transform("sum")

    base_n = totals["n"] - daily["n"]
    base_ng = totals["ng"] - daily["ng"]
    p0 = np.where(base_n > 0, base_ng / base_n.replace(0, np.nan), np.nan)
    p = daily["ng"] / daily["n"]
    se = np.sqrt(p0 * (1 - p0) / daily["n"])
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(se > 0, (p - p0) / se, np.where(p > p0, np.inf, 0.0))

    daily["p0"] = p0
    daily["z"] = z
    flagged = (
        (daily["ng"] >= min_defects)
        & (p >= rate_ratio * daily["p0"])
        & (daily["z"] >= z_score)
    )
    out = daily[flagged].copy()

    # 그날 가장 많이 늘어난 불량 종류도 함께 보고
    ng_rows = work[work["_ng"]]
    top = (
        ng_rows.groupby(["date", "facility", "camera_id"])["defect_name"]
        .agg(lambda s: ", ".join(f"{k} {v}건" for k, v in s.value_counts().head(3).items()))
        .rename("주요 불량")
    )
    out = out.join(top, on=["date", "facility", "camera_id"])

    out = out.rename(columns={
        "date": COL_DATE, "facility": COL_FACILITY, "camera_id": COL_CAMERA,
        "n": COL_INSPECTIONS, "ng": COL_DEFECTS,
    })
    out[COL_RATE] = defect_rate(out[COL_DEFECTS], out[COL_INSPECTIONS])
    out["평소 불량률(%)"] = np.round(out["p0"] * 100, 2)
    out["배수"] = np.round(out[COL_RATE] / out["평소 불량률(%)"].replace(0, np.nan), 1)
    out["z"] = out["z"].round(2)
    cols = [COL_DATE, COL_FACILITY, COL_CAMERA, COL_INSPECTIONS, COL_DEFECTS, COL_RATE,
            "평소 불량률(%)", "배수", "z", "주요 불량"]
    return out[cols].sort_values([COL_DATE, COL_FACILITY, COL_CAMERA]).reset_index(drop=True)
