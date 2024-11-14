from flask import Flask, request, jsonify
import pandas as pd
import spacy
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

# Load the English NLP model
nlp = spacy.load('en_core_web_sm')

# Load the CSV file into a DataFrame
def load_company_data():
    csv_file_path = r"C:\Users\zadec\OneDrive\Desktop\Cornell Tech\Studio\PitchRoom\companies.csv"  # Replace with the actual path to your CSV file
    df = pd.read_csv(csv_file_path)
    return df

company_df = load_company_data()

# Information Extraction Functions
def extract_information(text):
    doc = nlp(text)
    entities = {'PERSON': [], 'ORG': [], 'MONEY': [], 'PRODUCT': [], 'GPE': []}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    extracted_data = {
        'founder_name': entities['PERSON'][0] if entities['PERSON'] else 'N/A',
        'company_name': 'Census', # Hardcoded for now
        'funding_amount': entities['MONEY'][0] if entities['MONEY'] else 'N/A',
        'location': entities['GPE'][0] if entities['GPE'] else 'N/A',
        'product_description': extract_product_description(text)
    }
    return extracted_data

def extract_product_description(text):
    sentences = [sent.text for sent in nlp(text).sents if any(keyword in sent.text.lower() for keyword in ['product', 'solution', 'service'])]
    return sentences[0] if sentences else 'N/A'

# Data Enrichment Function
def enrich_data(data, df):
    company_name = data.get('company_name', 'N/A')
    if company_name != 'N/A':
        matched_companies = df[df['Company Name'].str.lower() == company_name.lower()]
        
        if not matched_companies.empty:
            company_info = matched_companies.iloc[0].fillna('N/A')

            data['founders'] = company_info.get('Team', 'N/A')
            data['company_website'] = company_info.get('Website', 'N/A')
            data['company_description'] = company_info.get('Description', 'N/A')
            data['team_size'] = company_info.get('Headcount', 'N/A')
            data['customer_type'] = company_info.get('Customer Type', 'N/A')
            data['country'] = company_info.get('Country', 'N/A')
            data['state'] = company_info.get('State', 'N/A')
            data['last_funding_type'] = company_info.get('Last Funding Type', 'N/A')
            
    else:
        data['founders'] = 'N/A'
        data['company_website'] = 'N/A'
        data['company_description'] = 'N/A'
        data['team_size'] = 'N/A'
        data['customer_type'] = 'N/A'
        data['country'] = 'N/A'
        data['state'] = 'N/A'
        data['last_funding_type'] = 'N/A'
    
    return data



@app.route('/process_pitch', methods=['POST'])
def process_pitch():
    print("here")  # This will print if the POST request is reached
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')

        if email_text.strip():
            # Extract and enrich the data
            extracted_data = extract_information(email_text)
            enriched_data = enrich_data(extracted_data, company_df)
            print(enriched_data)  # You should also see this print in the logs
            return jsonify(enriched_data), 200
        else:
            return jsonify({'error': 'Please provide an email pitch to process.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
