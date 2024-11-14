import streamlit as st
import plotly.graph_objects as go
from streamlit_folium import folium_static
import pandas as pd

from utils.calculations import calculate_distance, get_transport_comparison
from utils.map_utils import create_route_map
from registry_form import registry_service_form  # Import the registry service form

# Page configuration
st.set_page_config(page_title="Eco Travel Calculator",
                   page_icon="🌍",
                   layout="wide")

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Create tabs
tabs = st.tabs(["Eco Travel Calculator", "Service Registry"])

# Eco Travel Calculator tab
with tabs[0]:
    st.title("🌍 Eco Travel Calculator")
    st.markdown("""
        Compare the carbon footprint of different transportation methods for your journey.
        Enter your starting point and destination to get started.
    """)

    # Create two columns for input
    col1, col2 = st.columns(2)

    with col1:
        start_city = st.text_input("Starting City", placeholder="City, Country")

    with col2:
        end_city = st.text_input("Destination City", placeholder="City, Country")

    if start_city and end_city:
        # Calculate distance and get coordinates
        distance, start_coords, end_coords, loc1, loc2 = calculate_distance(
            start_city, end_city)

        if distance:
            st.markdown("### Journey Details")
            st.write(f"Total Distance: {distance:.2f} km")

            # Create and display map
            st.markdown("### Route Visualization")
            route_map = create_route_map(start_coords, end_coords)
            if route_map:
                folium_static(route_map)

            # Calculate emissions for different transport methods
            emissions = get_transport_comparison(distance, loc1, loc2)

            if emissions:
                st.markdown("### Available Transport Options")
                
                # Create emissions comparison chart with only valid options
                fig = go.Figure(data=[
                    go.Bar(name='CO2 Emissions',
                           x=list(emissions.keys()),
                           y=list(emissions.values()),
                           marker_color=['#2ECC71' if method in ['bicycle', 'walk']
                                       else '#95A5A6' if method == 'train'
                                       else '#FF9B9B' for method in emissions.keys()])
                ])

                fig.update_layout(title='CO2 Emissions by Transport Method (kg)',
                                  xaxis_title='Transport Method',
                                  yaxis_title='CO2 Emissions (kg)',
                                  template='simple_white',
                                  height=400)

                st.plotly_chart(fig, use_container_width=True)

                # Detailed breakdown
                st.markdown("### Detailed Breakdown")
                
                # Create columns based on number of available options
                cols = st.columns(len(emissions))
                
                # Transport mode icons
                icons = {
                    'plane': '✈️',
                    'car': '🚗',
                    'train': '🚂',
                    'bicycle': '🚲',
                    'walk': '🚶'
                }
                
                # Impact levels
                impact_levels = {
                    'plane': 'Highest impact',
                    'car': 'High impact',
                    'train': 'Medium impact',
                    'bicycle': 'No emissions',
                    'walk': 'No emissions'
                }

                for col, (mode, emission) in zip(cols, emissions.items()):
                    col.markdown(f"""
                        <div class="transport-card">
                            <h4>{icons.get(mode, '🚌')} {mode.title()}</h4>
                            <p>CO2: {emission:.2f} kg</p>
                            <p>{impact_levels.get(mode, 'Medium impact')}</p>
                        </div>
                    """, unsafe_allow_html=True)

                # Environmental impact context
                st.markdown("### Environmental Impact Context")
                most_eco = min(emissions.items(), key=lambda x: x[1])
                worst_option = max(emissions.items(), key=lambda x: x[1])
                
                if worst_option[1] > 0:  # Only show savings if there are emissions to save
                    saved_emissions = worst_option[1] - most_eco[1]
                    st.info(f"""
                        By choosing {most_eco[0]} instead of {worst_option[0]}, you could save {saved_emissions:.2f} kg of CO2 emissions.
                        This is equivalent to planting {(saved_emissions/21):.1f} trees! 🌱
                    """)
                else:
                    st.success(f"""
                        Great news! {most_eco[0].title()} produces no CO2 emissions for this journey! 🌱
                    """)

                # Send data to the registry
                try:
                    response = requests.post('http://localhost:3000/register', json={
                        'start_city': start_city,
                        'end_city': end_city,
                        'distance': distance,
                        'emissions': emissions
                    })
                    if response.status_code == 201:
                        st.success("Journey registered successfully!")
                    else:
                        st.error("Failed to register journey.")
                except Exception as e:
                    st.error(f"Error registering journey: {e}")

        else:
            st.error(
                "Unable to calculate distance between these cities. Please check the city names and try again."
            )
    else:
        st.info(
            "👆 Enter your journey details above to calculate the carbon footprint."
        )

# Service Registry tab
with tabs[1]:
    registry_service_form()  # Call the function to display the registry service form

# Footer
st.markdown("""
    ---
   
    Data sources:
    - Transport emission factors: European Environment Agency
    - Distance calculations: GeoPy
""")


