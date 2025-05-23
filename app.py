from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import threading
import psutil


app = Flask(__name__)

CORS(app, origins=["https://peppy-starlight-0d421a.netlify.app"])
SEEDR_USERNAME = os.getenv("SEEDR_USERNAME")
SEEDR_PASSWORD = os.getenv("SEEDR_PASSWORD")

def get_magnet_link(search_query):
    url = f"https://tpirbay.top/search/{search_query.replace(' ', '%20')}/1/99/0"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    magnet_link = soup.select_one("a[href^='magnet:']")

    return magnet_link["href"] if magnet_link else None

@app.route("/")
def home():
    return "Flask backend is running!"
    
@app.route("/get-magnet", methods=["POST"])
def get_magnet():
    data = request.json
    movie_name = data.get("query")
    magnet_link = get_magnet_link(movie_name)

    if magnet_link:
        return jsonify({"magnet": magnet_link})
    return jsonify({"error": "No magnet link found"}), 404

def upload_to_seedr(magnet_link):

    print("Starting Seedr upload process...")

    # Memory usage before Chrome opens
    print("Memory usage before Chrome (MB):", psutil.virtual_memory().used / 1024 / 1024)
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-accelerated-2d-canvas")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.binary_location = "/usr/bin/google-chrome" 
    service = Service("/usr/bin/chromedriver")
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://www.seedr.cc/")

        try:
            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login")))
            login_button.click()
            print("Clicked login button")
        except Exception as e:
            print("Login button click failed:", e)

        try:
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
        except Exception:
            print("Iframe not found, skipping switch.")

        try:
            email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            email_input.send_keys(SEEDR_USERNAME)
            password_input.send_keys(SEEDR_PASSWORD)
            print("Entered credentials")
        except Exception as e:
            print("Credential input failed:", e)

        try:
            popup_login_button = wait.until(EC.element_to_be_clickable((By.ID, "login")))
            popup_login_button.click()
            print("Clicked login")
        except Exception as e:
            print("Login button click error:", e)

        time.sleep(5)

        try:
            upload_input = wait.until(EC.visibility_of_element_located((By.NAME, "link")))
            upload_input.clear()
            upload_input.send_keys(magnet_link)
            print("Magnet link input success")
        except Exception as e:
            print("Standard input failed. Falling back to JS injection:", e)
            try:
                driver.execute_script(
                    "document.querySelector('input[name=\"link\"]').value = arguments[0];", 
                    magnet_link
                )
                print("Magnet link set via JS")
            except Exception as js_err:
                print("JS injection failed:", js_err)

        time.sleep(2)

        try:
            driver.execute_script("document.querySelector('#upload-button').click();")
            print("Upload button clicked via JS")
        except Exception as e:
            print("Upload button click failed:", e)

        time.sleep(3)

    except Exception as main_err:
        print("Unexpected error in upload_to_seedr:", main_err)

    finally:
        if driver:
            try:
                driver.quit()
                print("Driver closed successfully.")
            except Exception as quit_err:
                print("Error during driver.quit():", quit_err)

        # Memory usage after Chrome closes
        print("Memory usage after Chrome (MB):", psutil.virtual_memory().used / 1024 / 1024)

    return "Uploaded Successfully"



@app.route("/upload-to-seedr", methods=["POST"])
def upload_magnet():
    data = request.json
    magnet_link = data.get("magnet")
    if not magnet_link:
        return jsonify({"error": "Magnet link is required"}), 400
    
    def background_upload():
        result = upload_to_seedr(magnet_link)
        print("Background upload finished:", result)

    threading.Thread(target=background_upload).start()
    return jsonify({"message": "Upload started in background."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
