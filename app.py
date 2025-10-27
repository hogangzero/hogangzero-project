import streamlit as st

import run_home
import source_price
from species_price import species_price
import status_price

def main():
    st.title('Seafood forecasting')

    menu = ['Home', '경락가', 'ML', '정보']
    sub_menu = ['어종별 경락가', '산지별 경락가', '상태별(활어, 선어, 냉동) 경락가']

    choice = st.sidebar.selectbox('메뉴', menu)
    

    if choice == menu[0]:
        pass
    elif choice == menu[1]:
        sub_choice = st.sidebar.selectbox('경락가', sub_menu)
        if sub_choice == sub_menu[0] :
            pass # 어종별 경락가
        elif sub_choice == sub_menu[1] :
            pass # 산지별 경락가
        elif sub_choice == sub_menu[2] :
            pass # 상태별 경락가
        
    elif choice == menu[2]:
        pass
    elif choice == menu[3]:
        pass

    
if __name__ == '__main__':
    main()