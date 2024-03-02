# **Job Offer Web Scraper**

Simple US Indeed job offer web scraper for a Natural Language Processing project, we target:
1. Job title.
2. Company name.
3. Location.
4. Salary range.
5. Job type.
6. Job description.

---

To run the script, install the [Anaconda](https://www.anaconda.com/) environment provided in the `environment.yml` file and, from the Anaconda prompt, run:

`conda config --add channels conda-forge`

`conda env create -f environment.yml`

`conda activate scraper_env`

`python scraper.py url pages_to_scrape csv_file_path [discard_non_pay=True]`

NOTES: 

1. You might need to adjust the HTML parser depending on your location or website language. The scraper provided here is adapted to spanish.
2. The URL must be passed as a string.

---

Code is based on implementation from [this website](https://brightdata.com/blog/how-tos/how-to-scrape-job-postings).

