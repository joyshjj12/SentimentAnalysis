import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
def extract_reviews_from_page(soup):
    reviews = []
    review_containers = soup.select('.review')
    for container in review_containers:
        review_text = container.select_one('.review-text').get_text(strip=True)
        rating = container.select_one('.review-rating').get_text(strip=True)
        date_element = container.select_one('.review-date')
        date = date_element.get_text(strip=True) if date_element else None
        reviews.append({
            'text': review_text,
            'rating': rating,
            'date': date
        })
    return reviews

url = "https://www.amazon.com/Intel-i3-8100-Desktop-Processor-Unlocked/dp/B0759FTRZL/ref=sr_1_9?dib=eyJ2IjoiMSJ9.v_70CLXFwbUM1sgaVP-O4CZFyB1WElwx0ov_AcswMVjT844h0oyOqR1Vbrm1e9zMRbMctNSGFsTGrCBtexP96qvOi6DHK6fRi223Qr61VFXLQYuqUuTxybD7iCnIng_3nXEo1luus5xEAF5fe1ahvwQdHRdESJt8M_WiPY8vY4rEKj4dYm5CfyCJvr0ni4_573r8ofFsKDN0qWktLimNSuERx7zbArp-AgdKE4QwtPE.lFVrTgrukkj7Guj_jka0NYCP-mcUlVxN-kyZH4VzvJo&dib_tag=se&keywords=intel%2Bi3&qid=1716563860&sr=8-9&th=1"
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the URL with Selenium
setup_driver()

# Proceed with scraping as before
try:
    driver.get(url)
    
    # Check if a CAPTCHA is present
    if 'captcha' in driver.page_source.lower():
        # Handle CAPTCHA
        print("CAPTCHA detected. Exiting.")
        driver.quit()
        exit()

    time.sleep(2)  # Ensure page is fully loaded

    # Extract reviews from multiple pages
    reviews_data = []
    while len(reviews_data) < 50:
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract reviews from the current page
        reviews_on_page = extract_reviews_from_page(soup)
        print(f"Extracted {len(reviews_on_page)} reviews from this page")
        
        if not reviews_on_page:
            print("No reviews found on this page. Exiting.")
            break

        reviews_data.extend(reviews_on_page)

        # Check if we have enough reviews
        if len(reviews_data) >= 50:
            break

        # Try to go to the next page of reviews
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.a-last a'))
            )
            next_button.click()
            time.sleep(2)  # Wait for the next page to load
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException) as e:
            print(f"Error clicking 'Next' button or no more pages: {e}")
            break
    
    # Print the extracted review data
    for review in reviews_data:
        print(review)

    # Save the output to a text file
    with open("reviews_intel_i3_8100F.txt", "w", encoding="utf-8") as file:
        for review in reviews_data:
            file.write(str(review) + "\n")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the Selenium WebDriver
    driver.quit()
