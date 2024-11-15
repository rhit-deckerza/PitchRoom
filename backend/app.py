from flask import Flask, request, jsonify
import pandas as pd
import spacy
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

# Load chatgpt key
openai.api_key = os.environ['OPENAI_API_KEY'] # Might need to reactivate the right path to the OPEN_API_KEY

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


def extract_information(text):
    prompt = f"""
    Extract the following details from the email below:
    1. Founder Name(s)
    2. Company Name
    3. Funding Amount Requested
    4. Location
    5. Product Description

    Return the information in JSON format with the following keys:
    - founder_name
    - company_name
    - funding_amount
    - location
    - product_description

    Email:
    \"\"\"
    {text}
    \"\"\"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if accessible
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        import json
        extracted_data = json.loads(response['choices'][0]['message']['content'])

        # Print for debugging purposes and to check what chatgpt collects from the email
        print("Extracted Data:", extracted_data)

    except json.JSONDecodeError:
        st.error("Failed to parse the extracted information. Please check the email content.")
        extracted_data = {}

    except openai.error.OpenAIError as e:
        st.error(f"An error occurred while contacting OpenAI: {e}")
        extracted_data = {}

    # Ensure all keys are present with default values
    return {
        "founder_name": extracted_data.get("founder_name", "N/A"),
        "company_name": extracted_data.get("company_name", "N/A"),
        "funding_amount": extracted_data.get("funding_amount", "N/A"),
        "location": extracted_data.get("location", "N/A"),
        "product_description": extracted_data.get("product_description", "N/A")
    }


# Information Extraction Functions
def extract_information_SpaCy(text):
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
    st.write("Extracted Company Name:", extracted_data['company_name']) #For debugging
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
            data['team_size'] = company_info.get('Headcount', 'N/A') #look into whether headcount is teamsize, probably not 
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
