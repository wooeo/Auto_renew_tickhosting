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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    # 添加更多日志选项
    options.add_argument('--enable-logging')
    options.add_argument('--v=1')
    return webdriver.Chrome(options=options)

def add_cookies(driver):
    cookie = {
        "name": "pterodactyl_session",
        "value": SESSION_COOKIE,
        "domain": "tickhosting.com"
    }
    driver.add_cookie(cookie)

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

def wait_and_find_element(driver, by, value, timeout=10, description=""):
    try:
        print(f"Waiting for element: {description} ({value})")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print(f"Found element: {description}")
        return element
    except Exception as e:
        print(f"Failed to find element: {description}")
        print(f"Error: {str(e)}")
        raise

def main():
    driver = None
    try:
        print("Starting browser...")
        driver = setup_driver()
        
        print("Navigating to website...")
        driver.get("https://tickhosting.com")
        add_cookies(driver)
        
        print("Navigating to login page...")
        driver.get("https://tickhosting.com/auth/login")
        time.sleep(5)  # 增加等待时间
        
        print("Navigating to server page...")
        driver.get("https://tickhosting.com/server")
        time.sleep(5)  # 增加等待时间
        
        print("Taking screenshot of current page...")
        driver.save_screenshot('debug_server_page.png')
        
        print("Looking for server card...")
        server_card = wait_and_find_element(
            driver,
            By.XPATH,
            "//div[contains(@class, 'server-card') or contains(@class, 'status-bar')]",
            description="Server Card"
        )
        server_card.click()
        
        print("Looking for renew button...")
        renew_button = wait_and_find_element(
            driver,
            By.XPATH,
            "//button[contains(@class, 'Button___StyledSpan') or contains(text(), 'ADD 96 HOURS')]",
            description="Renew Button"
        )
        
        print("Getting initial expiry time...")
        expiry_element = wait_and_find_element(
            driver,
            By.XPATH,
            "//div[contains(text(), 'EXPIRED:') or contains(text(), 'Free server renew')]",
            description="Expiry Time Element"
        )
        initial_time = expiry_element.text
        print(f"Initial time text: {initial_time}")
        
        print("Clicking renew button...")
        renew_button.click()
        
        print("Waiting 70 seconds for renewal process...")
        time.sleep(70)
        
        print("Taking screenshot after renewal...")
        driver.save_screenshot('debug_after_renewal.png')
        
        print("Checking new expiry time...")
        expiry_element = wait_and_find_element(
            driver,
            By.XPATH,
            "//div[contains(text(), 'EXPIRED:') or contains(text(), 'Free server renew')]",
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
        update_last_renew_time(False, error_message=error_msg)
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        update_last_renew_time(False, error_message=error_msg)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing browser: {str(e)}")

if __name__ == "__main__":
    main()
