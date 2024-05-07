import streamlit as st
import requests
import json
import base64
from PIL import Image
import fitz  # PyMuPDF
import io

def load_image(image_file):
    """Load an image file."""
    return Image.open(image_file)

def get_document_types():
    """Retrieve all document types from the API."""
    url = "https://edms-demo.epik.live/api/v4/document_types/"
    document_types = []
    next_url = url
    while next_url:
        response = requests.get(next_url, auth=('admin', '1234@BCD'))
        if response.status_code == 200:
            data = response.json()
            document_types.extend(data['results'])
            next_url = data['next']  # Update next_url for the next iteration
        else:
            return []  # Return an empty list if there's an error
    return document_types

def get_metadata_types(doc_type_id):
    """Retrieve metadata types for a specific document type."""
    url = f"https://edms-demo.epik.live/api/v4/document_types/{doc_type_id}/metadata_types/"
    response = requests.get(url, auth=('admin', '1234@BCD'))
    if response.status_code == 200:
        return response.json()['results']
    else:
        return []

def save_to_json(file_base64, file_name, doc_type_id, metadata_values):
    """Save data to a JSON file with the specified structure."""
    metadata_list = [{"id": id, "value": value} for id, value in metadata_values.items()]
    data = {
        "file_base64": file_base64,
        "dms_domain": "edms-demo.epik.live",
        "file_name": file_name,
        "doctype_id": doc_type_id,
        "docmeta_data": metadata_list
    }
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)

def save_and_download_json(file_base64, file_name, doc_type_id, metadata_values):
    """Save and download the generated JSON file."""
    progress_text = st.markdown(" ***Please wait a moment for the data submission process.***")
    progress_bar = st.progress(0)
    save_to_json(file_base64, file_name, doc_type_id, metadata_values)
    
    progress_bar.progress(40) 
    with open('data.json', 'rb') as f:
        data = f.read()
    progress_bar.progress(75)
    st.download_button(label="Download JSON", data=data, file_name="data.json", mime="application/json")
    json_data = json.loads(data)
    
    # Sending the data to the API endpoint
    response = send_data_to_api(json_data)
    if response.status_code == 200:
        
        progress_bar.progress(100)
        progress_text.markdown(" :green[Data submission completed successfully!]")  # Complete the progress bar only if API call is successful
    else:
        st.error(f"Failed to send data to the API: {response.status_code}")
        progress_bar.progress(0)
def send_data_to_api(json_data):
    """Send JSON data to a specified API endpoint."""
    url = "https://dms.api.epik.live/api/processBase64File"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=json_data, headers=headers)
    return response
def main():
    st.set_page_config(layout="wide", page_title="Document Viewer App")
    st.markdown("<style>.reportview-container .main .block-container{max-width: 90%;}</style>", unsafe_allow_html=True)

    document_types = get_document_types()
    doc_type_options = {doc['label']: doc['id'] for doc in document_types}

    col_title1, col_title2 = st.columns([1,8])
    with col_title2:
        st.title('Document Viewer App')

    col_empty_1, col_select, col_upload, col_empty_4 = st.columns([1,4,4,1])
    with col_select:
        doc_type = st.selectbox("Choose the document type:", list(doc_type_options.keys()), key='doc_type')
    with col_upload:
        uploaded_file = st.file_uploader("Upload your document", type=['png', 'jpg', 'jpeg', 'pdf'], key="uploaded_file")

    if uploaded_file:
        # Using the uploaded file's name as a part of each metadata input key to ensure freshness
        file_key = uploaded_file.name + str(uploaded_file.size)

    col1, col2_emt, col3_input_filed = st.columns([7,0.2,2.8])
    with col1:
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                display_pdf(uploaded_file)
            else:
                display_image(uploaded_file)

    with col3_input_filed:
        if doc_type and uploaded_file:
            metadata_types = get_metadata_types(doc_type_options[doc_type])
            metadata_values = {meta['metadata_type']['id']: st.text_input(meta['metadata_type']['label'], key=f"meta_{meta['metadata_type']['id']}_{file_key}") for meta in metadata_types}
            if st.button("Done and Submit", type="primary"):
                handle_submission(uploaded_file, doc_type_options[doc_type], metadata_values)

def display_pdf(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
        total_pages = len(doc)
        current_page = st.session_state.get('current_page', 0)

        col_empty_PDF, col1_titlePDF, col2, col3 = st.columns([1,5,2,2])
        with col1_titlePDF:
            st.markdown("#### Preview of the PDF:")

        # Navigation buttons
        with col2:
            if st.button('Previous page', key='prev_page'):
                if current_page > 0:
                    current_page -= 1
                    st.session_state['current_page'] = current_page
            
        with col3:
            if st.button('Next page', key='next_page'):
                if current_page < total_pages - 1:
                    current_page += 1
                    st.session_state['current_page'] = current_page

        # Display current page
        page = doc.load_page(current_page)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        st.image(img, caption=f"Page {current_page + 1} of {total_pages}", use_column_width=True)
    except Exception as e:
        st.error(f"Error in PDF processing: {e}")



def display_image(uploaded_file):
    image = load_image(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

def handle_submission(uploaded_file, doc_type_id, metadata_values):
    file_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    file_name = uploaded_file.name
    save_and_download_json(file_base64, file_name, doc_type_id, metadata_values)
    st.success("Data saved and submitted successfully!")

if __name__ == "__main__":
    main()
