import streamlit as st  
import pandas as pd
from faker import Faker
import time
import random

# ✅ 페이지 설정
st.set_page_config(
    page_title="자리바꾸기",
    page_icon="👾",
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
col_input, col_preview = st.columns([1.2, 2.8])

# 데이터프레임 초기화
df = None
n_student = 0

with col_input:
    st.subheader("👥 학생 명단 입력")

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

    # 2. 이름 직접 입력
    if df is None or df.empty:
        st.markdown("#### ✍️ 이름 직접 입력")
        name_input = st.text_area("콤마(,)로 이름을 구분해 입력해주세요.\n예: 김철수, 이영희, 박민수", height=100)

        if name_input:
            names = [name.strip() for name in name_input.split(",") if name.strip()]
            if names:
                df = pd.DataFrame({
                    "번호": list(range(1, len(names) + 1)),
                    "이름": names
                })
                n_student = len(df)
                st.success(f"{n_student}명의 학생 이름이 직접 입력되었습니다.")

    # 3. 랜덤 이름 생성
    if df is None or df.empty:
        st.markdown("#### 🎲 랜덤 이름 생성")
        n_student_random = st.number_input("생성할 학생 수", min_value=1, step=1, value=18)
        df = create_sample_data(n_student_random)
        n_student = n_student_random
        st.success(f"{n_student}명의 무작위 학생 이름이 생성되었습니다.")

with col_preview:
    st.subheader("🧾 학생 명단 미리보기")
    if df is not None:
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.warning("왼쪽에서 학생 명단을 입력하거나 생성해주세요.")



col_row, col_col = st.columns(2)
with col_row:
    # 가로줄(행) 입력
    n_row = st.number_input("가로줄(행)은 몇줄인가요?", min_value=1, value=st.session_state.get('n_row', 1), step=1)
    st.session_state.n_row = n_row
with col_col:
    # 세로줄(열) 입력
    n_col = st.number_input("세로줄(열)은 몇줄인가요?", min_value=1, value=st.session_state.get('n_col', 1), step=1)
    st.session_state.n_col = n_col

st.write('---')
st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 5px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
cols = st.columns(n_col)

seating_chart = [[cols[j].checkbox(f"{i+1}-{j+1}", key=f"{i+1}-{j+1}", value=True) for j in range(n_col)] for i in range(n_row)]
# st.session_state.seating_chart = seating_chart  # 세션 상태에 저장

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

        # 학생 관점 자리배치도
        st.subheader("학생 관점 자리배치도")
        st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 20px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)

        sight_student_pv = pd.pivot_table(sight_student, index='행', columns='열', values='이름', aggfunc='first')
        st.dataframe(sight_student_pv, use_container_width=True)  # 화면에 꽉차도록

        # 교사 관점 자리배치도
        sight_teacher_pv = sight_student_pv.iloc[::-1, ::-1].reset_index(drop=True)
        st.subheader("교사 관점 자리배치도")
        st.dataframe(sight_teacher_pv, use_container_width=True)  # 화면에 꽉차도록
        st.markdown("<h5 style='text-align: center; background-color: #a9ebbc; line-height: 1.5; margin-top: 0px; margin-bottom: 0px; padding: 5px'>칠판</h5>", unsafe_allow_html=True)
        
        # 자리표 다운로드 버튼
        with pd.ExcelWriter('자리표.xlsx') as writer:
            st.write("")  # 위에 빈칸 추가
            chilpan = pd.DataFrame(['칠판'] * sight_teacher_pv.shape[1]).T
            chilpan = pd.concat([pd.Series([""]), chilpan, pd.Series([""])], ignore_index=True)  # 위아래에 빈칸 추가
            chilpan.columns = range(1, sight_teacher_pv.shape[1] + 1)  # 열 수에 맞게 수정

            sight_student_pv_with_title = pd.concat([chilpan, sight_student_pv.fillna('')], ignore_index=True)
            sight_teacher_pv_with_title = pd.concat([sight_teacher_pv.fillna(''), chilpan], ignore_index=True)

            sight_student_pv_with_title.to_excel(writer, sheet_name='학생 관점', index=False, header=False)
            sight_teacher_pv_with_title.to_excel(writer, sheet_name='교사 관점', index=False, header=False)

        st.download_button(
            label="자리표 다운로드",
            data=open('자리표.xlsx', 'rb').read(),
            file_name='자리표.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
