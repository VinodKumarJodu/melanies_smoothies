# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """choose your fruits you want in your custom smoothie.
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('Name on your Smoothie will be:', name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))
# st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect(
    'Choose upto 5 Ingredients:', my_dataframe, 
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


import requests  
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response)
