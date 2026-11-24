"""PNG 그래프 저장. (F10)"""
import matplotlib

matplotlib.use("Agg")  # 화면 없이 파일로만 저장
import matplotlib.pyplot as plt
from matplotlib import font_manager

from .analysis import COL_DATE, COL_FACILITY, COL_RATE, TOTAL
from .writer import ensure_dir

KOREAN_FONTS = ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"]


def set_korean_font():
    """**한국어 글꼴 지정 함수**

    설치된 한글 글꼴을 찾아 matplotlib 기본 글꼴로 지정한다."""
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in KOREAN_FONTS:
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False  # 음수 부호 깨짐 방지
    return plt.rcParams["font.family"]


def plot_facility_defects(table, output_dir, filename="chart_facility_defects.png"):
    """**시설별 불량 종류 건수 -> 막대그래프**

    - 입력: 테이블(analysis.py의 facility_defect_table()의 결과), 출력할 파일의 경로
    - 출력: 막대그래프를 저장한 png 사진
    
    - 시설별 불량 종류 건수 묶은 막대그래프. table은 facility_defect_table()의 결과."""

    set_korean_font()
    data = table[table[COL_FACILITY] != TOTAL].set_index(COL_FACILITY).drop(columns=[TOTAL])
    fig, ax = plt.subplots(figsize=(11, 6))
    data.plot(kind="bar", ax=ax, width=0.8, colormap="tab10")
    ax.set_title("시설별 불량 종류 건수")
    ax.set_xlabel("시설")
    ax.set_ylabel("불량 건수")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="불량 종류", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = ensure_dir(output_dir) / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_daily_rate(daily, output_dir, filename="chart_daily_defect_rate.png"):
    """**날짜별 시설 불량률 추이 -> 꺾은선그래프**

    - 입력: analysis.py의 daily_facility_summary(), 출력할 파일의 경로
    - 출력: 꺾은선그래프를 저장한 png 사진
    
    - 날짜별 시설 불량률 추이 꺾은선그래프. daily는 daily_facility_summary()의 결과."""

    set_korean_font()
    pivot = daily.pivot(index=COL_DATE, columns=COL_FACILITY, values=COL_RATE)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for facility in pivot.columns:
        ax.plot(pivot.index, pivot[facility], marker="o", label=facility)
    ax.set_title("날짜별 시설 불량률 추이")
    ax.set_xlabel("날짜")
    ax.set_ylabel("불량률(%)")
    ax.set_ylim(bottom=0)
    ax.legend(title="시설")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = ensure_dir(output_dir) / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
