import streamlit as st

from app_home import run_home
from app_ml import run_ml
from app_species import species_price
from app_source import source, source_species, source_price

def main():
    st.title('호갱제로')


    menu = ['Home', 'price trend', 'ML', 'information']
    sub_menu = ['어종별 경락가', '산지별 경락가']


    st.sidebar.title("- 호갱제로 -")
    st.sidebar.title("")    
    choice = st.sidebar.selectbox('메뉴', menu)
    

    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        sub_choice = st.sidebar.selectbox('경락가', sub_menu)
        if sub_choice == sub_menu[0] :
            species_price() # 어종별 경락가
        elif sub_choice == sub_menu[1] :
            source_price()
            source() # 산지별 경락가
            source_species()
        
    elif choice == menu[2]:
        run_ml()
    elif choice == menu[3]:
        pass

    
if __name__ == '__main__':
    main()