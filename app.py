import time
import streamlit as st
import random
import pandas as pd
from faker import Faker
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import math

###### 📄 페이지 기본 설정
st.set_page_config(page_title="자리바꾸기", page_icon="👾", layout="wide")
st.title("👾 자리바꾸기")

st.info("""
이 앱은 **교실 자리배치표를 손쉽게 만들고, 예쁜 Excel 파일로 내려받기** 위해 제작되었습니다.

1. **엑셀 파일 업로드** : CSV 형식으로 업로드  
2. **이름 입력하기** : 콤마(,)로 구분해서 직접 입력  
3. **랜덤 이름 생성** : 사람 수만 입력하면 무작위 이름 생성

💡 CSV 양식이 필요하면 오른쪽 표에서 다운로드 버튼을 눌러주세요.
""")

###### 🔧 유틸리티 함수 정의
fake = Faker('ko_KR')

@st.cache_data
def create_sample_data(n):
    return pd.DataFrame({"번호": range(1, n + 1), "이름": [fake.name() for _ in range(n)]})

@st.cache_data
def render_styled_table(df, font_size=30):
    html = "<table style='width: 100%; border-collapse: collapse; text-align: center;'>"
    for row in df.itertuples(index=False):
        html += "<tr>"
        for cell in row:
            html += f"<td style='border: 1px solid #999; padding: 12px; font-weight: bold; font-size: {font_size}px;'>"
            html += f"{cell if pd.notna(cell) else ''}</td>"
        html += "</tr>"
    html += "</table>"
    return html

###### 🔢 변수 및 레이아웃 기본 설정
today = datetime.today().strftime("%Y.%m.%d")
todayfile = datetime.today().strftime("%Y%m%d")
df, n_student = None, 0
col_input, col_preview = st.columns([1, 1])

###### 👥 1단계: 명단 입력
with col_input:
    st.subheader("👥 1단계: 명단 입력")

    st.markdown("#### 📄 파일 업로드", help="엑셀만 있다면 오른쪽 미리보기 표에서 CSV로 다운로드할 수 있어요.")
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요.", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, index_col=0)
            n_student = len(df)
            st.success(f"{n_student}명의 명단 데이터가 업로드되었습니다.")
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    if df is None or df.empty:
        st.markdown("#### ✍️ 이름 직접 입력")
        name_input = st.text_area("콤마(,)로 이름을 구분해 입력해주세요.", height=100)

        if name_input:
            names = [n.strip() for n in name_input.split(",") if n.strip()]
            if names:
                df = pd.DataFrame({"번호": range(1, len(names) + 1), "이름": names})
                n_student = len(df)
                st.success(f"{n_student}명의 이름이 입력되었습니다.")

    if df is None or df.empty:
        if st.checkbox("이름 없이 번호(1, 2, 3...)로 명단 생성하기"):
            count = st.number_input("사람 수를 입력하세요", min_value=1, step=1, value=24)
            df = pd.DataFrame({
                "번호": range(1, count + 1),
                "이름": [str(i) for i in range(1, count + 1)]
            })
            n_student = count
            st.success(f"{n_student}명의 번호 기반 명단이 생성되었습니다.")

    if df is None or df.empty:
        st.markdown("#### 🎲 랜덤 이름 생성", help="일단 테스트로 해보고 싶으시다면!")
        rand_count = st.number_input("생성할 학생 수", min_value=1, step=1, value=24)
        df = create_sample_data(rand_count)
        n_student = rand_count
        st.success(f"{n_student}명의 무작위 학생 이름이 생성되었습니다.")

###### 🧾 학생 명단 미리보기
with col_preview:
    st.subheader("🧾 학생 명단 미리보기")
    if df is not None:
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.warning("왼쪽에서 학생 명단을 입력하거나 생성해주세요.")

# 기본 세팅: 세로줄 5, 가로줄은 학생 수 기반 계산
default_col = 5
default_row = math.ceil(n_student / default_col) if n_student else 1
col_row, col_col, font = st.columns(3)

with col_col:
    n_col = st.number_input("세로줄(열)은 몇 줄인가요?", min_value=1, value=default_col, step=1)
    st.session_state.n_col = n_col

