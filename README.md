# **Job Offer Web Scraper**

Simple US Indeed job offer web scraper for an NLP project, we target:
1. Job title.
2. Company name.
3. Location.
4. Salary range.
5. Job type.
6. Job description.

---

To run the script, install the [Anaconda](https://www.anaconda.com/) environment provided in the `environment.yml` file and, from the Anaconda prompt, run:

`python scraper.py url pages_to_scrape csv_file_path`

NOTES: 

1. You might need to adjust the HTML parser depending on your location or wesite language. The scraper provided here is adapted to spanish.
2. The URL must be passed as a string.

---

Code is based on implementation from [this website](https://brightdata.com/blog/how-tos/how-to-scrape-job-postings).

