from bs4 import BeautifulSoup
import requests

# Function to scrape data from the website
def scrape_website(keywords1, keywords2):
    # Create a new session object
    session = requests.Session()
    
    # Send a request to the website
    url = "https://etenders.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"
    response = session.get(url)
    
    # Check if the request was successful
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
                    scrape_organization_page(session, organization_name, page_link, keywords2)

# Function to scrape data from the organization page
def scrape_organization_page(session, organization_name, link, keywords):
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
            # Print header with organization name
            print(f"Organization: {organization_name}")
            print("Filtered Data:")
            
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
                        
                        # Print the filtered data
                        print(f"e-Published Date: {e_published_date} | Closing Date: {closing_date} | Opening Date: {opening_date} | Title/Ref.No./Tender ID: {title_ref} | Title/Ref.No./Tender ID Link: {title_ref_link} | Organisation Chain: {organisation_chain}")



# Call the function to scrape the website with multiple keywords for both pages
keywords1 = ["ustan", "gail"]  # Keywords for the first page
keywords2 = ["security", "services", "civil"]  # Keywords for the second page
scrape_website(keywords1, keywords2)

