import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO
import smtplib
from email.message import EmailMessage

def fetch_pdf():
    load_dotenv()
    route_code = os.getenv('ROUTE_CODE')
    if not route_code:
        raise ValueError('ROUTE_CODE not found in environment variables')

    url = f'https://storage.googleapis.com/dd-front-cabin-dd-prod-5ab1/cabin_availability_{route_code}.pdf'
    
    headers = {
        'accept': 'application/pdf',
        'accept-language': 'en-GB,en;q=0.7',
        'origin': 'https://www.brittany-ferries.co.uk',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content

def send_email_notification(subject, body):
    load_dotenv()
    email_to = os.getenv('EMAIL_TO')
    email_from = os.getenv('EMAIL_FROM')
    email_host = os.getenv('EMAIL_HOST')
    email_port = int(os.getenv('EMAIL_PORT', 587))
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')

    if not all([email_to, email_from, email_host, email_port, email_user, email_pass]):
        print('Email settings are not fully configured in .env')
        return

    # Add the Brittany Ferries link to the email body
    body += '\n\nCheck live cabin availability: https://www.brittany-ferries.co.uk/cabin-availability'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        print('Notification email sent.')
    except Exception as e:
        print(f'Failed to send email: {str(e)}')

def check_cabin_availability(pdf_content):
    load_dotenv()
    date_time = os.getenv('SAILING_DATE_TIME', '').strip()
    cabin_indexes = os.getenv('CABIN_INDEXES', '').strip()
    if cabin_indexes:
        cabin_indexes = [int(idx) for idx in cabin_indexes.split(',') if idx.strip().isdigit()]
    else:
        cabin_indexes = None

    pdf_file = BytesIO(pdf_content)
    reader = PdfReader(pdf_file)
    found = False
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if date_time in line:
                parts = line.strip().split()
                # Find the index of the date_time in the parts
                try:
                    dt_index = parts.index(date_time.split()[0])
                    # The time is the next part
                    if parts[dt_index + 1] == date_time.split()[1]:
                        # The numbers follow
                        numbers = parts[dt_index + 2:]
                        if not numbers:
                            continue
                        if cabin_indexes is not None:
                            for idx in cabin_indexes:
                                if idx < len(numbers) and numbers[idx].isdigit() and int(numbers[idx]) > 0:
                                    print(f'Cabin(s) available for {date_time} at index {idx}: {numbers[idx]}')
                                    send_email_notification(
                                        subject=f'Cabin available for {date_time}',
                                        body=f'Cabin(s) available for {date_time} at index {idx}: {numbers[idx]}'
                                    )
                                    found = True
                        else:
                            for idx, num in enumerate(numbers):
                                if num.isdigit() and int(num) > 0:
                                    print(f'Cabin(s) available for {date_time} at index {idx}: {num}')
                                    send_email_notification(
                                        subject=f'Cabin available for {date_time}',
                                        body=f'Cabin(s) available for {date_time} at index {idx}: {num}'
                                    )
                                    found = True
                except (ValueError, IndexError):
                    continue
    if not found:
        print('No matching cabins available for the specified date and time.')

def main():
    try:
        pdf_content = fetch_pdf()
        check_cabin_availability(pdf_content)
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    main() 