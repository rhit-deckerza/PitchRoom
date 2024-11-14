# dashboard.py

import streamlit as st
import pandas as pd
import requests
import spacy  # For NLP tasks repace with chatGPT later

# Load the English NLP model
nlp = spacy.load('en_core_web_sm')

# Load the CSV file into a DataFrame
@st.cache_resource # toc cache the DF loading to prevent it from reloading everytime
def load_company_data():
    csv_file_path = '/Users/deberend/Desktop/Cornell Tech/Studio /Prototype/data/10_4_Differential_Harmonic_Export.csv'  # Replace with the actual path to your CSV file
    df = pd.read_csv(csv_file_path)
    return df

# All companies of the scraped harmonic data
company_df = load_company_data()

# Information Extraction Functions
def extract_information(text):
    doc = nlp(text)
    entities = {'PERSON': [], 'ORG': [], 'MONEY': [], 'PRODUCT': [], 'GPE': []}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # Simplify and select the most relevant entities
    extracted_data = {
        'founder_name': entities['PERSON'][0] if entities['PERSON'] else 'N/A',
        'company_name': entities['ORG'][0] if entities['ORG'] else 'Census', # Hard coded the company Census here as the NLP model is not recognizing the company, which is something to look into later 
        'funding_amount': entities['MONEY'][0] if entities['MONEY'] else 'N/A',
        'location': entities['GPE'][0] if entities['GPE'] else 'N/A',
        'product_description': extract_product_description(text)
    }
    st.write("Extracted Company Name:", extracted_data['company_name'])
    return extracted_data

def extract_product_description(text):
    # Extract sentences that likely contain product descriptions
    sentences = [sent.text for sent in nlp(text).sents if any(keyword in sent.text.lower() for keyword in ['product', 'solution', 'service'])]
    return sentences[0] if sentences else 'N/A'

# Data Enrichment Function
def enrich_data(data, df):
    # Attempt to find the company in the DataFrame
    company_name = data.get('company_name', 'N/A')
    if company_name != 'N/A':
        # Perform a case-insensitive search for the company name
        matched_companies = df[df['Company Name'].str.lower() == company_name.lower()]
        #print(matched_companies)
        
        #if matched_companies.empty:
         #   # If no exact match is found, consider using fuzzy matching
          #  matched_companies = fuzzy_match_company(company_name, df)
        
        if not matched_companies.empty:
            # Assuming there's only one matching company
            company_info = matched_companies.iloc[0].fillna('N/A')

            data['founders'] = company_info.get('Team', 'N/A')
            data['company_website'] = company_info.get('Website', 'N/A')
            data['company_description'] = company_info.get('Description', 'N/A')
            data['team_size'] = company_info.get('Headcount', 'N/A')
            data['customer_type'] = company_info.get('Customer Type', 'N/A')  # Add Customer Type
            data['country'] = company_info.get('Country', 'N/A')
            data['state'] = company_info.get('State', 'N/A')
            data['last_funding_type'] = company_info.get('Last Funding Type', 'N/A')
            
            # Add more fields as needed

    else:
        # Company name not extracted
        # Set default values if company name was not extracted
        data['founders'] = 'N/A'
        data['company_website'] = 'N/A'
        data['company_description'] = 'N/A'
        data['team_size'] = 'N/A'
        data['customer_type'] = 'N/A'
        data['country'] = 'N/A'
        data['state'] = 'N/A'
        data['last_funding_type'] = 'N/A'
    
    return data

# Data Enrichment Function (Mocked)
def enrich_data_mock(data):
    # Simulated enriched data
    data['company_website'] = 'https://www.example.com'
    data['company_description'] = 'Example Company is a leading provider of innovative solutions.'
    #data['company_logo'] = 'https://via.placeholder.com/150'  # Placeholder image URL
    data['team_size'] = '5-10 employees'
    return data

# Data Enrichment Function
def enrich_data_API(data):
    # This function would be to fetch the data from online databases (for later stage)
    CLEARBIT_API_KEY = 'YOUR_CLEARBIT_API_KEY'

    headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}

    # Enrich company data using Clearbit
    if data['company_name'] != 'N/A':
        company_response = requests.get(f"https://company.clearbit.com/v2/companies/find?name={data['company_name']}", headers=headers)
        if company_response.status_code == 200:
            company_info = company_response.json()
            data['company_website'] = company_info.get('domain', 'N/A')
            data['company_description'] = company_info.get('description', 'N/A')
            data['company_logo'] = company_info.get('logo', '')
            data['team_size'] = company_info.get('metrics', {}).get('employees', 'N/A')
        else:
            data['company_website'] = 'N/A'
            data['company_description'] = 'N/A'
            data['company_logo'] = ''
            data['team_size'] = 'N/A'
    else:
        data['company_website'] = 'N/A'
        data['company_description'] = 'N/A'
        data['company_logo'] = ''
        data['team_size'] = 'N/A'
    
    return data

# Data Display Function
def display_data(data):
    st.header('Structured Pitch Information')

    st.subheader('Founder Information')
    st.write(f"**Name:** {data['founder_name']}")
    # You can add more fields if available

    st.subheader('Company Information')
    st.write(f"**Founders:** {data['founders']}")
    st.write(f"**Company Name:** {data['company_name']}")
    st.write(f"**Website:** {data['company_website']}")
    st.write(f"**Description:** {data['company_description']}")
    st.write(f"**Team Size:** {data['team_size']}")
    st.write(f"**Customer Type:** {data['customer_type']}")
    st.write(f"**Country:** {data['country']}")
    st.write(f"**State:** {data['state']}")
    st.write(f"**Last Funding Type:** {data['last_funding_type']}")

    #if data['company_logo']:
    #    st.image(data['company_logo'], caption=data['company_name'])

    st.subheader('Funding Information')
    st.write(f"**Requested Amount:** {data['funding_amount']}")
    st.write(f"**Location:** {data['location']}")
    st.write(f"**Product Description:** {data['product_description']}")

# Main Application Code
def main():
    # App Title and Description
    st.title('Pitch Room Prototype')
    st.subheader('An AI Email Assistant for Venture Capitalists')
    st.markdown('Upload an email pitch to see it transformed into structured data.')

    # Email Input Section
    uploaded_file = st.file_uploader('Upload an Email Pitch (Text File)', type='txt')
    email_text = ''
    if uploaded_file is not None:
        email_text = uploaded_file.read().decode('utf-8')
    else:
        email_text = st.text_area('Or Paste Email Pitch Here')

    # Process Button
    if st.button('Process Pitch'):
        if email_text.strip():
            with st.spinner('Processing...'):
                extracted_data = extract_information(email_text)
                enriched_data = enrich_data(extracted_data, company_df)
                display_data(enriched_data)
        else:
            st.warning('Please provide an email pitch to process.')

if __name__ == '__main__':
    main()
