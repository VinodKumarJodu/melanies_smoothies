
import streamlit as st
import requests
import snowflake.connector
from urllib.parse import quote

st.set_page_config(
    page_title="Melanie's Smoothies",
    page_icon="🥤",
    layout="wide"
)

st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom smoothie.")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

@st.cache_resource
def get_snowflake_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database="SMOOTHIES",
        schema="PUBLIC",
        role=st.secrets["snowflake"]["role"]
    )

ingredients_list = []

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

    ingredients_string = " ".join(ingredients_list)

    if ingredients_list:
        st.write("Your selected ingredients:", ingredients_string)

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
                (ingredients_string, name_on_order.strip())
            )
            conn.commit()
            st.success(f"Your Smoothie is ordered, {name_on_order}!")

    cursor.close()

except Exception as exc:
    st.error("Unable to connect to or query the smoothie database.")
    st.exception(exc)

# Display nutrition information for each selected fruit
if ingredients_list:

    for fruit_chosen in ingredients_list:

        st.subheader(f"{fruit_chosen} Nutrition Information")

        fruit_api_url = (
            "https://my.smoothiefroot.com/api/fruit/"
            + quote(fruit_chosen.lower(), safe="")
        )

        try:
            smoothiefroot_response = requests.get(
                fruit_api_url,
                timeout=15
            )

            if smoothiefroot_response.status_code == 404:
                st.info(
                    f"{fruit_chosen} is not available "
                    "in the SmoothieFroot database."
                )
                continue

            smoothiefroot_response.raise_for_status()

            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        except requests.RequestException as exc:
            st.warning(
                f"Unable to retrieve {fruit_chosen} information: {exc}"
            )

        except ValueError:
            st.warning(
                f"Invalid JSON response for {fruit_chosen}."
            )
