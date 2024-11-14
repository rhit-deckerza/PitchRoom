from openai import OpenAI
import csv

# Function to generate pitch email using GPT
def generate_pitch_email(company_name, highlights, description, team, customer_type, funding_total, client):
    prompt = f"""
    You are a VC advisor. Write a persuasive and concise pitch email for a company seeking funding. 

    Company Name: {company_name}
    Highlights: {highlights}
    Description: {description}
    Team: {team}
    Customer Type: {customer_type}
    Funding Total So Far: {funding_total}

    The email should highlight the company's unique value proposition, team strengths, and investment potential.
    """

    

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )
   
    print(chat_completion.choices[0].message)
    # Extract the generated pitch email
    return chat_completion.choices[0].message.content.strip()

# Function to read CSV and generate pitch emails
def generate_pitches_from_csv(csv_file_path, output_csv_file_path):

    # Open CSV file for reading
    with open(csv_file_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    # Prepare list to store results
    output_rows = []

    for row in rows:
        company_name = row['Company Name']
        highlights = row['Company Highlights']
        description = row['Description']
        team = row['Team']
        customer_type = row['Customer Type']
        funding_total = row['Funding Total']

        # Generate pitch email using GPT
        pitch_email = generate_pitch_email(company_name, highlights, description, team, customer_type, funding_total, client)

        # Append the company name and generated email to the output rows
        output_rows.append({
            'Company Name': company_name,
            'Generated Pitch Email': pitch_email
        })
        break

    # Write only the company name and generated email to a new CSV file
    with open(output_csv_file_path, mode="w", encoding="utf-8", newline="") as outfile:
        fieldnames = ['Company Name', 'Generated Pitch Email']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Pitch emails have been successfully generated and saved to {output_csv_file_path}")

# Example usage
if __name__ == "__main__":
    # Set your OpenAI API key

    # Path to the input CSV file containing company data
    input_csv_file = 'companies.csv'
    
    # Path to the output CSV file that will contain only the company name and generated pitch emails
    output_csv_file = 'companies_with_pitches.csv'
    
    # Generate the pitches and save to the new CSV file
    generate_pitches_from_csv(input_csv_file, output_csv_file)
