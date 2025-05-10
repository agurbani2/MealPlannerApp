import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

# Load dataset
@st.cache_data
def load_data():
    file_path = "/Users/apple/Desktop/ids/Meal .xlsx"  # Local path
    df = pd.read_excel(file_path)
    return df

df = load_data()

# Apply custom styling
st.markdown(
    """
    <style>
        body {
            background-color: #f8f9fa;
            font-family: Arial, sans-serif;
        }
        .main-title {
            color: #16a085;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
        }
        .subheader {
            color: #16a085;
            font-size: 24px;
            font-weight: bold;
        }
        .meal-button {
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 18px;
            width: 100%;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Home Page
st.markdown("<h1 class='main-title'>Personalized Meal Plan Generator</h1>", unsafe_allow_html=True)
st.write("Enter your daily calorie intake goal, choose your dietary preference, and select the number of meals you want.")

# User selections
diet_choice = st.radio("Choose your diet preference:", ["Vegetarian", "Non-Vegetarian"], horizontal=True)
calorie_goal = st.number_input("Enter your daily calorie goal:", min_value=500, max_value=5000, step=100)
meal_count = st.radio("Choose the number of meals per day:", [2, 3, 4], horizontal=True)

if st.button("Generate Meal Plan", use_container_width=True):
    selected_meals = []
    remaining_calories = calorie_goal
    total_calories = 0
    
    # Define meal selection rules
    meal_types = ["Breakfast", "Lunch", "Dinner"][:meal_count]  # Ensure correct meal count

    for meal in meal_types:
        meal_options = df[(df['Meals'] == meal) & (df['Preferred Diet Type'] == diet_choice)]
        meal_options = meal_options[meal_options['Calories'] <= remaining_calories]
        
        if not meal_options.empty:
            chosen_meal = meal_options.sample(1).iloc[0].to_dict()
            selected_meals.append(chosen_meal)
            total_calories += chosen_meal["Calories"]
            remaining_calories -= chosen_meal["Calories"]
    
    while len(selected_meals) < meal_count:
        additional_meals = df[(df['Preferred Diet Type'] == diet_choice) & (df['Meals'].isin(meal_types)) & (df['Calories'] <= remaining_calories)]
        if additional_meals.empty:
            break
        extra_meal = additional_meals.sample(1).iloc[0].to_dict()
        selected_meals.append(extra_meal)
        total_calories += extra_meal["Calories"]
        remaining_calories -= extra_meal["Calories"]
    
    st.session_state["meal_plan"] = selected_meals[:meal_count]  
    st.session_state["selected_meal"] = None  
    st.rerun()

# Show meal plan if generated
if st.session_state.get("meal_plan") and not st.session_state.get("selected_meal"):
    st.subheader("Your Recommended Meal Plan")
    for meal in st.session_state["meal_plan"]:
        if st.button(meal["Dish Name"], key=meal["Dish Name"], use_container_width=True):  
            st.session_state["selected_meal"] = meal
            st.rerun()

# Meal Details Page
if st.session_state.get("selected_meal"):
    meal = st.session_state["selected_meal"]
    
    st.markdown(f"<h2 class='subheader'>{meal['Dish Name']}</h2>", unsafe_allow_html=True)
    st.subheader("Nutritional Information")
    
    # Create a pie chart
    fig, ax = plt.subplots()
    labels = ["Protein", "Fats", "Carbs"]
    values = [meal['Protein(g)'], meal['Fats(g)'], meal['Carbs(g)']]
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
    
    # Display pie chart and nutritional info side by side
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig)
    with col2:
        st.write(f"Calories: {meal['Calories']} kcal")
        st.write(f"Protein: {meal['Protein(g)']} g")
        st.write(f"Fats: {meal['Fats(g)']} g")
        st.write(f"Sodium: {meal['Sodium(mg)']} mg")
        st.write(f"Carbohydrates: {meal['Carbs(g)']} g")
    
    st.subheader("Ingredients")
    st.write(meal["Ingredients"])
    
    st.subheader("Directions")
    st.write(meal["Directions"])
    
    st.subheader("Recipe Video")
    if pd.notna(meal["Recipe Links"]):  
        st.video(meal["Recipe Links"])
    else:
        st.write("No video available.")
    
    if st.button("Back to Meal Plan", use_container_width=True):
        st.session_state["selected_meal"] = None
        st.rerun()


