"""비전검사 로그 Dash 화면. (D1~D7)

실행: python app.py  ->  브라우저에서 http://127.0.0.1:8050 열기
집계는 vision_log.analysis의 함수만 불러서 하고, 로그는 시작할 때 한 번만 읽는다. (D7)
"""
import argparse

import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html

from vision_log import analysis, loader
from vision_log.config import load_config


def parse_args():
    p = argparse.ArgumentParser(description="비전검사 로그 Dash 화면")
    p.add_argument("--config", default="config.json")
    p.add_argument("--input", dest="input_dir")
    p.add_argument("--output", dest="output_dir")
    p.add_argument("--threshold", dest="process_ms_threshold", type=float)
    p.add_argument("--port", type=int)
    return p.parse_args()


ARGS = parse_args()
CONFIG = load_config(ARGS.config, {
    "input_dir": ARGS.input_dir,
    "output_dir": ARGS.output_dir,
    "process_ms_threshold": ARGS.process_ms_threshold,
})
THRESHOLD = CONFIG["process_ms_threshold"]

# ---- 로그는 앱 시작 시 한 번만 읽는다 (D7)
loader.setup_logger(CONFIG["output_dir"], "dash_run_log.txt")
DF, CODES = loader.load_dataset(CONFIG)

FACILITIES = sorted(DF["facility"].unique())
MIN_DATE = DF["timestamp"].min().date()
MAX_DATE = DF["timestamp"].max().date()
DEFECT_OPTIONS = [{"label": f"{r.defect_code} {r.defect_name}", "value": r.defect_code}
                  for r in CODES.itertuples()]

ANOMALY_COLUMNS = ["이상 사유", "timestamp", "facility", "camera_id", "product_code",
                   "serial_no", "defect_code", "defect_name", "confidence", "process_ms", "image_file"]


# ---------------------------------------------------------------- 화면 구성 요소
def card(title, value_id):
    return html.Div(className="card", children=[
        html.Div(title, className="card-title"),
        html.Div("-", id=value_id, className="card-value"),
    ])


def table(table_id, page_size=10):
    return dash_table.DataTable(
        id=table_id,
        page_size=page_size,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "inherit", "fontSize": 13, "padding": "4px 8px", "textAlign": "center"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f1f3f5"},
    )


def section(title, *children):
    return html.Div(className="section", children=[html.H3(title), *children])


app = Dash(__name__, title="비전검사 로그 현황")
app.index_string = app.index_string.replace("</head>", """
<style>
  body { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; margin: 0; background: #f8f9fa; color: #212529; }
  .wrap { max-width: 1280px; margin: 0 auto; padding: 16px; }
  .filters { display: flex; flex-wrap: wrap; gap: 24px; background: #fff; padding: 16px; border-radius: 8px;
             box-shadow: 0 1px 3px rgba(0,0,0,.08); position: sticky; top: 0; z-index: 10; }
  .filters label.title { display: block; font-weight: bold; margin-bottom: 6px; font-size: 14px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 16px 0; }
  .card { background: #fff; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
  .card-title { font-size: 13px; color: #6c757d; }
  .card-value { font-size: 28px; font-weight: bold; margin-top: 4px; }
  .row { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 16px; }
  .section { background: #fff; padding: 12px 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 16px; }
  .section h3 { margin: 4px 0 8px; font-size: 16px; }
  .note { font-size: 12px; color: #6c757d; }
</style>
</head>""")

app.layout = html.Div(className="wrap", children=[
    html.H2("비전검사 로그 통합 현황"),

    # D2: 선택 요소
    html.Div(className="filters", children=[
        html.Div([
            html.Label("시설", className="title"),
            dcc.Checklist(id="f-facility", options=FACILITIES, value=FACILITIES, inline=True,
                          inputStyle={"marginRight": "4px", "marginLeft": "8px"}),
        ]),
        html.Div([
            html.Label("날짜 범위", className="title"),
            dcc.DatePickerRange(id="f-date", min_date_allowed=MIN_DATE, max_date_allowed=MAX_DATE,
                                start_date=MIN_DATE, end_date=MAX_DATE, display_format="YYYY-MM-DD"),
        ]),
        html.Div(style={"minWidth": "320px", "flex": "1"}, children=[
            html.Label("불량 종류 (비우면 전체)", className="title"),
            dcc.Dropdown(id="f-defect", options=DEFECT_OPTIONS, multi=True, placeholder="전체 불량"),
        ]),
    ]),

    # D3: 요약 숫자
    html.Div(className="cards", children=[
        card("검사 수", "v-inspections"),
        card("불량 수", "v-defects"),
        card("불량률", "v-rate"),
        card(f"이상 기록 수 (D99 / >{THRESHOLD:g}ms)", "v-anomalies"),
    ]),

    # D4: 그래프
    html.Div(className="row", children=[
        section("시설별 불량 종류 건수", dcc.Graph(id="g-facility-defect")),
        section("날짜별 불량률 추이", dcc.Graph(id="g-daily-rate")),
    ]),

    # D5: 표
    section("시설 x 불량 종류 건수", table("t-facility-defect")),
    section(f"이상 기록 목록 (판정 불가 D99 또는 처리 시간 > {THRESHOLD:g}ms)",
            html.Div("시설·날짜 조건만 적용됩니다.", className="note"),
            table("t-anomalies")),

    # O1: 불량 박스 위치·크기
    html.Div(className="row", children=[
        section("불량 위치 분포 (박스 중심점, 사진 1280x1024)", dcc.Graph(id="g-box-scatter")),
        section("불량 종류별 박스 평균 크기·위치", table("t-box-stats"), html.Br(), table("t-box-region")),
    ]),

    # O2: 급증 감지
    section("불량 급증 감지 (날짜·시설·카메라)",
            html.Div(
                f"기준: 그날 불량 {CONFIG['spike']['min_defects']}건 이상, "
                f"같은 카메라의 나머지 날 평균 불량률의 {CONFIG['spike']['rate_ratio']:g}배 이상, "
                f"z ≥ {CONFIG['spike']['z_score']:g}. 시설·날짜·불량 종류 조건을 모두 적용합니다.",
                className="note"),
            table("t-spikes")),
])


