# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

# Path to your previously saved HTML file
html_file_path = './data/porto_map_without_points_full_folium.html'
output_image_path = './data/porto_map_without_points_full_folium.png'

# Set up Selenium to use a headless Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1500,1000")

# Initialize the browser and load the HTML file
driver = webdriver.Chrome(options=chrome_options)
driver.get(f"file://{os.path.abspath(html_file_path)}")

# Give it a second to ensure the map loads fully
time.sleep(2)

# Save the screenshot
driver.save_screenshot(output_image_path)
print(f"Screenshot saved as {output_image_path}")

# Close the browser
driver.quit()
