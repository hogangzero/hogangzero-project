import streamlit as st

from app_home import run_home
# from app_species import species_price # 어종별 경락가
from app_species import species_price
from app_source import source_price

def main():
    st.title('Seafood forecasting')

    menu = ['Home', '경락가', 'ML', '정보']
    sub_menu = ['어종별 경락가', '산지별 경락가']

    choice = st.sidebar.selectbox('메뉴', menu)
    

    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        sub_choice = st.sidebar.selectbox('경락가', sub_menu)
        if sub_choice == sub_menu[0] :
            species_price() # 어종별 경락가
        elif sub_choice == sub_menu[1] :
            source_price() # 산지별 경락가 
        
    elif choice == menu[2]:
        pass
    elif choice == menu[3]:
        pass

    
if __name__ == '__main__':
    main()