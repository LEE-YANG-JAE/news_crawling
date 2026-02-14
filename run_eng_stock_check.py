import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import datetime
import time


def main():
    driver = webdriver.Chrome()

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
                rows = tbody.find_elements(By.TAG_NAME, 'tr')[:30]  # Limit to 30 rows

                # Extract data from each row
                for row in rows:
                    try:
                        news_link_cell = row.find_element(By.CLASS_NAME, 'news_link-cell')
                        news_badges_container = news_link_cell.find_element(By.CLASS_NAME, 'news-badges-container')
                        anchors = news_badges_container.find_elements(By.TAG_NAME, 'a')

                        # Collect data
                        if len(anchors) > 0:
                            news_url = anchors[0].get_attribute('href')
                            news_title = anchors[0].text.strip()
                            stock_labels = [label.text.strip() for label in news_badges_container.find_elements(By.CLASS_NAME, 'stock-news-label')]

                            # Collect press name
                            press_element = news_link_cell.find_element(By.CLASS_NAME, 'news_date-cell')
                            press_name = press_element.text.strip()

                            # Store collected data
                            news_data.append({
                                'title': news_title,
                                'url': news_url,
                                'labels': stock_labels,
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
                article_body = first_p_text[:300] + "..." if len(first_p_text) > 300 else first_p_text

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = ''
                data['body'] = 'Body text not available'

        elif 'www.prnewswire.co.uk' in data['url'] or 'www.prnewswire.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect time information
                article_time = driver.find_element(By.CLASS_NAME, 'mb-no').text.strip()

                # Collect body text
                article_body_div = driver.find_element(By.CLASS_NAME, 'release-body')
                row_div = article_body_div.find_element(By.CLASS_NAME, 'row')
                first_p_text = row_div.find_element(By.TAG_NAME, 'p').text.strip()

                # Limit the body text to 300 characters
                article_body = first_p_text[:300] + "..." if len(first_p_text) > 300 else first_p_text

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = ''
                data['body'] = 'Body text not available'

        elif 'www.businesswire.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect body text
                subhead_div = driver.find_element(By.CLASS_NAME, 'bw-release-story')
                first_p = subhead_div.find_element(By.CLASS_NAME, 'bwalignc').text.strip()

                # Limit the body text to 300 characters
                article_body = first_p[:300] + "..." if len(first_p) > 300 else first_p

                # Update data
                data['body'] = article_body

            except NoSuchElementException:
                data['body'] = 'Body text not available'

        elif 'www.globenewswire.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect time information
                article_time = driver.find_element(By.CLASS_NAME, 'article-published-source').text.strip()

                # Collect body text
                article_body_div = driver.find_element(By.CLASS_NAME, 'article-body')
                first_p_text = article_body_div.find_element(By.TAG_NAME, 'p').text.strip()

                # Limit the body text to 300 characters
                article_body = first_p_text[:300] + "..." if len(first_p_text) > 300 else first_p_text

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = ''
                data['body'] = 'Body text not available'

        elif 'www.investopedia.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect time information
                article_time = driver.find_element(By.CLASS_NAME, 'mntl-attribution__item-date').text.strip()

                # Collect body text
                article_body_div = driver.find_element(By.CLASS_NAME, 'article-body-content')
                paragraphs = article_body_div.find_elements(By.CLASS_NAME, 'finance-sc-block-html')

                # Extract text from the paragraphs and concatenate
                article_body = ' '.join([p.text.strip() for p in paragraphs])

                # Limit the body text to 300 characters
                article_body = article_body[:300] + "..." if len(article_body) > 300 else article_body

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = ''
                data['body'] = 'Body text not available'

        elif 'www.newsfilecorp.com' in data['url']:
            driver.get(data['url'])
            time.sleep(1)  # Pause for 1 second

            try:
                # Collect time information
                article_time = driver.find_element(By.ID, 'release').text.strip()

                # Collect body text
                paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                article_body = ' '.join([p.text.strip() for p in paragraphs if not p.get_attribute('style')])

                # Limit the body text to 300 characters
                article_body = article_body[:300] + "..." if len(article_body) > 300 else article_body

                # Update data
                data['time'] = article_time
                data['body'] = article_body

            except NoSuchElementException:
                data['time'] = ''
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
        file.write(f"=== {today} Latest 30 Stock News ===\n\n\n")
        for data in news_data:
            file.write(f"Title: {data['title']}\n")
            file.write(f"Press: {data['press']}\n")
            file.write(f"Labels: {', '.join(data['labels'])}\n")
            file.write(f"Date: {data['time']}\n")
            file.write(f"Content: {data['body']}\n")
            file.write(f"Link: {data['url']}\n\n")
            file.write("=" * 50 + "\n\n")

    print(f"News data has been saved at: {file_path}")

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()
