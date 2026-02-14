import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, WebDriverException)
import datetime
import time


def main():
    driver = webdriver.Chrome()

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
    headline_file_path = os.path.join(directory, f'{today}_헤드라인_모음.txt')

    # Store collected headline data and section names for the index
    headline_data = []
    section_names = []

    # Headline Crawling
    try:
        # Open the Naver News website
        driver.get('https://news.naver.com/')

        # List of tabs to click based on the image provided (Korean labels)
        tabs = ["경제", "IT/과학", "세계", "정치", "사회", "생활/문화"]

        with open(headline_file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} 헤드라인 모음 ===\n\n\n")

            for tab in tabs:
                try:
                    # Find the tab element by its text and click it
                    tab_element = driver.find_element(By.LINK_TEXT, tab)
                    tab_element.click()

                    # Wait for the page to load (adjust time if necessary)
                    time.sleep(2)

                    # Add the section name to the section_names list for the index
                    section_names.append(tab)

                    try:
                        # Attempt to find and click "헤드라인 더보기" (Headline More) button
                        more_button = driver.find_element(By.LINK_TEXT, "헤드라인 더보기")
                        more_button.click()

                        # Wait for the page to load after clicking
                        time.sleep(2)

                    except NoSuchElementException:
                        # If the "헤드라인 더보기" button is not found, continue without clicking
                        pass

                    # Find the section with class "section_component as_section_headline"
                    headlines_section = driver.find_element(By.CLASS_NAME, "section_component.as_section_headline")

                    # Find all headline titles, press names, summaries, and URLs within this section
                    headlines = headlines_section.find_elements(By.CLASS_NAME, "sa_text_strong")
                    presses = headlines_section.find_elements(By.CLASS_NAME, "sa_text_press")
                    titles = headlines_section.find_elements(By.CLASS_NAME, "sa_text_title")
                    summaries = headlines_section.find_elements(By.CLASS_NAME, "sa_text_lede")

                    for headline, press, title, summary in zip(headlines, presses, titles, summaries):
                        news_url = title.get_attribute('data-imp-url')
                        summary_text = summary.text.strip()

                        # Truncate the summary to 50 characters and add "..." if necessary
                        if len(summary_text) > 70:
                            summary_text = summary_text[:70] + "..."

                        # Store the collected data
                        headline_data.append({
                            "tab": tab,
                            "headline": headline.text,
                            "press": press.text,
                            "summary": summary_text,
                            "url": news_url
                        })

                except NoSuchElementException:
                    file.write(f"Could not access {tab} section.\n\n")

            # Write the index to the file
            file.write("목차:\n")
            for idx, section_name in enumerate(section_names, 1):
                file.write(f"{idx}. === {section_name} ===\n")
            file.write("\n\n")

            # Process each collected headline URL to extract additional information
            current_tab = None
            for data in headline_data:
                if current_tab != data['tab']:
                    current_tab = data['tab']
                    file.write(f"=== {current_tab} ===\n\n")

                try:
                    # Navigate to the headline URL to get the publication date
                    driver.get(data["url"])

                    # Wait for the article page to load and find the published date
                    date_elements = driver.find_elements(By.CLASS_NAME, "media_end_head_info_datestamp_time")
                    if len(date_elements) == 2:
                        published_date = date_elements[0].text.strip()
                        modified_date = driver.find_element(By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME").text.strip()
                    else:
                        published_date = date_elements[0].text.strip()
                        modified_date = None

                    # Write the details to the file
                    file.write(f"제목: {data['headline']}\n내용: {data['summary']}\n언론사: {data['press']}\n")
                    file.write(f"작성일: {published_date}\n")
                    if modified_date:
                        file.write(f"수정일: {modified_date}\n")
                    file.write(f"링크: {data['url']}\n\n")
                    file.write("=" * 50 + "\n\n")

                except NoSuchElementException:
                    file.write(f"Could not retrieve details for URL: {data['url']}\n\n")
                except TimeoutException:
                    file.write(f"Timeout occurred while retrieving details for URL: {data['url']}\n\n")

    except WebDriverException as e:
        print(f"An error occurred with the WebDriver: {e}")

    # Close the browser
    driver.quit()

    # Confirm the file has been saved
    if headline_file_path:
        print(f"Headline file saved at: {headline_file_path}")


if __name__ == "__main__":
    main()
