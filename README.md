# Brittany Ferries Cabin Availability Notifier

A Python utility to fetch and parse cabin availability PDFs from Brittany Ferries.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and set your route code (e.g. GBPLY_ESSDR)

## Usage

Run the script:
```bash
python main.py
```

The script will:
- Fetch the PDF from Brittany Ferries
- Parse its contents
- Display the first 500 characters of the extracted text

## Environment Variables

- `ROUTE_CODE`: The route code for the ferry crossing (e.g. GBPLY_ESSDR)
- `SAILING_DATE_TIME`: The sailing date and time to look for (e.g. 23/07/25 15:45)
- `CABIN_INDEXES`: Comma-separated indexes of cabin types to trigger on (e.g. 0,1). Leave empty for any cabin.
- Email settings for notifications (see below)

## Email Notification

To enable email notifications, add these to your `.env`:
```
EMAIL_TO=recipient@example.com
EMAIL_FROM=sender@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=your_smtp_username
EMAIL_PASS=your_smtp_password
```

## Docker Usage

You can run this project in Docker for easy deployment (e.g. on a server or with cron):

1. **Build the Docker image:**
   ```bash
   docker build -t brittany-ferries-cabin-notifier .
   ```
2. **Run the container with your .env file:**
   ```bash
   docker run --rm --env-file .env brittany-ferries-cabin-notifier
   ```

## Running on a Schedule (crontab)

To run the script every hour (10 past given brittany ferries update on the hour) using Docker and cron, add this to your crontab:
```
10 * * * * docker run --rm --env-file /path/to/.env brittany-ferries-notifier
```