import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('admin', '1234@BCD')  
st.title("Advanced Search for: Document")

# Persistency Section
st.header("Persistency")
save_results = st.checkbox("Save results", help="Store the search results to speed up paging and for later browsing.")

# Search Logic Section
st.header("Search logic")
match_all = st.radio("Match all:", ["Yes", "No"], index=1, help="Return only results that match all fields.")

# Cabinets Section
st.header("Cabinets")
cabinet_id = st.text_input("Cabinet ID:", help="The database ID of the cabinet.")
cabinets = st.text_input("Cabinets:", help="A short text used to identify the cabinet.")

# Comments Section
st.header("Comments")
comments = st.text_area("Comments:")

# Document Files Section
st.header("Document files")
mime_type = st.text_input("Document file MIME type:", help="The document file's MIME type. Some examples: 'text/plain' or 'image/jpeg'.")
checksum = st.text_input("Document file checksum:", help="A hash/checkdigit/fingerprint generated from the document's binary data.")
file_content = st.text_area("Document file content:", help="The actual text content as extracted by the document parsing backend.")
filename = st.text_input("Document file filename:")

# Metadata Section
st.header("Document metadata")
metadata_type = st.text_input("Metadata type:", help="Name used by other apps to reference this metadata type. Do not use python reserved words, or spaces.")
metadata_value = st.text_input("Metadata value:", help="The actual value stored in the metadata type field for the document.")

# Document Types Section
st.header("Document types")
document_type_id = st.text_input("Document type ID:", help="The database ID of the document type.")
document_type_label = st.text_input("Document type label:", help="A short text identifying the document type.")

# Document Versions Section
st.header("Document versions")
version_ocr = st.text_area("Document version OCR:", help="The actual text content extracted by the OCR backend.")

# Documents Section
st.header("Documents")
created = st.text_input("Created:", help="The date and time of the document creation.")
description = st.text_input("Description:", help="An optional short text describing a document.")
label = st.text_input("Label:", help="A short text identifying the document.")
uuid = st.text_input("UUID:", help="UUID of a document, universally Unique ID. An unique identifier generated for each document.")

# Signature Captures Section
st.header("Signature captures")
signature_text = st.text_input("Signature capture text:", help="Print version of the captured signature.")
signature_first_name = st.text_input("Signature capture user first name:")
signature_last_name = st.text_input("Signature capture user last name:")
signature_username = st.text_input("Signature capture user username:", help="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")

# Tags Section
st.header("Tags")
tag_id = st.text_input("Tag ID:", help="The database ID of the tag.")
tag_color = st.text_input("Tag color:", help="The RGB color values for the tag.")
tag_label = st.text_input("Tag label:", help="A short text used as the tag name.")

# Workflow Instances Section
st.header("Workflow instances")
workflow_comment = st.text_area("Document workflow transition comment:")
def fetch_all_documents():
    url = "https://edms-demo.epik.live/api/v4/documents/"
    all_documents = []
    while url:
        response = requests.get(url, auth=auth)
        data = response.json()
        all_documents.extend(data['results'])
        url = data['next']
    return all_documents
def fetch_all_document_types():
    url = "https://edms-demo.epik.live/api/v4/document_types/"
    all_document_types = []
    while url:
        response = requests.get(url, auth=auth)
        data = response.json()
        all_document_types.extend(data['results'])
        url = data['next']
    return all_document_types

def fetch_documents_from_url(documents_url):
    all_documents = []
    while documents_url:
        response = requests.get(documents_url, auth=auth)
        data = response.json()
        all_documents.extend(data['results'])
        documents_url = data['next']
    return all_documents

if st.button("Search"):
    # Fetch Cabinets Data
    cabinets_response = requests.get("https://edms-demo.epik.live/api/v4/cabinets/", auth=auth)
    cabinets_data = cabinets_response.json()

    # Store documents URLs to fetch
    documents_urls = []

    # Find matching cabinets
    for cabinet in cabinets_data['results']:
        if cabinet['label'] == cabinets or str(cabinet['id']) == cabinet_id:
            documents_urls.append(cabinet['documents_url'])

    cabinet_documents = []
    if documents_urls:
        # Fetch and store documents for each matching cabinet
        for documents_url in documents_urls:
            documents_response = requests.get(documents_url, auth=auth)
            documents_data = documents_response.json()
            cabinet_documents.extend(documents_data['results'])

        # Display Document Links for Cabinet documents
        for document in cabinet_documents:
            document_url = f"https://edms-demo.epik.live/#/documents/documents/{document['id']}/preview/"
            st.markdown(f"[{document['label']}]({document_url})")
    else:
        st.write("No matching cabinet found.")

    # Check if any Document Files Section input is provided
    if mime_type or checksum or filename:
        # Fetch all documents and filter based on Document Files Section inputs
        all_documents = fetch_all_documents()
        filtered_documents = []
        for document in all_documents:
            if mime_type and mime_type != document['file_latest']['mimetype']:
                continue
            if checksum and checksum != document['file_latest']['checksum']:
                continue
            if filename and filename != document['file_latest']['filename']:
                continue
            filtered_documents.append(document)

        # Display Document Links for filtered documents
        if filtered_documents:
            for document in filtered_documents:
                document_url = f"https://edms-demo.epik.live/#/documents/documents/{document['id']}/preview/"
                st.markdown(f"[{document['label']}]({document_url})")
        else:
            st.write("No matching documents found.")

    # Fetch all Document Types and filter based on Document Types Section inputs
    if document_type_id or document_type_label:
        all_document_types = fetch_all_document_types()
        filtered_document_types = []
        for doc_type in all_document_types:
            if document_type_id and str(doc_type['id']) != document_type_id:
                continue
            if document_type_label and doc_type['label'] != document_type_label:
                continue
            filtered_document_types.append(doc_type)

        document_type_documents = []
        for doc_type in filtered_document_types:
            document_type_documents.extend(fetch_documents_from_url(doc_type['documents_url']))

        # Display Document Links for Document Type documents
        if document_type_documents:
            for document in document_type_documents:
                document_url = f"https://edms-demo.epik.live/#/documents/documents/{document['id']}/preview/"
                st.markdown(f"[{document['label']}]({document_url})")
        else:
            st.write("No matching documents found.")
st.button("Cancel")
