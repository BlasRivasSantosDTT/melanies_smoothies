# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd

# helpful_links = [
    # "https://docs.streamlit.io",
    # "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit",
    # "https://github.com/Snowflake-Labs/snowflake-demo-streamlit",
    # "https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake"
# ]

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie :smile:")

name_on_order = st.text_input('Name on smoothie')
st.write("The name on smoothie will be", name_on_order)

cnx = st.connection ("snowflake")
session = cnx.session ()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark df to a Pandas df so we can use LOC function
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections = 5
)

if ingredients_list:
    
    ingredients_string =''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen+ ' Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width = True)

    # st.write (ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # st.write(my_insert_stmt)

    time_to_insert = st.button ('Submit order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, friend {name_on_order}', icon="✅")
