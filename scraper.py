import requests
from bs4 import BeautifulSoup

def get_jobs():

    url = "https://remoteok.com/remote-dev-jobs"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    listings = soup.find_all("tr", class_="job")

    for job in listings[:10]:

        title = job.find("h2")

        if title:
            title = title.text.strip()
        else:
            title = "Unknown"

        company = job.find("h3")

        if company:
            company = company.text.strip()
        else:
            company = "Unknown"

        description = title + " " + company

        jobs.append({
            "title": title,
            "company": company,
            "text": description
        })

    return jobs