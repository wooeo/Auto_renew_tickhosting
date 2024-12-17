from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
from dateutil import parser
import os

# 从环境变量获取cookie
SESSION_COOKIE = os.getenv('PTERODACTYL_SESSION', '')

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--enable-logging')
    options.add_argument('--v=1')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    return webdriver.Chrome(options=options)

def add_cookies(driver):
    print("Current cookies before adding:", driver.get_cookies())
    driver.delete_all_cookies()
    cookies = [
        {
            'name': 'PTERODACTYL_SESSION',
            'value': os.environ['PTERODACTYL_SESSION'],
            'domain': '.tickhosting.com'
        },
        {
            'name': 'pterodactyl_session',
            'value': os.environ['PTERODACTYL_SESSION'],
            'domain': '.tickhosting.com'
        }
    ]
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
            print(f"Added cookie: {cookie['name']}")
        except Exception as e:
            print(f"Error adding cookie {cookie['name']}: {str(e)}")
    
    print("Current cookies after adding:", driver.get_cookies())

def try_login(driver):
    try:
        print("\nAttempting to navigate to dashboard...")
        driver.get("https://tickhosting.com")
        time.sleep(5)
        print(f"URL after navigation: {driver.current_url}")
        
        # Check if we're on the dashboard
        if driver.title == "Dashboard":
            print("Successfully reached dashboard")
            return True
            
        print("\nPage title:", driver.title)
        print("\nPage source preview:")
        print(driver.page_source[:2000])
        return False
        
    except Exception as e:
        print(f"Error during login attempt: {str(e)}")
        return False

def wait_and_find_element(driver, by, value, timeout=20, description=""):
    try:
        print(f"Waiting for element: {description} ({value})")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        time.sleep(2)
        print(f"Found element: {description}")
        return element
    except Exception as e:
        print(f"Failed to find element: {description}")
        print(f"Error: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source: {driver.page_source[:1000]}...")
        driver.save_screenshot(f'debug_{description.lower().replace(" ", "_")}.png')
        raise

