import streamlit as st
import requests
import threading
import time
import json
from urllib.parse import urlparse

def send_heartbeat(service_id, service_url, registry_urls):
    def heartbeat():
        data = {
            'serviceId': service_id,
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'myUrl': service_url
        }
        json_data = json.dumps(data)

        while True:
            for reg_url in registry_urls:
                try:
                    url = urlparse(reg_url)
                    hostname = url.hostname
                    port = url.port or (443 if url.scheme == 'https' else 80)
                    path = '/heartbeat'
                    headers = {
                        'Content-Type': 'application/json',
                        'Content-Length': str(len(json_data))
                    }

                    response = requests.post(f"{url.scheme}://{hostname}:{port}{path}", headers=headers, data=json_data)
                    if response.status_code == 200:
                        print(f"{reg_url}: Heartbeat sent. Response: {response.text}")
                        if response.text == "Reregister":
                            print(f"{reg_url}: Service needs to be re-registered.")
                    else:
                        print(f"{reg_url}: Failed to send heartbeat. Status code: {response.status_code}")
                except Exception as e:
                    print(f"{reg_url}: Error sending heartbeat. Response: {e}")

            time.sleep(30)  # Send heartbeat every 30 seconds

    threading.Thread(target=heartbeat, daemon=True).start()

def registry_service_form():
    st.title("🔧 Service Registry")
    st.markdown("""
        Register and deregister services in the registry.
    """)

    # Initialize session state for input fields
    if 'service_id' not in st.session_state:
        st.session_state.service_id = ""
    if 'service_url' not in st.session_state:
        st.session_state.service_url = ""
    if 'deregister_service_id' not in st.session_state:
        st.session_state.deregister_service_id = ""
    if 'deregister_service_url' not in st.session_state:
        st.session_state.deregister_service_url = ""

    # Register service form
    st.markdown("### Register Service")
    with st.form(key='register_form'):
        service_id = st.text_input("Service ID", value=st.session_state.service_id)
        service_url = st.text_input("Service URL", value=st.session_state.service_url)
        register_button = st.form_submit_button(label='Register Service')

    if register_button:
        if service_id and service_url:
            try:
                response = requests.post('http://localhost:3000/register', json={
                    'serviceId': service_id,
                    'myUrl': service_url
                })
                if response.status_code == 200:
                    st.success("Service registered successfully!")
                    # Start sending heartbeats
                    registry_urls = ["http://localhost:3000"]  # Add your registry URLs here
                    send_heartbeat(service_id, service_url, registry_urls)
                    # Clear input fields
                    st.session_state.service_id = ""
                    st.session_state.service_url = ""
                else:
                    st.error("Failed to register service.")
            except Exception as e:
                st.error(f"Error registering service: {e}")
        else:
            st.error("Please provide both Service ID and Service URL.")

    # Deregister service form
    st.markdown("### Deregister Service")
    with st.form(key='deregister_form'):
        deregister_service_id = st.text_input("Service ID to Deregister", value=st.session_state.deregister_service_id)
        deregister_service_url = st.text_input("Service URL to Deregister", value=st.session_state.deregister_service_url)
        deregister_button = st.form_submit_button(label='Deregister Service')

    if deregister_button:
        if deregister_service_id and deregister_service_url:
            try:
                response = requests.post('http://localhost:3000/deregister', json={
                    'serviceId': deregister_service_id,
                    'myUrl': deregister_service_url
                })
                if response.status_code == 200:
                    st.success("Service deregistered successfully!")
                    # Clear input fields
                    st.session_state.deregister_service_id = ""
                    st.session_state.deregister_service_url = ""
                else:
                    st.error("Failed to deregister service.")
            except Exception as e:
                st.error(f"Error deregistering service: {e}")
        else:
            st.error("Please provide both Service ID and Service URL.")
