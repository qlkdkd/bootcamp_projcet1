"""비전검사 로그 통합 처리 - 전체 처리 실행 파일. (S6)

사용 예:
    python main.py
    python main.py --input . --output output --threshold 1000
    python main.py --facility A시설 C시설 --start 2026-11-17 --end 2026-11-18 --defect D01 D05
"""
import argparse
import sys

from vision_log import analysis, charts, loader
from vision_log.config import load_config
from vision_log.writer import save_csv, save_text


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="비전검사 로그 통합 처리 프로그램")
    p.add_argument("--config", default="config.json", help="설정 파일 경로 (기본: config.json)")
    p.add_argument("--input", dest="input_dir", help="입력 폴더")
    p.add_argument("--output", dest="output_dir", help="출력 폴더")
    p.add_argument("--threshold", dest="process_ms_threshold", type=float, help="처리 시간 기준값(ms)")
    g = p.add_argument_group("기록 골라내기(F9) - 일부만 주어도 됨")
    g.add_argument("--facility", nargs="+", help="시설 이름 (예: A시설 B시설)")
    g.add_argument("--start", help="시작 날짜 (예: 2026-11-16)")
    g.add_argument("--end", help="끝 날짜, 포함 (예: 2026-11-18)")
    g.add_argument("--defect", nargs="+", help="불량 코드 또는 이름 (예: D01 찍힘)")
    return p.parse_args(argv)


def run(config):
    out = config["output_dir"]
    thr = config["process_ms_threshold"]
    log = loader.setup_logger(out, config["run_log_file"])
    log.info("처리 시작 - 입력: %s, 출력: %s, 처리 시간 기준: %gms", config["input_dir"], out, thr)

    # F1~F3: 읽기, 합치기, 불량코드 결합
    # F1~F3이 통합된 함수 호출 후 'all_facility_log.csv'로 저장
    df, _codes = loader.load_dataset(config)
    full = df.drop(columns=["source_file"])
    log.info("저장: %s", save_csv(full, out, "all_facility_log.csv"))

    # F4~F7: 집계
    # 시설(행) x 불량 종류(열) 불량 건수 표. 열 순서는 불량 코드 순, 합계 행·열 포함
    fac_defect = analysis.facility_defect_table(df)
    # 날짜별·시설별 검사 수와 불량률
    daily = analysis.daily_facility_summary(df)
    tables = {
        # 시설별 검사 수, 불량 수, 불량률(%). 맨 아래에 합계 행을 붙인다
        "summary_by_facility.csv": analysis.facility_summary(df),
        "defects_by_facility_type.csv": fac_defect,
        # 불량 분류별 건수와 비율(%)
        "defects_by_category.csv": analysis.category_table(df),
        "summary_by_date_facility.csv": daily,
        "summary_by_camera.csv": analysis.camera_summary(df),

        # F8
        # 판정 불가(D99)이거나 처리 시간이 기준값을 넘는 기록. '이상 사유' 열을 붙인다
        "anomaly_records.csv": analysis.find_anomalies(full, thr),
        # O1
        "box_stats_by_defect.csv": analysis.box_stats(df),
        "box_region_by_defect.csv": analysis.box_region_table(df),
    }
    # O2
    spike_cfg = config["spike"]
    spikes = analysis.detect_spikes(df, spike_cfg["min_defects"], spike_cfg["rate_ratio"], spike_cfg["z_score"])
    tables["defect_spikes.csv"] = spikes

    for name, table in tables.items():
        log.info("저장: %s (%d행)", save_csv(table, out, name), len(table))

    # F9: 조건이 하나라도 있으면 골라낸 기록 저장
    f = config["filter"]
    if any(f.get(k) for k in ("facilities", "start_date", "end_date", "defect_codes")):
        picked = analysis.filter_records(full, f["facilities"], f["start_date"], f["end_date"], f["defect_codes"])
        log.info("조건 %s -> %d건", {k: v for k, v in f.items() if v}, len(picked))
        log.info("저장: %s", save_csv(picked, out, "filtered_records.csv"))
    else:
        log.info("기록 골라내기 조건이 없어 filtered_records.csv는 만들지 않음 (--facility/--start/--end/--defect)")

    # F10: 그래프

    # 시설별 불량률 테이블 -> 막대그래프
    log.info("저장: %s", charts.plot_facility_defects(fac_defect, out))
    # 날짜별 불량률 테이블 -> 꺾은선그래프
    log.info("저장: %s", charts.plot_daily_rate(daily, out))

    # F11: 요약
    summary_text = analysis.format_summary(analysis.build_summary(df, thr, spikes), thr)
    log.info("저장: %s", save_text(summary_text + "\n", out, "summary.txt"))
    print()
    print(summary_text)
    log.info("처리 완료")


def main(argv=None):
    args = parse_args(argv)
    overrides = {
        "input_dir": args.input_dir,
        "output_dir": args.output_dir,
        "process_ms_threshold": args.process_ms_threshold,
        "filter": {
            "facilities": args.facility,
            "start_date": args.start,
            "end_date": args.end,
            "defect_codes": args.defect,
        },
    }
    config = load_config(args.config, overrides)
    try:
        run(config)
    except Exception as e:
        loader.logger.exception("처리 실패: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
