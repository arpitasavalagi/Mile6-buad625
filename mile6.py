import os
import requests
import zipfile
from io import BytesIO
import boto3
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs

from fnmatch import fnmatch

from zipfile import ZipFile
from io import BytesIO
import os
import re

import streamlit as st
import os


def download_and_extract_zip(url):
    # Parse the URL to get the file name from the query string or path
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    file_name = query.get('filename', [os.path.basename(parsed_url.path)])[0]  # Get filename from query or path

    if os.path.exists("./init"):
        shutil.rmtree("./init")
    os.makedirs("./init", exist_ok=True)

    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses

    # Create a ZipFile object with BytesIO
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall("./init")  # Extract all the contents into the subdirectory 'init'
    
    print(f"Files extracted to ./init")
    print(f"Downloaded ZIP file name: {file_name}")
    base_filename, ext = os.path.splitext(file_name)
    return(base_filename)



def compare_faces(sourceFile, targetFile):

    session = boto3.Session(
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"])
    client = session.client('rekognition')

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})

    facefound = 0
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        facefound = 1
        '''
        print(similarity)
        print('Thex face at ' +
              str(position['Left']) + ' ' +
              str(position['Top']) +
              ' matches with ' + similarity + '% confidence')
        '''

    imageSource.close()
    imageTarget.close()
    return facefound


def mile1():
    # Initialize lists to store data
    cust_ids = []
    bank_ids = []

    # Regex to match file names in the format XXXX_ID.jpg
    pattern = re.compile(r'^\d{4}_\d+\.jpg$')

    # Walk through the directory and subdirectories to find matching files
    for root, dirs, files in os.walk("./init"):
        for file in files:
            if pattern.match(file):
                # Extract the ID from the file name and append it to the lists
                parts = file.split('.')
                cust_id = parts[0]
\
                cust_ids.append(cust_id)
    
    print(cust_ids)
    combined_df = pd.DataFrame({
        'loginID': cust_ids,
    })
    # Convert the lists to DataFrames
    #image_ids_df = pd.DataFrame(image_ids, columns=['loginID'])
    #image_ids_df = pd.DataFrame(bank_ids, columns=['bankAcctID'])

    # Combine DataFrames if necessary, or handle them separately as needed
    # For now, assuming we save only image_ids_df

    # Specify the path to save the CSV file
    csv_path = "./mile1.csv"

    # Save the DataFrame to a CSV file
    combined_df.to_csv(csv_path, index=False)

    print(f"CSV file with image IDs saved to {csv_path}")
    
    combined_df['verifiedID'] = 0
    image_directory = "./identityPics-custID_PicID"
    for index, row in combined_df.iterrows():
        cust_id = row['loginID']
        # Build a pattern to match the files (xxxx_yyyyy.jpg)
        pattern = f"{cust_id}_*.jpg"
        for filename in os.listdir(image_directory):
            if fnmatch(filename, pattern):
                full_path = os.path.join(image_directory, filename)
                # Assuming there's a target image to compare with
                target_image_path = f'./init/{cust_id}_{bankAcctID}.jpg'  # You need to define this
                print(target_image_path)
                # Apply the compare_faces function
                result = compare_faces(full_path, target_image_path)
                print(result)
                combined_df.at[index, 'verifiedID'] = result
                break  # Assuming we only need to check the first matched file

    # Save the updated DataFrame back to CSV
    combined_df.to_csv(csv_path, index=False)
    return csv_path




def main():
    st.title('Data Processing and Prediction')
    
    # Input for URL
    url = st.text_input("Enter the URL of the zip file to process:")

    # Button to run the process
    if st.button("Process URL"):
        try:
            # Path where the output will be saved (adjust as necessary)
            output_file_name = run(url)  # Assume 'run' is modified to return the output file path

            # Show a link to download the result
            with open(output_file_name, "rb") as file:
                btn = st.download_button(
                    label="Download Prediction Results",
                    data=file,
                    file_name=os.path.basename(output_file_name),
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Failed to process URL: {e}")

if __name__ == "__main__":
    main()



