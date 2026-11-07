
import streamlit as st
import requests
import snowflake.connector

st.set_page_config(
    page_title="Melanie's Smoothies",
    page_icon="🥤",
    layout="centered"
)

st.title("🥤 Customize Your Smoothie")
st.write("Choose up to five fruits for your custom smoothie.")

# Input fields
name_on_order = st.text_input("Name on Smoothie:")

# Connect to Snowflake
@st.cache_resource
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database="SMOOTHIES",
        schema="PUBLIC",
        role=st.secrets["snowflake"]["role"]
    )

try:
    conn = get_snowflake_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT FRUIT_NAME
        FROM FRUIT_OPTIONS
        ORDER BY FRUIT_NAME
    """)

    fruits = [row[0] for row in cursor.fetchall()]

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        options=fruits,
        max_selections=5
    )

    if ingredients_list:
        st.write("Selected ingredients:", ", ".join(ingredients_list))

    if st.button("Submit Order"):
        if not name_on_order.strip():
            st.warning("Please enter your name.")
        elif not ingredients_list:
            st.warning("Please select at least one fruit.")
        else:
            cursor.execute(
                """
                INSERT INTO ORDERS (INGREDIENTS, NAME_ON_ORDER)
                VALUES (%s, %s)
                """,
                (", ".join(ingredients_list), name_on_order.strip())
            )

            st.success(
                f"Your smoothie is ordered, {name_on_order}!"
            )

    cursor.close()

except Exception:
    st.error("Unable to connect to the smoothie database.")
    st.exception(Exception)

# Fruit API

# New section to display SmoothieFroot nutrition information
import requests

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon",
    timeout=15
)

smoothiefroot_response.raise_for_status()

# Display API response
# st.text(smoothiefroot_response.json())

# Convert JSON response into a Streamlit DataFrame
sf_df = st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
