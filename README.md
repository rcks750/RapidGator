# RapidGator

RapidGator downloader for Google Colab with live progress.

## Files
- `rapidgator_for_colab.ipynb` — Colab notebook with form inputs for email, password, link, and output directory.
- `rgcolab.py` — Python downloader with live progress, destination path output, and safe filename handling.
- `README.md` — Repository overview and usage notes.

## Requirements
- A Rapidgator account.
- Google Colab or Python 3.
- Python packages: `requests` and `lxml`.

## Open in Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rcks750/RapidGator/blob/main/rapidgator_for_colab.ipynb)

## Colab usage
1. Open the notebook from your GitHub repo.
2. Enter your Rapidgator email, password, and file URL.
3. Run the cell.
4. The file will download into the selected output folder and show live status in the cell.

## Local usage
```bash
python rgcolab.py "your_email" "your_password" "https://rapidgator.net/file/..." "./downloads"
```