with col_row:
    default_row = math.ceil(n_student / n_col) if n_student else 1
    n_row = st.number_input("가로줄(행)은 몇 줄인가요?", min_value=1, value=default_row, step=1)
    st.session_state.n_row = n_row

with font:
    font_size = st.number_input("자리표 글자 크기 설정 (단위: px)", min_value=10, max_value=60, value=30, step=1)

st.write('---')
st.subheader("🪑 2단계: 좌석배치 & 빈자리 체크하기")

st.info("아래에서 빈 자리를 체크 해제 해주세요. 세로 다섯 줄로 추천 배치도가 만들어졌습니다. ")
st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 5px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
cols = st.columns(n_col)

seating_chart = [
    [
        cols[j].checkbox(
            f"{i+1}-{j+1}",
            key=f"{i+1}-{j+1}",
            value=st.session_state.get(f"{i+1}-{j+1}", True)   # ✅ 수정
        )
        for j in range(n_col)
    ]
    for i in range(n_row)
]

classname = st.text_input("📘 학급명 또는 파일명에 쓸 제목 입력",
                        value="우리 반",
                        help="예: 3학년2반, Class A 등")

if st.button("🔮 랜덤 자리배치 시작하기") or st.session_state.get("자리배치_트리거"):
    st.session_state["자리배치_트리거"] = False

    # ▶ 무조건 현재 체크된 자리들 다시 가져옴
    # ▸ 랜덤 섞기 전 계산
    selected_seats = [
        (i+1, j+1)
        for i in range(n_row)
        for j in range(n_col)
        if st.session_state.get(f"{i+1}-{j+1}", True)
    ]

    if len(selected_seats) < len(df):
        st.error(f"자리배치도의 자리 수({len(selected_seats)})가 학생 수({len(df)})보다 적습니다.")
    elif len(selected_seats) > len(df):
        st.error(f"자리배치도의 자리 수({len(selected_seats)})가 학생 수({len(df)})보다 많습니다.")
    else:
        # 애니메이션 효과를 위한 로딩 메시지
        st.image("https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/5eeea355389655.59822ff824b72.gif")
        with st.spinner("자리배치 중... 잠시만 기다려 주세요!"):
            time.sleep(0.1)  # 2초 지연

        # 랜덤
        random.shuffle(selected_seats)

        # 학생 데이터 업데이트
        updated_data = []
        for idx, seat in enumerate(selected_seats):
            if idx < len(df):
                updated_data.append({
                    "번호": df.iloc[idx]["번호"],
                    "이름": df.iloc[idx]["이름"],
                    "행": seat[0],
                    "열": seat[1]
                })

        sight_student = pd.DataFrame(updated_data)

        # 자리표 데이터 피벗
        sight_student_pv = pd.pivot_table(sight_student, index='행', columns='열', values='이름', aggfunc='first')
        sight_teacher_pv = sight_student_pv.iloc[::-1, ::-1].reset_index(drop=True)

        # ✅ 세션에 저장
        st.session_state["자리배치_학생"] = sight_student_pv
        st.session_state["자리배치_교사"] = sight_teacher_pv

        # 학생 관점 자리배치도

        with pd.ExcelWriter("자리표.xlsx", engine="openpyxl") as writer:
            # 칠판 행(빈칸 포함)
            board = pd.DataFrame([[""] * sight_teacher_pv.shape[1],
                                ["칠판"] * sight_teacher_pv.shape[1],
                                [""] * sight_teacher_pv.shape[1]])
            board.columns = range(1, sight_teacher_pv.shape[1] + 1)

            # 시트 데이터
            stu_sheet = pd.concat([board, sight_student_pv.fillna("")], ignore_index=True)
            tch_sheet = pd.concat([sight_teacher_pv.fillna(""), board], ignore_index=True)

            stu_sheet.to_excel(writer, sheet_name="학생 관점", index=False, header=False)
            tch_sheet.to_excel(writer, sheet_name="교사 관점", index=False, header=False)

        wb = load_workbook("자리표.xlsx")
        thin = Side(style="thin", color="999999")
        green = PatternFill("solid", fgColor="A9EBBC")

        for ws in wb.worksheets:
            max_row = ws.max_row

            # ── 셀 서식 설정 ───────────────────────────────────────
            for r in ws.iter_rows(min_row=1, max_row=max_row):
                is_board = any(c.value == "칠판" for c in r)
                for c in r:
                    c.font = Font(size=40, bold=True)
                    c.alignment = Alignment(horizontal="center", vertical="center")
                    c.border = Border(top=thin, left=thin, right=thin, bottom=thin)
                    if is_board:
                        c.fill = green

            # ── 열 너비 설정 ───────────────────────────────────────
            for col in range(1, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(col)].width = 28

            # ── 하단 안내 문구 삽입 ─────────────────────────────────
            ws.cell(row=max_row + 3, column=1, value=f"제작 날짜 : {today}").font = Font(size=12)
            
            if ws.title == "학생 관점":
                ws.cell(row=max_row + 4, column=1, value="※ 이 시트는 학생이 보는 자리배치표입니다. 교사 관점 배치도는 아래의 다른 탭에서 확인해주세요. ").font = Font(size=12, italic=True)
            elif ws.title == "교사 관점":
                ws.cell(row=max_row + 4, column=1, value="※ 이 시트는 교사가 보는 자리배치표입니다. 학생 관점 배치도는 아래의 다른 탭에서 확인해주세요. ").font = Font(size=12, italic=True)

        # ▸ 인쇄 설정: 가로 방향 + 한 페이지에 맞추기
        ws.page_setup.orientation = "landscape"              # 가로 방향
        ws.page_setup.paperSize = ws.PAPERSIZE_A4            # A4용지
        ws.page_setup.fitToWidth = 1                         # 가로 1페이지
        ws.page_setup.fitToHeight = 1                        # 세로 1페이지

        # ▸ 여백 최소화
        ws.page_margins.left = 0.2
        ws.page_margins.right = 0.2
        ws.page_margins.top = 0.3
        ws.page_margins.bottom = 0.3

        # ▸ 인쇄영역 명시적으로 지정
        ws.print_area = f"A1:{get_column_letter(ws.max_column)}{ws.max_row + 4}"



        wb.save("자리표.xlsx")
        st.session_state["자리배치_완료됨"] = True
        st.session_state["엑셀_파일명"] = f"{classname} 자리표_{todayfile}.xlsx"

