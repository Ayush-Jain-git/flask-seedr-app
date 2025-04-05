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


app = Flask(__name__)

CORS(app, origins=["https://peppy-starlight-0d421a.netlify.app"])
SEEDR_USERNAME = os.getenv("SEEDR_USERNAME")
SEEDR_PASSWORD = os.getenv("SEEDR_PASSWORD")

def get_magnet_link(search_query):
    search_url = f"https://www.1337x.to/search/{search_query}/1/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    result_row = soup.select_one(".table-list tbody tr")
    if not result_row:
        print(" No result rows found")
        return None

    name_cell = result_row.select_one("td.name")
    if not name_cell:
        print(" No name cell found")
        return None

    links = name_cell.find_all("a")
    if len(links) < 2:
        print("Torrent link not found")
        return None

    torrent_relative_link = links[1]["href"]
    torrent_page_url = "https://www.1337x.to" + torrent_relative_link
    response = requests.get(torrent_page_url, headers=headers)
    
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
    movie_name = data.get("movie")
    magnet_link = get_magnet_link(movie_name)

    if magnet_link:
        return jsonify({"magnet": magnet_link})
    return jsonify({"error": "No magnet link found"}), 404

def upload_to_seedr(magnet_link):
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
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://www.seedr.cc/")

    try:
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login")))
        login_button.click()
        print("Succesfully login with credentials")
    except:
        print("unsuccesfully credentials")
        pass

    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
    except:
        pass

    try:
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        email_input.send_keys(SEEDR_USERNAME)
        password_input.send_keys(SEEDR_PASSWORD)
        print("Succesfully eneterd the credentials")
    except:
        print("unsuccesfully eneterd the credentials")
        pass

    try:
        popup_login_button = wait.until(EC.element_to_be_clickable((By.ID, "login")))
        popup_login_button.click()
        print("Succesfully clicked on login button")
    except:
        print("unable to click the login button")
        pass

    time.sleep(5)  

    try:
        upload_input = wait.until(EC.visibility_of_element_located((By.NAME, "link")))
        upload_input.clear()
        upload_input.send_keys(magnet_link)
        print("Succesfully copied the magnet link")
    except Exception as e:
        print("Fallback to JS injection due to:", e)
        driver.execute_script("document.querySelector('input[name=\"link\"]').value = arguments[0];", magnet_link)
        print("Succesfully copied the magnet link using JS")

    time.sleep(2)

    try:
        driver.execute_script("document.querySelector('#upload-button').click();")
        print("Succesfully clicked on upload button")
    except:
        print("not able to click on upload button")
        pass

    time.sleep(3)
    driver.quit()
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
