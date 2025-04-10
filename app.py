import streamlit as st  
import pandas as pd
from faker import Faker
import time
import random

# ✅ 페이지 설정
st.set_page_config(
    page_title="자리바꾸기",
    page_icon="👾",
    layout="wide"
)

# ✅ 타이틀
st.title("👾 자리바꾸기")

st.info("""
**학생 명단 입력 방법을 선택해주세요!**  
1. **이름 입력하기** : 콤마(,)로 구분해서 직접 입력  
2. **엑셀 파일 업로드** : CSV 형식으로 업로드  
3. **랜덤 이름 생성** : 학생 수만 입력하면 무작위 이름 생성  

💡 엑셀 양식이 필요하면 오른쪽 표에서 다운로드 버튼을 눌러주세요! (표 위에 마우스를 올리면 버튼이 보여요)
""")

# ✅ Faker 설정 및 샘플 생성 함수
fake = Faker('ko_KR')

@st.cache_data
def create_sample_data(n_student):
    data = {
        "번호": [i for i in range(1, n_student + 1)],
        "이름": [fake.name() for _ in range(n_student)]
    }
    return pd.DataFrame(data)

# ✅ 2단 레이아웃: 입력창과 미리보기 분리 (좁은:넓은 비율)
col_input, col_preview = st.columns([1,1])

# 데이터프레임 초기화
df = None
n_student = 0

with col_input:
    st.subheader("👥 1단계: 학생 명단 입력")

    # 1. 엑셀 업로드
    st.markdown("#### 📄 엑셀 업로드")
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, index_col=0)
            n_student = len(df)
            st.success(f"{n_student}명의 학생 데이터가 업로드되었습니다.")
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    if df is None or df.empty:
        st.markdown("#### ✍️ 이름 직접 입력")
        name_input = st.text_area("콤마(,)로 이름을 구분해 입력해주세요.\n예: 김철수,이영희,박민수", height=100)

        if name_input:
            names = [name.strip() for name in name_input.split(",") if name.strip()]
            if names:
                df = pd.DataFrame({
                    "번호": list(range(1, len(names) + 1)),
                    "이름": names
                })
                n_student = len(df)
                st.success(f"{n_student}명의 학생 이름이 직접 입력되었습니다.")

        # ✅ 이름 없이 번호만으로 명단 만들기
        if df is None or df.empty:
            use_numbers_only = st.checkbox("이름 없이 번호(1, 2, 3...)로 명단 생성하기")
            if use_numbers_only:
                count = st.number_input("학생 수를 입력하세요", min_value=1, step=1, value=24)
                df = pd.DataFrame({
                    "번호": list(range(1, count + 1)),
                    "이름": [str(i) for i in range(1, count + 1)]
                })
                n_student = len(df)
                st.success(f"{n_student}명의 번호 기반 명단이 생성되었습니다.")


    # 3. 랜덤 이름 생성
    if df is None or df.empty:
        st.markdown("#### 🎲 랜덤 이름 생성")
        n_student_random = st.number_input("생성할 학생 수", min_value=1, step=1, value=24)
        df = create_sample_data(n_student_random)
        n_student = n_student_random
        st.success(f"{n_student}명의 무작위 학생 이름이 생성되었습니다.")

with col_preview:
    st.subheader("🧾 학생 명단 미리보기")
    if df is not None:
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.warning("왼쪽에서 학생 명단을 입력하거나 생성해주세요.")



import math

# 기본 세팅: 세로줄 5, 가로줄은 학생 수 기반 계산
default_col = 5
default_row = math.ceil(n_student / default_col) if n_student else 1
st.write(default_row)
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

seating_chart = [[cols[j].checkbox(f"{i+1}-{j+1}", key=f"{i+1}-{j+1}", value=True) for j in range(n_col)] for i in range(n_row)]
# st.session_state.seating_chart = seating_chart  # 세션 상태에 저장

classname = st.text_input("반 이름을 입력해주세요. 파일명에 포함됩니다. ")

st.write('---')