def update_last_renew_time(success, new_time=None, error_message=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "成功" if success else "失败"
    content = f"最后续期时间: {current_time}\n状态: {status}"
    if new_time:
        content += f"\n新的到期时间: {new_time}"
    if error_message:
        content += f"\n错误信息: {error_message}"
    
    with open('last_renew_data.txt', 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    driver = None
    try:
        print("Starting browser...")
        driver = setup_driver()
        driver.set_page_load_timeout(30)
        
        print("Navigating to website...")
        driver.get("https://tickhosting.com")
        time.sleep(5)
        
        print("Adding cookies...")
        add_cookies(driver)

        print("Refreshing page after adding cookies...")
        driver.refresh()
        time.sleep(5)  # Give more time for the page to load

        print(f"Current URL after refresh: {driver.current_url}")
        print("Taking screenshot of current page state...")
        driver.save_screenshot('debug_after_refresh.png')

        if not try_login(driver):
            raise Exception("Failed to reach dashboard")
        
        print("\nLooking for server elements...")
        selectors = [
            ("xpath", "//div[contains(@class, 'status-indicator')]"),
            ("xpath", "//div[contains(@class, 'status-bar')]"),
            ("xpath", "//div[contains(@class, 'server-status')]"),
            ("xpath", "//div[contains(@class, 'server-power')]"),
            ("xpath", "//div[contains(@class, 'server-info')]"),
            ("css", ".status-indicator"),
            ("css", ".status-bar"),
            ("css", ".server-status")
        ]

        # 先等待页面加载完成
        print("Waiting for page to fully load...")
        time.sleep(10)
        
        print("Taking screenshot before looking for status elements...")
        driver.save_screenshot('debug_before_status.png')
        
        print("Current page title:", driver.title)
        print("Current URL:", driver.current_url)
        
        server_element = None
        for selector_type, selector in selectors:
            try:
                print(f"Trying {selector_type} selector: {selector}")
                if selector_type == "xpath":
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"Found {len(elements)} elements with {selector_type} selector: {selector}")
                    for element in elements:
                        try:
                            print(f"Element text: {element.text}")
                            print(f"Element HTML: {element.get_attribute('outerHTML')}")
                        except:
                            pass
                    server_element = elements[0]
                    break
            except Exception as e:
                print(f"Failed with {selector_type} selector {selector}: {str(e)}")
                continue
        
        if not server_element:
            raise Exception("Could not find server element with any selector")

        print("Clicking server element...")
        driver.execute_script("arguments[0].click();", server_element)
        time.sleep(5)

        print("Taking screenshot before looking for status-bar...")
        driver.save_screenshot('debug_before_status_bar.png')

        print("Looking for status-bar...")
        selectors = [
            ("css", ".status-bar"),
            ("css", ".server-status"),
            ("xpath", "//div[contains(@class, 'status-bar')]"),
            ("xpath", "//div[contains(@class, 'server-card')]//div[contains(@class, 'status-bar')]"),
            ("xpath", "//div[contains(@class, 'container')]//div[contains(@class, 'status-bar')]")
        ]

        status_bar = None
        for selector_type, selector in selectors:
            try:
                status_bar = wait_and_find_element(
                    driver,
                    By.CSS_SELECTOR if selector_type == "css" else By.XPATH,
                    selector,
                    description=f"Status Bar ({selector})"
                )
                print(f"Found status bar with {selector_type} selector: {selector}")
                break
            except Exception as e:
                print(f"Failed with {selector_type} selector {selector}: {str(e)}")
                continue

        if not status_bar:
            raise Exception("Could not find status-bar with any selector")

        print("Taking screenshot before clicking status-bar...")
        driver.save_screenshot('debug_before_click.png')

        print("Clicking status-bar...")
        driver.execute_script("arguments[0].click();", status_bar)
        time.sleep(5)

        print("Taking screenshot of server page...")
        driver.save_screenshot('debug_server_page.png')

        print("Looking for renew button...")
        renew_button = wait_and_find_element(
            driver,
            By.XPATH,
            "//button[contains(text(), 'ADD') or contains(text(), '96 HOURS') or contains(@class, 'Button')]",
            description="Renew Button"
        )

        print("Getting initial expiry time...")
        expiry_element = wait_and_find_element(
            driver,
            By.XPATH,
            "//div[contains(text(), 'EXPIRED:') or contains(text(), 'Free server')]",
            description="Expiry Time Element"
        )
        initial_time = expiry_element.text
        print(f"Initial time text: {initial_time}")

        print("Clicking renew button...")
        driver.execute_script("arguments[0].click();", renew_button)
        time.sleep(2)

        print("Waiting 70 seconds for renewal process...")
        time.sleep(70)

        print("Taking screenshot after renewal...")
        driver.save_screenshot('debug_after_renewal.png')

        print("Checking new expiry time...")
        expiry_element = wait_and_find_element(
            driver,
            By.XPATH,
            "//div[contains(text(), 'EXPIRED:') or contains(text(), 'Free server')]",
            description="New Expiry Time Element"
        )
        new_time = expiry_element.text
        print(f"New time text: {new_time}")

        if "EXPIRED:" in new_time:
            new_time = new_time.replace("EXPIRED:", "").strip()
            initial_time = initial_time.replace("EXPIRED:", "").strip()
            try:
                initial_datetime = parser.parse(initial_time)
                new_datetime = parser.parse(new_time)
                if new_datetime > initial_datetime:
                    print("Renewal successful! Time has been extended.")
                    print(f"New expiry time: {new_time}")
                    update_last_renew_time(True, new_time)
                else:
                    print("Renewal may have failed. Time was not extended.")
                    update_last_renew_time(False, error_message="时间未延长")
            except Exception as e:
                print(f"Error parsing dates: {str(e)}")
                update_last_renew_time(False, error_message=f"日期解析错误: {str(e)}")
        else:
            print("Could not find expiry time in expected format")
            update_last_renew_time(False, error_message="无法找到到期时间")

    except TimeoutException as e:
        error_msg = f"Timeout error: {str(e)}"
        print(error_msg)
        if driver:
            print(f"Current URL: {driver.current_url}")
            driver.save_screenshot('error_timeout.png')
        update_last_renew_time(False, error_message=error_msg)
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        if driver:
            print(f"Current URL: {driver.current_url}")
            driver.save_screenshot('error_general.png')
        update_last_renew_time(False, error_message=error_msg)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing browser: {str(e)}")

if __name__ == "__main__":
    main()