def to_table(df):
    df = df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict("records"), [{"name": c, "id": c} for c in df.columns]


# ---------------------------------------------------------------- D6: 선택이 바뀌면 전부 다시 계산
@app.callback(
    Output("v-inspections", "children"),
    Output("v-defects", "children"),
    Output("v-rate", "children"),
    Output("v-anomalies", "children"),
    Output("g-facility-defect", "figure"),
    Output("g-daily-rate", "figure"),
    Output("t-facility-defect", "data"),
    Output("t-facility-defect", "columns"),
    Output("t-anomalies", "data"),
    Output("t-anomalies", "columns"),
    Output("g-box-scatter", "figure"),
    Output("t-box-stats", "data"),
    Output("t-box-stats", "columns"),
    Output("t-box-region", "data"),
    Output("t-box-region", "columns"),
    Output("t-spikes", "data"),
    Output("t-spikes", "columns"),
    Input("f-facility", "value"),
    Input("f-date", "start_date"),
    Input("f-date", "end_date"),
    Input("f-defect", "value"),
)
def update(facilities, start_date, end_date, defects):
    defects = defects or None
    # 시설을 하나도 고르지 않으면 빈 결과
    scoped = analysis.filter_records(DF, facilities or ["__none__"], start_date, end_date)
    picked = analysis.filter_records(scoped, defect_codes=defects)

    # D3: 요약 숫자 (검사 수는 시설·날짜 기준, 불량은 선택한 불량 종류 기준)
    fac = analysis.facility_summary(scoped, defects)
    total = fac[fac[analysis.COL_FACILITY] == analysis.TOTAL].iloc[0]
    anomalies = analysis.find_anomalies(scoped, THRESHOLD)

    # D4: 그래프
    fac_defect = analysis.facility_defect_table(scoped, defects)
    long = fac_defect[fac_defect[analysis.COL_FACILITY] != analysis.TOTAL] \
        .drop(columns=[analysis.TOTAL]) \
        .melt(id_vars=analysis.COL_FACILITY, var_name="불량 종류", value_name="건수")
    fig_bar = px.bar(long, x=analysis.COL_FACILITY, y="건수", color="불량 종류", barmode="group")
    fig_bar.update_layout(margin=dict(l=40, r=10, t=10, b=40), legend_title_text="불량 종류")

    daily = analysis.daily_facility_summary(scoped, defects)
    fig_line = px.line(daily, x=analysis.COL_DATE, y=analysis.COL_RATE, color=analysis.COL_FACILITY,
                       markers=True, hover_data=[analysis.COL_INSPECTIONS, analysis.COL_DEFECTS])
    fig_line.update_layout(margin=dict(l=40, r=10, t=10, b=40), yaxis_rangemode="tozero")
    fig_line.update_xaxes(type="category")

    # O1
    boxes = analysis.add_box_features(picked)
    fig_box = px.scatter(boxes, x="center_x", y="center_y", color="defect_name", size="box_area",
                         size_max=18, hover_data=["facility", "camera_id", "serial_no"],
                         labels={"center_x": "중심 X", "center_y": "중심 Y", "defect_name": "불량 종류"})
    fig_box.update_xaxes(range=[0, analysis.IMAGE_WIDTH])
    fig_box.update_yaxes(range=[analysis.IMAGE_HEIGHT, 0])  # 사진 좌표계: 위가 0
    fig_box.update_layout(margin=dict(l=40, r=10, t=10, b=40))

    # O2
    spike = CONFIG["spike"]
    spikes = analysis.detect_spikes(scoped, spike["min_defects"], spike["rate_ratio"],
                                    spike["z_score"], defect_codes=defects)

    return (
        f"{int(total[analysis.COL_INSPECTIONS]):,}",
        f"{int(total[analysis.COL_DEFECTS]):,}",
        f"{total[analysis.COL_RATE]:.2f}%",
        f"{len(anomalies):,}",
        fig_bar,
        fig_line,
        *to_table(fac_defect),
        *to_table(anomalies[ANOMALY_COLUMNS]),
        fig_box,
        *to_table(analysis.box_stats(picked)),
        *to_table(analysis.box_region_table(picked)),
        *to_table(spikes),
    )


if __name__ == "__main__":
    port = ARGS.port or CONFIG["dash"]["port"]
    print(f"브라우저에서 http://{CONFIG['dash']['host']}:{port} 를 여세요.")
    app.run(host=CONFIG["dash"]["host"], port=port, debug=False)
