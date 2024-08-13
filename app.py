import streamlit as st  
import pandas as pd
from faker import Faker
import time  # 시간 지연을 위한 임포트

st.title("우리 반 자리바꾸기")
st.warning("자리바꾸기 알고리즘은 추가될 예정입니다. 현재는 랜덤만 가능합니다. ")

fake = Faker('ko_KR')

col_student, col_data = st.columns(2)

@st.cache_data
def create_sample_data(n_student):
    data = {
        "번호": [i for i in range(1, n_student + 1)],
        "이름": [fake.name() for _ in range(n_student)]
    }
    return pd.DataFrame(data)

with col_student:
    st.info("명단 엑셀을 업로드해주세요. 엑셀 양식을 다운로드하려면 fake 데이터 생성에 학생 수를 입력하고 오른쪽 표에서 다운로드 버튼을 눌러주세요.(표에 마우스오버를 하면 다운로드 버튼이 나타나요.)")

    uploaded_file = st.file_uploader("엑셀 파일을 업로드해주세요.", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=0)
        n_student = len(df)
        st.success(f"{n_student}명의 학생 데이터가 업로드되었습니다.")
    else:
        n_student = st.number_input("fake 데이터 생성용: 학생수를 입력해주세요.",
                            min_value=1, step=1, value=18)
        df = create_sample_data(n_student)  # 샘플 데이터 생성하여 df에 저장

with col_data:
    if 'df' in locals():
        st.write(df)

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
