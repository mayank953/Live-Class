import streamlit as st
import requests
import json

st.title("AI Research Generator")

API_URL = "https://mb26kncdfg.execute-api.us-east-1.amazonaws.com/dev/research"

topic = st.text_input("Enter a research topic:", "AI in Healthcare")

if st.button("Generate Research Report"):
    with st.spinner("Generating..."):
        payload = json.dumps({"topic": topic})
        headers = {"Content-Type": "application/json"}

        response = requests.post(API_URL, headers=headers, data=payload)

        if response.status_code == 200:
            try:
                data = response.json()
                body = json.loads(data.get("body", "{}"))

                st.success(body.get("message", ""))

                st.subheader("📄 Research Report")
                st.write(body.get("response", ""))

                st.info(f"S3 Bucket: {body.get('s3_bucket')}")
                st.info(f"S3 Key: {body.get('s3_key')}")

            except Exception as e:
                st.error(f"Error parsing response: {e}")
                st.write(response.text)
        else:
            st.error(f"Request failed with status: {response.status_code}")
            st.write(response.text)
