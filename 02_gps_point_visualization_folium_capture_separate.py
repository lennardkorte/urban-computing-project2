from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

# Define file paths for HTML files and output directory for images
html_dir = './data/separate_html/'
output_image_dir = './data/trip_screenshots/'

# Ensure output directory exists
os.makedirs(output_image_dir, exist_ok=True)

# Set up Selenium to use a headless Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1500,1000")

# Initialize the browser
driver = webdriver.Chrome(options=chrome_options)

# Loop through each HTML file and take a screenshot
for file_name in os.listdir(html_dir):
    if file_name.endswith('.html') and file_name.startswith('porto_trip_'):
        # Full path to the HTML file and corresponding output image path
        html_file_path = os.path.join(html_dir, file_name)
        trip_id = file_name.split('_')[-1].replace('.html', '')
        output_image_path = os.path.join(output_image_dir, f'porto_trip_{trip_id}.png')

        # Load the HTML file in the browser
        driver.get(f"file://{os.path.abspath(html_file_path)}")

        # Inject CSS to force a specific color (e.g., blue) for trip elements
        driver.execute_script("""
            let style = document.createElement('style');
            style.innerHTML = `
                /* Replace '.trip-element' with the actual class used in the HTML */
                .trip-element {
                    color: #007bff !important; /* Blue color */
                    background-color: #e7f3ff !important; /* Light blue background */
                }
            `;
            document.head.appendChild(style);
        """)

        # Pause to ensure the map loads fully
        time.sleep(2)

        # Save the screenshot
        driver.save_screenshot(output_image_path)
        print(f"Screenshot saved as {output_image_path}")

# Close the browser
driver.quit()
