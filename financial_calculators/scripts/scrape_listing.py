from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import json

def initialize_driver():
    """Initialize Chrome WebDriver with appropriate options"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    return driver

def wait_for_listing_content(driver, max_attempts=3):
    print("Waiting for listing content to load...")

    for attempt in range(max_attempts):
        try:
            print(f"\nAttempt {attempt + 1}: Checking for listing content...")

            # Wait for the main listing container
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "listingPriceValue"))
            )

            return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(3)

    return False

def extract_listing_data(driver):
    """Extract data from the listing page"""
    listing_data = {}

    try:
        # Extract price
        try:
            price_element = driver.find_element(By.ID, "listingPriceValue")
            listing_data['price'] = price_element.text.strip()
            print(f"Price found: {listing_data['price']}")
        except NoSuchElementException:
            print("Could not find price element")

        # Extract bedrooms
        try:
            bedroom_element = driver.find_element(By.ID, "BedroomIcon")
            bedroom_num = bedroom_element.find_element(By.CLASS_NAME, "listingIconNum")
            listing_data['bedrooms'] = bedroom_num.text.strip()
            print(f"Bedrooms found: {listing_data['bedrooms']}")
        except NoSuchElementException:
            print("Could not find bedroom element")

        # Extract bathrooms
        try:
            bathroom_element = driver.find_element(By.ID, "BathroomIcon")
            bathroom_num = bathroom_element.find_element(By.CLASS_NAME, "listingIconNum")
            listing_data['bathrooms'] = bathroom_num.text.strip()
            print(f"Bathrooms found: {listing_data['bathrooms']}")
        except NoSuchElementException:
            print("Could not find bathroom element")

        # Extract square footage
        try:
            sqft_element = driver.find_element(By.ID, "SquareFootageIcon")
            sqft_num = sqft_element.find_element(By.CLASS_NAME, "listingIconNum")
            listing_data['square_feet'] = sqft_num.text.strip()
            print(f"Square footage found: {listing_data['square_feet']}")
        except NoSuchElementException:
            print("Could not find square footage element")

        # Extract description
        try:
            desc_element = driver.find_element(By.ID, "propertyDescriptionCon")
            listing_data['description'] = desc_element.text.strip()
            print(f"Description found: {listing_data['description'][:50]}...")
        except NoSuchElementException:
            print("Could not find description element")

        # Extract property summary
        try:
            summary_element = driver.find_element(By.ID, "PropertySummary")
            summary_items = summary_element.find_elements(By.CLASS_NAME, "propertyDetailsSectionContentSubCon")

            for item in summary_items:
                try:
                    label = item.find_element(By.CLASS_NAME, "propertyDetailsSectionContentLabel")
                    value = item.find_element(By.CLASS_NAME, "propertyDetailsSectionContentValue")
                    key = label.text.strip()
                    listing_data[key] = value.text.strip()
                    print(f"Summary item found: {key}: {listing_data[key]}")
                except NoSuchElementException:
                    continue
        except NoSuchElementException:
            print("Could not find property summary element")

                    # Click Statistics tab and wait for content
        print("\nAttempting to access statistics...")
        try:
            # Find the Statistics tab using a more robust selector
            stats_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'listingDetailsTabsIconCon')]//div[contains(text(), 'Statistics')]"))
            )

            # Scroll the tab into view
            driver.execute_script("arguments[0].scrollIntoView(true);", stats_tab)
            time.sleep(2)

            print("Found Statistics tab, attempting to click...")

            # Try to click using both regular click and JavaScript click
            try:
                stats_tab.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", stats_tab)

            time.sleep(5)  # Increased wait time for statistics to load
            print("Clicked Statistics tab, waiting for content to load...")

            # Wait for stats tab content to load
            print("Waiting for statistics content to load...")
            time.sleep(3)  # Add additional wait time

            # Extract income statistics using XPath
            try:
                print("Looking for income statistics...")
                # Wait for the Average Income text to be present
                income_title = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Average Income')]"))
                )
                print("Found income section")

                # Now find individual income
                individual_row = driver.find_element(By.XPATH,
                    "//div[.//p[contains(text(), 'Individual')]]")
                individual_value = individual_row.find_element(By.XPATH,
                    ".//p[@class='font-normal']")
                listing_data['individual_income'] = individual_value.text.strip()
                print(f"Found individual income: {listing_data['individual_income']}")

                # Find family income
                family_row = driver.find_element(By.XPATH,
                    "//div[.//p[contains(text(), 'Family')]]")
                family_value = family_row.find_element(By.XPATH,
                    ".//p[@class='font-normal']")
                listing_data['family_income'] = family_value.text.strip()
                print(f"Found family income: {listing_data['family_income']}")

            except Exception as e:
                print(f"Error finding income statistics: {str(e)}")
                print("Page source:", driver.page_source)

            # Click Education tab
            print("\nAttempting to access education statistics...")
            # Find the Education tab using a more robust selector
            education_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[.//p[contains(text(), 'Education')]]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", education_tab)
            time.sleep(2)  # Increased wait time

            print("Found Education tab, attempting to click...")

            try:
                education_tab.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", education_tab)

            time.sleep(2)

            # Wait and try to click the Education button
            print("\nLooking for Education tab...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='tablist']"))
                )

                # Find education button using multiple possible selectors
                education_tab = None
                for selector in [
                    "//button[.//p[contains(text(), 'Education')]]",
                    "//button[contains(@id, 'trigger-education')]",
                    "//button[.//div[contains(@aria-label, 'GraduationCap')]]"
                ]:
                    try:
                        education_tab = driver.find_element(By.XPATH, selector)
                        if education_tab:
                            print(f"Found education tab using selector: {selector}")
                            break
                    except:
                        continue

                if education_tab:
                    driver.execute_script("arguments[0].scrollIntoView(true);", education_tab)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", education_tab)
                    print("Clicked Education tab")
                    time.sleep(3)

                    # Extract education statistics
                    education_stats = {}
                    education_rows = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH,
                            "//div[contains(@class, 'grid grid-rows-1')]//p[contains(@class, 'undefined')]/../.."))
                    )

                    for row in education_rows:
                        try:
                            label = row.find_element(By.XPATH, ".//p[contains(@class, 'undefined')]").text.strip()
                            value = row.find_element(By.XPATH, ".//p[@data-align='center']").text.strip()
                            education_stats[label] = value
                            print(f"Found education stat: {label}: {value}")
                        except Exception as e:
                            print(f"Error processing education row: {str(e)}")

                    if education_stats:
                        listing_data['education_statistics'] = education_stats
                else:
                    print("Could not find Education tab")

            except Exception as e:
                print(f"Error with education statistics: {str(e)}")
                print("Page source after error:", driver.page_source)

        except Exception as e:
            print(f"Error accessing statistics tabs: {str(e)}")

        return listing_data

    except Exception as e:
        print(f"Error extracting listing data: {str(e)}")
        return None

def main():
    url = "https://www.realtor.ca/real-estate/27856550/22-adara-alley-winnipeg-aurora-at-north-point"
    driver = initialize_driver()

    try:
        print(f"\nNavigating to URL: {url}")
        driver.get(url)

        # Wait for user to solve CAPTCHA if needed
        input("\nPlease solve any CAPTCHA if present, then press Enter to continue...")

        if not wait_for_listing_content(driver):
            print("Failed to load listing content")
            return

        listing_data = extract_listing_data(driver)

        if listing_data:
            print("\n=== Final Results ===")
            print(json.dumps(listing_data, indent=2))

            # Save results to file
            with open('listing_data.json', 'w') as f:
                json.dump(listing_data, f, indent=2)
            print("\nResults saved to listing_data.json")
        else:
            print("\nFailed to extract listing data")

    except Exception as e:
        print(f"An error occurred in main: {str(e)}")

    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    main()