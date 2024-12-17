from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
from dateutil import parser
import os

# 从环境变量获取cookie值
SESSION_COOKIE = os.getenv('PTERODACTYL_SESSION', 'eyJpdiI6InNaVURiZVl1SlIwMEI5c3ZMbUM5ZVE9PSIsInZhbHVlIjoiNVNsInZ')

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    return webdriver.Chrome(options=options)

def add_cookies(driver):
    cookie = {
        "name": "pterodactyl_session",
        "value": SESSION_COOKIE,
        "domain": "tickhosting.com"
    }
    driver.add_cookie(cookie)

def update_last_renew_time(success, new_time=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "成功" if success else "失败"
    content = f"最后续期时间: {current_time}\n状态: {status}"
    if new_time:
        content += f"\n新的到期时间: {new_time}"
    
    with open('last_renew_data.txt', 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    try:
        # Initialize driver
        driver = setup_driver()
        
        # First navigate to the domain to set cookies
        driver.get("https://tickhosting.com")
        add_cookies(driver)
        
        # Navigate to login page
        driver.get("https://tickhosting.com/auth/login")
        time.sleep(3)  # Wait for page load
        
        # Navigate to server management page
        driver.get("https://tickhosting.com/server")
        
        # Wait for and click the status bar
        status_bar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "status-bar"))
        )
        status_bar.click()
        
        # Wait for and click the renew button
        renew_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Button___StyledSpan-sc-1qu1gou-2"))
        )
        
        # Get initial expiry time
        expiry_element = driver.find_element(By.XPATH, "//div[contains(text(), 'EXPIRED:')]")
        initial_time = expiry_element.text.replace("EXPIRED:", "").strip()
        initial_datetime = parser.parse(initial_time)
        
        # Click renew button
        renew_button.click()
        
        # Wait for 70 seconds
        print("Waiting 70 seconds for renewal process...")
        time.sleep(70)
        
        # Check new expiry time
        expiry_element = driver.find_element(By.XPATH, "//div[contains(text(), 'EXPIRED:')]")
        new_time = expiry_element.text.replace("EXPIRED:", "").strip()
        new_datetime = parser.parse(new_time)
        
        if new_datetime > initial_datetime:
            print("Renewal successful! Time has been extended.")
            print(f"New expiry time: {new_time}")
            update_last_renew_time(True, new_time)
        else:
            print("Renewal may have failed. Time was not extended.")
            update_last_renew_time(False)
            
    except TimeoutException as e:
        print(f"Timeout error: {str(e)}")
        update_last_renew_time(False)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        update_last_renew_time(False)
    finally:
        time.sleep(5)  # Wait a bit before closing
        driver.quit()

if __name__ == "__main__":
    main()
