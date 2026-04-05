# One Piece Colorizer

A simple Python script that downloads the latest One Piece manga chapter pages from a public site (TCB Scans), colorizes them using Google Gemini Image, and exports the result as a PDF.

## Features

- Fetches latest chapter page URLs from `tcbonepiecechapters.com`
- Downloads black-and-white manga pages
- Uses Google Generative AI image API to colorize pages
- Saves raw and colored images locally
- Builds a single `one_piece_latest.pdf` from the colored pages

## Requirements

- Python 3.11+
- A Google Generative AI API key

## Setup

1. Clone the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Google API credentials. Example:

```env
GOOGLE_API_KEY=your_api_key_here
```

> The script uses `python-dotenv` to load environment variables.

## Usage

Run the script from the project root:

```bash
python main.py
```

The script will:

1. Fetch the latest One Piece chapter URL
2. Download each page as a black-and-white image into `raw_bw/`
3. Colorize each page and save it into `colored/`
4. Create `one_piece_latest.pdf`

## Output

- `raw_bw/` — downloaded manga pages
- `colored/` — AI colorized pages
- `one_piece_latest.pdf` — combined PDF of colored pages

## Notes

- This project is intended for personal experimentation.
- Make sure you have valid access to the Google Generative AI image model.
- The script includes a pause between requests to reduce rate limit issues.
