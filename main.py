from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
import os

patterns = [
    # Standard patterns
    r'Earn\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'earn\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards®?\s*Points',
    # Points back patterns
    r'up\s+to\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards®?\s*points?\s+back',
    # Welcome bonus patterns
    r'welcome\s+bonus\s+of\s+(\d{2,3}(?:,\d{3})*)',
    r'Welcome\s+Offer:\s*(\d{2,3}(?:,\d{3})*)',
    # HTML specific patterns
    r'header--[^"]*">.*?(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'class="[^"]*">.*?(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
]

def test_patterns_on_file():
    print("\n--- Testing patterns on debug_page.html ---")
    try:
        with open('debug_page.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        
        offers = []
        for pattern in patterns:
            print(f"\nTrying pattern: {pattern}")
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    if not match:
                        continue
                    full_text = match.group(0)
                    if not full_text:
                        continue
                    value_str = match.group(1)
                    if not value_str:
                        continue
                        
                    print(f"Found text: '{full_text}'")
                    print(f"Extracted value: '{value_str}'")
                    
                    clean_value = re.sub(r'[^\d,]', '', value_str)
                    if not clean_value:
                        continue
                    value = float(clean_value.replace(',', ''))
                    
                    if value >= 10000:
                        offers.append(value)
                        print(f"Added offer: {value:,.0f} points")
                except (ValueError, AttributeError, IndexError) as e:
                    print(f"Error processing match: {e}")
                    continue
        
        if offers:
            print("\nAll found offers:", [int(x) for x in offers])
            print(f"Highest offer: {max(offers):,.0f} points")
        else:
            print("\nNo offers found in debug file!")
            # Print a sample of the content for debugging
            print("\nContent sample:")
            print(content[:500])
            
    except FileNotFoundError:
        print("debug_page.html not found!")
    except Exception as e:
        print(f"Error testing patterns: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

def play_alert():
    # Simple console bell sound
    print('\a')
    # Print visible alert
    print("\n" + "!" * 50)
    print("HIGH OFFER FOUND!")
    print("!" * 50 + "\n")

def check_for_offer():
    chrome_options = Options()
    chrome_options.add_argument("--start-minimized")  # Start Chrome minimized
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Minimize the window immediately after opening
        driver.minimize_window()
        
        while True:
            try:
                print("\n--- Starting new check ---")
                driver.get("https://www.americanexpress.com/us/credit-cards/business/business-credit-cards/american-express-business-gold-card-amex")
                
                print("Waiting for page load...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Scroll to load dynamic content
                print("Scrolling page...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(5)
                
                page_content = driver.page_source
                if not page_content:
                    raise ValueError("Empty page content")
                
                offers = []
                for pattern in patterns:
                    matches = re.finditer(pattern, page_content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        try:
                            if not match:
                                continue
                            full_text = match.group(0)
                            if not full_text:
                                continue
                            value_str = match.group(1)
                            if not value_str:
                                continue
                                
                            clean_value = re.sub(r'[^\d,]', '', value_str)
                            if not clean_value:
                                continue
                            value = float(clean_value.replace(',', ''))
                            
                            if value >= 10000:
                                offers.append(value)
                                print(f"Found offer: {value:,.0f} points")
                        except (ValueError, AttributeError, IndexError) as e:
                            continue
                
                if not offers:
                    print("\nNo point offers found. Retrying...")
                    driver.quit()
                    driver = webdriver.Chrome(options=chrome_options)
                    continue
                
                max_offer = max(offers)
                print(f"\nFound offers: {[int(x) for x in offers]}")
                print(f"Current highest offer: {max_offer:,.0f} points")
                
                if max_offer >= 200000:
                    print("Found 200k offer! Keeping browser open and freezing.")
                    print("URL:", driver.current_url)
                    input("Press Enter to close the browser and end the script...")
                    driver.quit()
                    break
                elif max_offer >= 100000:
                    print(f"Found {int(max_offer):,} offer. Continuing to check for higher offers...")
                    driver.quit()
                    driver = webdriver.Chrome(options=chrome_options)
                else:
                    print("Offer below 100k found. Retrying...")
                    driver.quit()
                    time.sleep(30)
                    driver = webdriver.Chrome(options=chrome_options)
                
            except Exception as e:
                print(f"\nError processing page: {e}")
                print(f"Error type: {type(e)}")
                print(f"Error details: {str(e)}")
                if 'driver' in locals():
                    driver.quit()
                time.sleep(30)
                driver = webdriver.Chrome(options=chrome_options)
            
    except KeyboardInterrupt:
        print("\nStopping the checker...")
        if 'driver' in locals():
            driver.quit()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    # Run the test first
    test_patterns_on_file()
    
    # Ask whether to continue with live checking
    response = input("\nContinue with live checking? (y/n): ")
    if response.lower() == 'y':
        check_for_offer()