st.warning("자리표 미리보기 화면입니다. 이대로 저장하시는 경우 [📥 Excel 자리표 다운로드]를, 다시 배치하려면 [🔄 자리배치 다시 하기]버튼을 눌러주세요. ")


# ✅ 자리배치 완료 후에만 표시
if st.session_state.get("자리배치_완료됨"):
    # 자리표 미리보기
    st.subheader("👁️‍🗨️ 학생 관점 자리배치도")
    st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; "
                "line-height: 1.5; margin-top: 0px; margin-bottom: 20px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
    st.markdown(render_styled_table(st.session_state["자리배치_학생"], font_size=font_size), unsafe_allow_html=True)

    st.subheader("🧑‍🏫 교사 관점 자리배치도")
    st.markdown(render_styled_table(st.session_state["자리배치_교사"], font_size=font_size), unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; "
                "line-height: 1.5; margin-top: 0px; margin-bottom: 0px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)

    st.write("    ")
    col_dl, col_reset = st.columns([1, 1])
    with col_dl:
        st.download_button(
            label="📥 Excel 자리표 다운로드",
            data=open("자리표.xlsx", "rb").read(),
            file_name=st.session_state["엑셀_파일명"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    with col_reset:
        if st.button("🔄 자리배치 다시 하기", type='secondary'):
            st.session_state["자리배치_트리거"] = True
            st.session_state["자리배치_완료됨"] = False   # 버튼 잠시 숨기기(optional)
            st.rerun()

st.markdown("""
<div style='border: 1px solid lightgray; padding: 15px; border-radius: 10px; background-color: #f9f9f9; text-align: center; color: #444; font-size: 15px; margin-top: 40px;'>
    <strong>📌 Made by 반포고 황수빈T</strong><br>
    문의 사항은 <a href="mailto:sbhath17@gmail.com" style="text-decoration: none; color: #007acc;"><strong>sbhath17@gmail.com</strong></a> 로 연락 주세요.
</div>
""", unsafe_allow_html=True)