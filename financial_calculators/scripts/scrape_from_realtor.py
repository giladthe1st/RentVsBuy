from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    return driver

def get_listings_with_xpath(driver, xpath):
    try:
        listings = driver.find_elements(By.XPATH, xpath)
        return [listing.get_attribute('href') for listing in listings if listing.get_attribute('href')]
    except:
        return []

def wait_for_listings(driver, max_attempts=3):
    print("Waiting for listings to load...")

    for attempt in range(max_attempts):
        try:
            print(f"\nAttempt {attempt + 1}: Checking for listings...")

            # Wait for the container first
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "listInnerCon"))
            )

            # Try multiple XPath patterns
            xpaths = [
                "//div[contains(@class, 'listingCard')]//a[contains(@class, 'blockLink')]",
                "//ul[@class='listingCardList']//a[contains(@class, 'blockLink')]",
                "/html/body/form/div[5]/div[2]/span/div/div[4]/div[2]/div/div/a"
            ]

            for xpath in xpaths:
                listings = get_listings_with_xpath(driver, xpath)
                if listings:
                    print(f"Found {len(listings)} listings using xpath: {xpath}")
                    return listings

            print("No listings found yet, retrying...")
            time.sleep(3)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(3)

    return []

def get_listings(driver):
    try:
        print("\n=== Starting to get listings ===")

        # Wait for listings with retries
        urls = wait_for_listings(driver)
        if not urls:
            print("Failed to find listings after all attempts")
            return []

        # Print found URLs
        print(f"\nFound {len(urls)} listing elements")
        for idx, url in enumerate(urls, 1):
            print(f"Listing {idx}: {url}")

        return urls

    except Exception as e:
        print(f"Error in get_listings: {str(e)}")
        return []

def click_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "/html/body/form/div[5]/div[2]/span/div/div[4]/div[3]/span/span/div/a[3]"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)

        try:
            next_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", next_button)

        time.sleep(5)
        return True

    except Exception as e:
        print(f"Error clicking next page: {str(e)}")
        return False

def save_listings_to_file(listings, filename="listings.txt"):
    with open(filename, 'w') as f:
        for listing in listings:
            f.write(listing + '\n')
    print(f"\nListings saved to {filename}")

def main():
    num_pages = int(input("How many pages would you like to scrape? "))
    driver = initialize_driver()

    try:
        url = ""
        print(f"\nNavigating to URL: {url}")
        driver.get(url)

        # Wait for user to solve CAPTCHA
        input("\nPlease solve the CAPTCHA if present, then press Enter to continue...")

        all_listings = []
        current_page = 1

        while current_page <= num_pages:
            print(f"\n=== Processing page {current_page}/{num_pages} ===")

            # Get listings from current page
            page_listings = get_listings(driver)
            if page_listings:
                all_listings.extend(page_listings)
                print(f"Added {len(page_listings)} listings from page {current_page}")
                print(f"Running total: {len(all_listings)} listings")
            else:
                print(f"No listings found on page {current_page}")
                retry = input("Would you like to retry this page? (y/n): ")
                if retry.lower() == 'y':
                    continue

            if current_page < num_pages:
                print(f"\nMoving to page {current_page + 1}...")
                if not click_next_page(driver):
                    print("Could not proceed to next page. Stopping...")
                    break

            current_page += 1

        # Save and print results
        print(f"\n=== Final Results ===")
        print(f"Total listings found: {len(all_listings)}")
        save_listings_to_file(all_listings)

    except Exception as e:
        print(f"An error occurred in main: {str(e)}")

    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    main()