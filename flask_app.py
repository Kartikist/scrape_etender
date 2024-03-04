from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Function to scrape data from the website
def scrape_website(keywords1, keywords2):
    filtered_data = []

    session = requests.Session()
    url = "https://etenders.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"
    response = session.get(url)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the correct table containing organization data
        table = soup.find("table", {"id": "table"})  # Using the ID "table" to target the correct table

        # Iterate through rows in the table
        for row in table.find_all("tr"):
            # Extract data from columns
            columns = row.find_all("td")

            if len(columns) >= 3:
                # Extract organization name
                organization_name = columns[1].text.strip()

                # Check if any of the first keywords match part of the organization name
                if any(keyword.lower() in organization_name.lower() for keyword in keywords1):
                    # Extract page link dynamically
                    page_link = columns[2].find("a")["href"] if columns[2].find("a") else ""

                    # Adjust the link format if necessary
                    if not page_link.startswith("http"):
                        page_link = "https://etenders.gov.in" + page_link

                    # Call function to scrape data from organization's page
                    data = scrape_organization_page(session, organization_name, page_link, keywords2)
                    filtered_data.append({"Organization": organization_name, "Data": data})

    return filtered_data

# Function to scrape data from the organization page
def scrape_organization_page(session, organization_name, link, keywords):
    filtered_data = []

    # Send a request to the organization page using the same session object
    response = session.get(link)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table on the organization page
        table = soup.find("table", {"id": "table"})

        # Check if the table exists
        if table:
            # Iterate through rows in the table
            for row in table.find_all("tr"):
                # Extract data from columns
                columns = row.find_all("td")

                # Check if the row contains data
                if len(columns) >= 5:
                    # Extract the relevant data
                    e_published_date = columns[1].text.strip()
                    closing_date = columns[2].text.strip()
                    opening_date = columns[3].text.strip()
                    title_ref = columns[4].text.strip()
                    title_ref_link = columns[4].find("a")["href"] if columns[4].find("a") else ""
                    organisation_chain = columns[5].text.strip()

                    # Check if any of the second keywords match part of the relevant data
                    if any(keyword.lower() in e_published_date.lower() or \
                           keyword.lower() in closing_date.lower() or \
                           keyword.lower() in opening_date.lower() or \
                           keyword.lower() in title_ref.lower() or \
                           keyword.lower() in organisation_chain.lower() for keyword in keywords):

                        # Prepend the domain name to the title_ref_link
                        if not title_ref_link.startswith("http"):
                            title_ref_link = "https://etenders.gov.in" + title_ref_link

                        # Append the filtered data
                        filtered_data.append({
                            "e_published_date": e_published_date,
                            "closing_date": closing_date,
                            "opening_date": opening_date,
                            "title_ref": title_ref,
                            "title_ref_link": title_ref_link,
                            "organisation_chain": organisation_chain
                        })

    return filtered_data

# Route for the home page
@app.route("/")
def home():
    # Keywords for filtering
    keywords1 = ["ustan", "gail"]  # Keywords for the first page
    keywords2 = ["security", "services", "civil"]  # Keywords for the second page

    # Scrape the website and get filtered data
    filtered_data = scrape_website(keywords1, keywords2)

    # Render the HTML template with filtered data
    return render_template("index.html", filtered_data=filtered_data)

if __name__ == "__main__":
    app.run(debug=True)
