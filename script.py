import os
import random
import time
import logging
import pyautogui
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
COLLECTION_NAME = os.getenv("COLLECTION")
MAIN_DIR = os.getenv("MAIN_DIR")
NUM_PHOTOS = int(os.getenv("NUMBER_OF_PHOTOS"))

# Set up logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_directory = "logs"
timestamp = datetime.now().strftime("%Y%m%d_%H:%M")
log_file_path = os.path.join(log_directory, f"upload_{timestamp}.log")
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format=log_format,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Also log to stdout
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(log_format)
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Initialize WebDriver in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)

logging.info("=======================================")
logging.info("Starting upload process.")


# Open the digital frame website
driver.get("https://www.bluecanvas.com/Home")

# Wait for the login elements to load and input credentials
try:
    login_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
    )
    login_link.click()

    # Wait for the login popup to appear
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "loginEmail"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )

    # Enter your login details
    username.send_keys(LOGIN_EMAIL)
    password.send_keys(LOGIN_PASSWORD)

    # Submit the form
    login_button = driver.find_element(By.CLASS_NAME, "login_btn")
    login_button.click()

    # Wait for the login process to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mypage_order"))
    )
    logging.info("Login successful")

    # Click on the 'Content Management' button
    content_management_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Content Management"))
    )
    content_management_button.click()

    # Click on the collection box '기본컬렉션'
    collection_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//p[contains(@class, 'tit') and contains(text(), '{COLLECTION_NAME}')]/ancestor::div[@class='txtArea']/preceding-sibling::a",
            )
        )
    )
    collection_box.click()

    logging.info("Navigation to collection successful")

    # Delete content

    delete_content_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Delete content"))
    )
    delete_content_button.click()

    delete_all_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Delete all"))
    )
    delete_all_button.click()

    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert.accept()

    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert.accept()

    logging.info(f"Deleted all content.")

    cancel_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Cancel"))
    )
    cancel_button.click()

    album_dirs = [
        os.path.join(MAIN_DIR, d)
        for d in os.listdir(MAIN_DIR)
        if os.path.isdir(os.path.join(MAIN_DIR, d))
    ]

    # Function to pick random album and random percentage
    def pick_random_album_and_percentage() -> tuple[str, int]:
        random_album = random.choice(album_dirs)
        album_dirs.remove(random_album)
        percentage = random.randint(40, 100)
        return random_album, percentage

    # Function to get a random subset of photos from an album
    def get_random_photos(album, percentage):
        photos = [
            os.path.join(album, f)
            for f in os.listdir(album)
            if os.path.isfile(os.path.join(album, f))
        ]
        num_photos_to_upload = max(1, len(photos) * percentage // 100)
        return random.sample(photos, num_photos_to_upload)

    # Function to split a list into chunks of sublists
    def split_list_into_chunks(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # Total number of photos to upload
    total_photos_to_upload = NUM_PHOTOS
    uploaded_photos_count = 0

    # Loop until the total number of uploaded photos reaches the specified limit
    while album_dirs and uploaded_photos_count < total_photos_to_upload:

        # Pick a random album and percentage
        random_album, percentage = pick_random_album_and_percentage()

        logging.info("---------------------------------------")
        album_name = random_album.split("/")[-1]
        logging.info(f"Selected album: {album_name}, Percentage: {percentage}%")

        # Get random photos from the album based on the selected percentage
        file_paths = get_random_photos(random_album, percentage)
        logging.info(f"Selected {len(file_paths)} photos.")

        # Split file_paths into chunks of 30
        sublists = list(split_list_into_chunks(file_paths, 5))

        # Loop through each file and upload one by one
        sublist_index = 1
        sublist_size = len(sublists)
        for sublist in sublists:

            # Upload photos
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "+ UPLOAD"))
            )
            upload_button.click()

            for file_path in sublist:

                manual_upload_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "li.plus.file_upload7[onclick='fnFileFormAdd()']",
                        )
                    )
                )
                manual_upload_button.click()

                # Wait for the hidden file input element to be present
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "form#uploadContentsFileForm input[type='file']",
                        )
                    )
                )

                # Use send_keys to upload the file
                file_input.send_keys(file_path)
                pyautogui.press("esc")

            # Click the 'Confirm' button to complete the upload
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Confirm"))
            )
            confirm_button.click()

            # Wait until upload completes
            loading_spinner = WebDriverWait(driver, 600).until(
                EC.invisibility_of_element_located((By.ID, "spinLoading"))
            )
            logging.debug(f"Uploaded sublist ({sublist_index}/{sublist_size}).")
            sublist_index += 1

        uploaded_photos_count += len(file_paths)
        logging.info("Total uploaded count: " + str(uploaded_photos_count))

    logging.info("=======================================")
    logging.info("Photos upload completed successfully.")


except Exception as e:
    logging.error("An error occurred:", e)

finally:
    # Close the browser after a delay (for testing purposes)
    time.sleep(3)
    driver.quit()