if st.button("자리배치 완료"):
    # 선택된 자리배치표 생성하기
    selected_seats = [(i+1, j+1) for i in range(n_row) for j in range(n_col) if seating_chart[i][j]]

    if len(selected_seats) < len(df):
        st.error("자리배치도의 자리 수가 학생 수보다 적습니다.")
    elif len(selected_seats) > len(df):
        st.error("자리배치도의 자리 수가 학생 수보다 많습니다.")
    else:
        # 애니메이션 효과를 위한 로딩 메시지
        st.image("https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/5eeea355389655.59822ff824b72.gif")
        with st.spinner("자리배치 중... 잠시만 기다려 주세요!"):
            time.sleep(2)  # 2초 지연

        # 랜덤
        import random
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

        def render_styled_table(df, font_size=font_size):
            html = "<table style='width: 100%; border-collapse: collapse; text-align: center;'>"
            for row in df.itertuples(index=False):
                html += "<tr>"
                for cell in row:
                    html += f"<td style='border: 1px solid #999; padding: 12px; font-weight: bold; font-size: {font_size}px;'>{cell if pd.notna(cell) else ''}</td>"
                html += "</tr>"
            html += "</table>"
            return html



        # 학생 관점 자리배치도

        st.write('---')
        st.error("아래 자리표 미리보기는 엑셀파일을 다운로드 하면 사라집니다. 필요한 경우 📸 캡쳐해두세요!")
        st.subheader("👁️‍🗨️ 학생 관점 자리배치도")
        st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 20px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
        st.markdown(render_styled_table(sight_student_pv), unsafe_allow_html=True)

        # 교사 관점 자리배치도
        st.subheader("🧑‍🏫 교사 관점 자리배치도")
        st.markdown(render_styled_table(sight_teacher_pv), unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 0px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)

        # sight_student_pv = pd.pivot_table(sight_student, index='행', columns='열', values='이름', aggfunc='first')
        # st.dataframe(sight_student_pv, use_container_width=True)  # 화면에 꽉차도록

        # # 교사 관점 자리배치도
        # sight_teacher_pv = sight_student_pv.iloc[::-1, ::-1].reset_index(drop=True)
        # st.subheader("교사 관점 자리배치도")
        # st.dataframe(sight_teacher_pv, use_container_width=True)  # 화면에 꽉차도록
        # st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 0px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
        
        # # 세션에 자리배치 데이터 저장
        # st.session_state["자리배치_학생"] = sight_student_pv
        # st.session_state["자리배치_교사"] = sight_teacher_pv


        import io
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter

        if "자리표_학생" in st.session_state and "자리표_교사" in st.session_state:
            classname = st.text_input("📘 학급명 또는 파일명에 쓸 제목 입력", value="우리반", help="예: 3학년2반, Class A 등")

            # ✅ 파일을 메모리 버퍼로 처리
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                # 칠판 행 생성
                chilpan = pd.DataFrame([[""] * st.session_state["자리표_교사"].shape[1],
                                        ["칠판"] * st.session_state["자리표_교사"].shape[1],
                                        [""] * st.session_state["자리표_교사"].shape[1]])
                chilpan.columns = range(1, st.session_state["자리표_교사"].shape[1] + 1)

                # 학생 관점 / 교사 관점 시트 구성
                student_sheet = pd.concat([chilpan, st.session_state["자리표_학생"].fillna("")], ignore_index=True)
                teacher_sheet = pd.concat([st.session_state["자리표_교사"].fillna(""), chilpan], ignore_index=True)

                student_sheet.to_excel(writer, sheet_name="학생 관점", index=False, header=False)
                teacher_sheet.to_excel(writer, sheet_name="교사 관점", index=False, header=False)

            # ✅ 버퍼에서 워크북 로드
            output.seek(0)
            wb = load_workbook(output)
            thin = Side(style="thin", color="999999")
            green = PatternFill(fill_type="solid", fgColor="A9EBBC")

            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    chilpan_row = any(cell.value == "칠판" for cell in row)
                    for cell in row:
                        cell.font = Font(size=14, bold=True)
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
                        if chilpan_row:
                            cell.fill = green
                for col in range(1, ws.max_column + 1):
                    ws.column_dimensions[get_column_letter(col)].width = 15

            # ✅ 다시 메모리 버퍼에 저장
            final_output = io.BytesIO()
            wb.save(final_output)
            final_output.seek(0)

            # # ✅ 다운로드 버튼
            # st.download_button(
            #     label="📥 자리표 Excel 다운로드",
            #     data=final_output,
            #     file_name=f"자리배치표_{classname}.xlsx",
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # )








        # # ── 상단 import 구역에 추가 ─────────────────────────────────────────────
        # from openpyxl import load_workbook
        # from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        # from openpyxl.utils import get_column_letter
        # # ───────────────────────────────────────────────────────────────────────







        # # ── 기존 자리표 저장·다운로드 블록 “전체 교체” ──────────────────────────
        # with pd.ExcelWriter("자리표.xlsx", engine="openpyxl") as writer:
        #     # 칠판 행(빈칸 포함)
        #     chilpan = pd.DataFrame([[""] * sight_teacher_pv.shape[1],
        #                             ["칠판"] * sight_teacher_pv.shape[1],
        #                             [""] * sight_teacher_pv.shape[1]])
        #     chilpan.columns = range(1, sight_teacher_pv.shape[1] + 1)

        #     # 시트 데이터
        #     student_sheet = pd.concat([chilpan, sight_student_pv.fillna("")], ignore_index=True)
        #     teacher_sheet = pd.concat([sight_teacher_pv.fillna(""), chilpan], ignore_index=True)

        #     student_sheet.to_excel(writer, sheet_name="학생 관점", index=False, header=False)
        #     teacher_sheet.to_excel(writer, sheet_name="교사 관점", index=False, header=False)

        # # ── 서식 적용 ───────────────────────────────────────────────────────────
        # wb = load_workbook("자리표.xlsx")
        # thin = Side(style="thin", color="999999")
        # green = PatternFill(fill_type="solid", fgColor="A9EBBC")

        # for ws in wb.worksheets:
        #     for row in ws.iter_rows():
        #         chilpan_row = any(cell.value == "칠판" for cell in row)
        #         for cell in row:
        #             cell.font = Font(size=14, bold=True)
        #             cell.alignment = Alignment(horizontal="center", vertical="center")
        #             cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
        #             if chilpan_row:
        #                 cell.fill = green
        #     # 열 너비 균일 설정
        #     for col in range(1, ws.max_column + 1):
        #         ws.column_dimensions[get_column_letter(col)].width = 15

        # wb.save("자리표.xlsx")
        st.write("")
        # ── 다운로드 버튼 ───────────────────────────────────────────────────────
        st.download_button(
            label="자리표 Excel 다운로드",
            data=open("자리표.xlsx", "rb").read(),
            file_name=f"자리배치표_{classname}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # ───────────────────────────────────────────────────────────────────────





st.markdown("""
<hr style='margin-top: 50px; margin-bottom: 10px;'>
<div style='text-align: center; color: gray; font-size: 14px;'>
    Made with ❤️ by <strong>황수빈T</strong>
</div>
""", unsafe_allow_html=True)
