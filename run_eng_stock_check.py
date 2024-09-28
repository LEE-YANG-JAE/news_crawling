import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import datetime
import time


def main():
    if getattr(sys, 'frozen', False):
        # If the script is running as an executable
        # noinspection PyProtectedMember
        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
    else:
        # If the script is running in a development environment
        chromedriver_path = "./chromedriver.exe"

    # Initialize the WebDriver using the Service object
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Store collected data
    news_data = []

    try:
        # Open the web page
        driver.get('https://finviz.com/news.ashx?v=3')

        # Find the div with ID 'news'
        news_div = driver.find_element(By.ID, 'news')

        # Save news items locally to avoid issues with page refresh
        news_items = news_div.find_elements(By.CLASS_NAME, 'news')

        # Processing the news items
        for news_item in news_items:
            try:
                table = news_item.find_element(By.TAG_NAME, 'table')
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                rows = tbody.find_elements(By.TAG_NAME, 'tr')

                # Extract data from each row
                for row in rows:
                    try:
                        news_link_cell = row.find_element(By.CLASS_NAME, 'news_link-cell')
                        news_badges_container = news_link_cell.find_element(By.CLASS_NAME, 'news-badges-container')
                        anchors = news_badges_container.find_elements(By.TAG_NAME, 'a')

                        # Collect stock-news-label data
                        labels = []
                        for anchor in anchors:
                            if 'stock-news-label' in anchor.get_attribute('class'):
                                labels.append(anchor.text.strip())

                        labels_text = ', '.join(labels) if labels else 'No Labels'

                        # Collect title and URL
                        news_url = news_link_cell.find_element(By.CLASS_NAME, 'nn-tab-link').get_attribute('href')
                        news_title = news_link_cell.find_element(By.CLASS_NAME, 'nn-tab-link').text.strip()

                        # Collect press name
                        press_element = news_link_cell.find_element(By.CLASS_NAME, 'news_date-cell')
                        press_name = press_element.text.strip()

                        # Store collected data
                        news_data.append({
                            'title': news_title,
                            'url': news_url,
                            'label': labels_text,
                            'press': press_name,
                            'time': '',
                            'body': ''
                        })

                    except NoSuchElementException:
                        continue
                    except TimeoutException:
                        continue

            except NoSuchElementException:
                continue

    except WebDriverException as e:
        print(f"An error occurred with the WebDriver: {e}")

    # Now iterate over the collected news data to process the URLs
    for data in news_data:
        if 'finance.yahoo.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect time information
                article_time = driver.find_element(By.CLASS_NAME, 'byline-attr-meta-time').text.strip()

                # Collect body text
                article_div = driver.find_element(By.CLASS_NAME, 'article')
                body_wrap_div = article_div.find_element(By.CLASS_NAME, 'body-wrap')
                body_div = body_wrap_div.find_element(By.CLASS_NAME, 'body')

                # Start with the first <p> tag
                paragraphs = body_div.find_elements(By.TAG_NAME, 'p')
                first_p_text = paragraphs[0].text.strip()

                # Check if the first paragraph is a byline or too short
                if first_p_text.startswith('By') or len(first_p_text) < 50:
                    # Move to the second <p> tag if the first one is not suitable
                    first_p_text = paragraphs[1].text.strip()

                # Limit the body text to 300 characters
                if len(first_p_text) > 300:
                    article_body = first_p_text[:300] + "..."
                else:
                    article_body = first_p_text

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = 'Time information not available'
                data['body'] = 'Body text not available'

    # Set up the file path for saving the text file
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    base_dir = os.path.join('C:\\news', 'stock_news')
    directory = os.path.join(base_dir, year, month)
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, f'{today}_Stock_News.txt')

    # Save the collected data to a text file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} Latest Stock News ===\n\n\n")
        for data in news_data:
            file.write(f"Title: {data['title']}\n")
            file.write(f"Stock Label: {data['label']}\n")
            file.write(f"Content: {data['body']}\n")
            file.write(f"Press: {data['press']}\n")
            file.write(f"Date: {data['time']}\n")
            file.write(f"Link: {data['url']}\n\n")
            file.write("=" * 50 + "\n\n")

    print(f"News data has been saved at: {file_path}")

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()
