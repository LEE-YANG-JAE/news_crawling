import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import datetime

# Specify the path to your WebDriver
service = Service('./chromedriver.exe')

# Initialize the WebDriver using the Service object
driver = webdriver.Chrome(service=service)

# Open the Naver News website
driver.get('https://news.naver.com/')

# List of tabs to click based on the image provided (Korean labels)
tabs = ["경제", "IT/과학", "세계", "정치", "사회", "생활/문화"]

# Get today's date and format it as a string (e.g., "2024-09-20")
today = datetime.datetime.today().strftime('%Y-%m-%d')
year = datetime.datetime.today().strftime('%Y')
month = datetime.datetime.today().strftime('%m')

# Define the base directory depending on the operating system
base_dir = os.path.join('C:\\news', 'headlines')

# Define the directory path where the file will be saved
directory = os.path.join(base_dir, year, month)

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Define the file path
file_path = os.path.join(directory, f'{today}_헤드라인 모음.txt')

# Open the text file in the specified directory with today's date as the file name
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(f"=== {today} 헤드라인 모음 ===\n\n\n")

    # Loop through each tab and click
    for tab in tabs:
        try:
            # Find the tab element by its text and click it
            tab_element = driver.find_element(By.LINK_TEXT, tab)
            tab_element.click()

            # Print the current URL to verify the navigation
            print(f"Clicked on {tab}. Current URL: {driver.current_url}")

            # After clicking the tab, find and click "헤드라인 더보기" (Headline More)
            try:
                more_button = driver.find_element(By.LINK_TEXT, "헤드라인 더보기")
                more_button.click()
                print(f"Clicked on 헤드라인 더보기 in {tab} section.")

                # Wait for the page to load after clicking
                time.sleep(2)

                # Find the section with class "section_component as_section_headline"
                headlines_section = driver.find_element(By.CLASS_NAME, "section_component.as_section_headline")

                # Find all headline titles, press names, summaries, and URLs within this section
                headlines = headlines_section.find_elements(By.CLASS_NAME, "sa_text_strong")
                presses = headlines_section.find_elements(By.CLASS_NAME, "sa_text_press")
                titles = headlines_section.find_elements(By.CLASS_NAME, "sa_text_title")
                summaries = headlines_section.find_elements(By.CLASS_NAME, "sa_text_lede")

                # Write the tab name as a section header in the file
                file.write(f"=== {tab} ===\n")

                # Write out each headline, its corresponding press name, and summary into the file
                for headline, press, title, summary in zip(headlines, presses, titles, summaries):
                    news_url = title.get_attribute('data-imp-url')
                    summary_text = summary.text.strip()

                    # Truncate the summary to 50 characters and add "..." if necessary
                    if len(summary_text) > 50:
                        summary_text = summary_text[:50] + "..."

                    file.write(f"제목: {headline.text}\n내용: {summary_text}\n언론사: {press.text}\n링크: {news_url}\n\n")

                # Add a separator between sections
                file.write("\n" + "=" * 50 + "\n\n")

            except Exception as e:
                print(f"Could not click '헤드라인 더보기' in {tab} section: {e}")
                file.write(f"Could not retrieve data for {tab} section.\n\n")

        except Exception as e:
            print(f"Could not click on {tab}: {e}")
            file.write(f"Could not access {tab} section.\n\n")

# Close the browser
driver.quit()

# Confirm the file has been saved
print(f"File saved at: {file_path}")
