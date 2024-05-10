import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
st.set_page_config(layout="wide", page_title="Document Viewer App")
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
def get_all_document_types(auth):
    url = "https://edms-demo.epik.live/api/v4/document_types/"
    document_types = []
    while url:
        response = requests.get(url, auth=auth)
        data = response.json()
        document_types.extend(data['results'])
        url = data['next']
    return document_types

# Hàm để lấy tất cả documents
def get_all_documents(auth):
    documents = []
    url = "https://edms-demo.epik.live/api/v4/documents/"
    while url:
        response = requests.get(url, auth=auth)
        data = response.json()
        documents.extend(data['results'])
        url = data['next']  # Cập nhật URL cho trang kế tiếp nếu có
    return documents


# Giao diện
def main():
    col_title_empty1, col_title, col_title_empty2 = st.columns([1,8,1])
    with col_title:
        st.title('Search documents')

    auth = HTTPBasicAuth('admin', '1234@BCD')  # Prepare the authentication
    # Sử dụng một spinner cho cả hai lời gọi API
    with st.spinner('Please wait...'):
        # Lấy tất cả document types và documents
        document_types = get_all_document_types(auth)
        document_type_options = {dt['label']: dt['id'] for dt in document_types}
        all_documents = get_all_documents(auth)
    # Chia giao diện thành hai cột
    col_empty1,col1,col_empty2, col2,col_empty3 = st.columns([1,3.5,1,3.5,1])

    # Cột 1: Chọn và tìm kiếm dựa trên loại tài liệu
    with col1:
        st.markdown('#### Search documents by document type')
        selected_type_label = st.selectbox("Select document type:", options=list(document_type_options.keys()))

        if selected_type_label:
            selected_type_id = document_type_options[selected_type_label]
            filtered_documents = [doc for doc in all_documents if doc['document_type']['id'] == selected_type_id]
            # Using a dictionary to avoid duplicates and maintain ID linkage
            label_to_docs = {}
            for doc in filtered_documents:
                if doc['label'] in label_to_docs:
                    label_to_docs[doc['label']].append(doc['id'])
                else:
                    label_to_docs[doc['label']] = [doc['id']]

            selected_docs = st.multiselect("Select or search documents based on the selected document type:", options=list(label_to_docs.keys()))

            if selected_docs:
                st.write(f"You have selected the documents:")
                for doc in filtered_documents:
                    if doc['label'] in selected_docs:
                        # Tạo URL preview
                        doc_url = f"https://edms-demo.epik.live/#/documents/documents/{doc['id']}/preview/"
                        # Hiển thị link tới tài liệu
                        st.markdown(f"[{doc['label']}]({doc_url})")

    # Cột 2: Tìm kiếm độc lập các tài liệu
    with col2:
        st.markdown('#### Search for independent documents')
        search_query = st.text_input("Enter the name of the document to search for:")
        if search_query:
            search_results = [doc for doc in all_documents if search_query.lower() in doc['label'].lower()]
            if search_results:
                for doc in search_results:
                    doc_url = f"https://edms-demo.epik.live/#/documents/documents/{doc['id']}/preview/"
                    st.markdown(f"[{doc['label']}]({doc_url})")
            else:
                st.write("No documents were found matching your search.")

if __name__ == "__main__":
    main()
