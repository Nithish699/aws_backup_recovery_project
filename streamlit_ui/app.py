import streamlit as st
import requests
import os

st.set_page_config(layout="wide")
st.title("AWS S3 Management Console")

API_BASE_URL = "http://localhost:5001"

# --- Upload Section ---
st.header("Upload File to S3")
upload_bucket = st.text_input("Bucket Name (for Upload)", key="upload_bucket_key", placeholder="your-s3-bucket-name")
s3_object_key_upload = st.text_input("S3 Object Key (e.g., folder/filename.ext)", key="upload_s3_key", placeholder="backup_folder/my_image.png")
uploaded_file = st.file_uploader("Choose a file to upload", key="file_uploader")

if st.button("Upload File", key="upload_button"):
    if uploaded_file is not None and upload_bucket and s3_object_key_upload:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        try:
            with st.spinner(f'Uploading {uploaded_file.name} to {upload_bucket}/{s3_object_key_upload}...'):
                res = requests.post(f"{API_BASE_URL}/upload/{upload_bucket}/{s3_object_key_upload}", files=files)
                res.raise_for_status()
                st.success(res.json().get('message', 'File uploaded successfully!'))
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Response content: {e.response.text}")
        except Exception as e:
            st.error(f"Upload failed: {e}")
    else:
        st.warning("Please provide bucket name, S3 object key, and select a file.")

st.markdown("---")

# --- List Files Section ---
st.header("List Files in S3 Bucket")
list_bucket = st.text_input("Bucket Name (for Listing)", key="list_bucket_key", placeholder="your-s3-bucket-name")

if st.button("List Files", key="list_button"):
    if list_bucket:
        with st.spinner(f'Listing files in {list_bucket}...'):
            try:
                res = requests.get(f"{API_BASE_URL}/list/{list_bucket}")
                res.raise_for_status()
                data = res.json()
                if 'files' in data and data['files']:
                    st.write(f"Files in '{list_bucket}':")
                    st.table(data['files'])
                elif 'files' in data and not data['files']:
                    st.info(f"No files found in bucket '{list_bucket}'.")
                else:
                    st.error(f"Failed to list files: {data.get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    st.error(f"Response content: {e.response.text}")
            except Exception as e:
                st.error(f"Failed to list files: {e}")
    else:
        st.warning("Please provide a bucket name to list files.")

st.markdown("---")

# --- Download File Section ---
st.header("Download File from S3")
download_bucket = st.text_input("Bucket Name (for Download)", key="download_bucket_key", placeholder="your-s3-bucket-name")
s3_object_key_download = st.text_input("S3 Object Key to Download", key="download_s3_key", placeholder="backup_folder/file.png")

if st.button("Prepare Download", key="prepare_download_button"):
    if download_bucket and s3_object_key_download:
        with st.spinner(f'Fetching {s3_object_key_download} from {download_bucket}...'):
            try:
                res = requests.get(f"{API_BASE_URL}/download/{download_bucket}/{s3_object_key_download}", stream=True)
                res.raise_for_status()
                
                file_name_for_download = s3_object_key_download.split('/')[-1]
                
                st.download_button(
                    label=f"Click to download '{file_name_for_download}'",
                    data=res.content,
                    file_name=file_name_for_download,
                    mime='application/octet-stream'
                )
                st.success(f"File '{s3_object_key_download}' is ready for download.")
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    st.error(f"Response content: {e.response.text}")
            except Exception as e:
                st.error(f"Download preparation failed: {e}")
    else:
        st.warning("Please provide bucket name and S3 object key for download.")

st.markdown("---")

# --- Delete File Section ---
st.header("Delete File from S3")

# Input fields
delete_bucket = st.text_input(
    "Bucket Name", 
    key="delete_bucket_key",
    placeholder="your-s3-bucket-name"
)

s3_object_key_delete = st.text_input(
    "File Path to Delete", 
    key="delete_s3_key",
    placeholder="folder/file.txt"
)

if st.button("Delete File", type="primary"):
    if not delete_bucket or not s3_object_key_delete:
        st.warning("Both bucket name and file path are required!")
        st.stop()
    
    with st.spinner(f"Deleting {s3_object_key_delete}..."):
        try:
            # URL encode the object key in case it has special characters
            from urllib.parse import quote
            encoded_key = quote(s3_object_key_delete, safe='')
            url = f"{API_BASE_URL}/delete/{delete_bucket}/{encoded_key}"
            
            response = requests.delete(url, timeout=15)
            
            if response.status_code == 200:
                st.success("File deleted successfully!")
            else:
                st.error(f"Delete failed (Status {response.status_code})")
                st.json(response.json())  # Show error details
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

st.markdown("---")
st.caption("Ensure the Flask API is running on http://localhost:5001")