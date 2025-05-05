import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO
import smtplib
from email.message import EmailMessage


def load_config():
    load_dotenv()
    config = {
        'route_code': os.getenv('ROUTE_CODE'),
        'sailing_date_time': os.getenv('SAILING_DATE_TIME', '').strip(),
        'cabin_indexes': os.getenv('CABIN_INDEXES', '').strip(),
        'email_to': os.getenv('EMAIL_TO'),
        'email_from': os.getenv('EMAIL_FROM'),
        'email_host': os.getenv('EMAIL_HOST'),
        'email_port': int(os.getenv('EMAIL_PORT', 587)),
        'email_user': os.getenv('EMAIL_USER'),
        'email_pass': os.getenv('EMAIL_PASS')
    }
    if config['cabin_indexes']:
        config['cabin_indexes'] = [int(idx) for idx in config['cabin_indexes'].split(',') if idx.strip().isdigit()]
    else:
        config['cabin_indexes'] = None
    return config


def fetch_pdf(route_code):
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


def send_email_notification(config, subject, body):
    if not all([
        config['email_to'], config['email_from'], config['email_host'],
        config['email_port'], config['email_user'], config['email_pass']
    ]):
        print('Email settings are not fully configured in .env')
        return
    body += '\n\nCheck live cabin availability: https://www.brittany-ferries.co.uk/cabin-availability'
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = config['email_to']
    msg.set_content(body)
    try:
        with smtplib.SMTP(config['email_host'], config['email_port']) as server:
            server.starttls()
            server.login(config['email_user'], config['email_pass'])
            server.send_message(msg)
        print('Notification email sent.')
    except Exception as e:
        print(f'Failed to send email: {str(e)}')


def parse_pdf_for_cabins(pdf_content, sailing_date_time, cabin_indexes, notify_func=None, notify_config=None):
    pdf_file = BytesIO(pdf_content)
    reader = PdfReader(pdf_file)
    found = False
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if sailing_date_time in line:
                parts = line.strip().split()
                try:
                    dt_index = parts.index(sailing_date_time.split()[0])
                    if parts[dt_index + 1] == sailing_date_time.split()[1]:
                        numbers = parts[dt_index + 2:]
                        if not numbers:
                            continue
                        if cabin_indexes is not None:
                            for idx in cabin_indexes:
                                if idx < len(numbers) and numbers[idx].isdigit() and int(numbers[idx]) > 0:
                                    msg = f'Cabin(s) available for {sailing_date_time} at index {idx}: {numbers[idx]}'
                                    print(msg)
                                    if notify_func:
                                        notify_func(notify_config, f'Cabin available for {sailing_date_time}', msg)
                                    found = True
                        else:
                            for idx, num in enumerate(numbers):
                                if num.isdigit() and int(num) > 0:
                                    msg = f'Cabin(s) available for {sailing_date_time} at index {idx}: {num}'
                                    print(msg)
                                    if notify_func:
                                        notify_func(notify_config, f'Cabin available for {sailing_date_time}', msg)
                                    found = True
                except (ValueError, IndexError):
                    continue
    if not found:
        print('No matching cabins available for the specified date and time.')


def main():
    config = load_config()
    if not config['route_code']:
        print('ROUTE_CODE not found in environment variables')
        return
    try:
        pdf_content = fetch_pdf(config['route_code'])
        parse_pdf_for_cabins(
            pdf_content,
            config['sailing_date_time'],
            config['cabin_indexes'],
            notify_func=send_email_notification,
            notify_config=config
        )
    except Exception as e:
        print(f'Error: {str(e)}')


if __name__ == '__main__':
    main() 