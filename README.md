# LinkedIn Profile Scraper, Autodialer, and Article Generator

This repository contains three assignments implemented using Streamlit:

1. LinkedIn profile scraping using Apify
2. Autodialing via Twilio
3. Article generation using Gemini

A Streamlit interface is used to run each module.

---

## Streamlit Application

* LinkedIn Scrapper:
`https://linkedin-profile-data-scrapper.streamlit.app/`
* AI-BLog Generator: `https://article-generation-ai.streamlit.app/`

---

## Features

### LinkedIn Profile Scraper

* Uses Apify LinkedIn actor
* Accepts profile URLs as input
* Displays scraped results in tabular format
* Supports CSV export

### Autodialer

* Accepts up to 100 phone numbers
* Sequentially calls numbers using Twilio
* Allows text-based input such as: “make a call to X”
* Maintains call logs
* Works with Twilio trial restrictions (only verified numbers)

### Article Generator

* Uses Gemini API to generate technical content
* Accepts topics and optional descriptions
* Produces structured Markdown output
* Supports CSV export

---

## Tech Stack

* Python
* Streamlit
* Apify API
* Twilio Voice API
* Google Gemini API

---

## Setup

1. Clone the repository
   `git clone LinkedIn_Profile_Data_Scrapper-Artical-generation`

2. Install dependencies
   `pip install -r requirements.txt`

3. Create a `.env` file with the following variables:

```
APIFY_TOKEN=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_NUMBER=...
GEMINI_API_KEY=...
```

You may alternatively configure these in Streamlit Cloud Secrets.

---

## Running the Application

Run the main Streamlit entry point:
`streamlit run app.py`

If each module is in a separate directory, run the corresponding `app.py`.

---

## Repository Structure

This repository does not follow a strict folder structure.
Each module contains:

* `app.py`
* `function.py`

Example modules:

* LinkedIn scraper
* Autodialer
* Article generator

---

## Notes

* LinkedIn scraping is performed via Apify. Private or limited profiles may not return data.
* Twilio trial accounts only allow calls to verified phone numbers.
* Article quality and structure depend on Gemini model responses.

---

## License

This project is for educational and demonstration purposes only. Use responsibly and comply with all platform terms.
