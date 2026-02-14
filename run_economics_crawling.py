import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, WebDriverException,
                                        StaleElementReferenceException)
import datetime
import time
from difflib import SequenceMatcher


def are_similar(str1, str2, threshold=0.8):
    return SequenceMatcher(None, str1, str2).ratio() > threshold


def main():
    driver = webdriver.Chrome()

    # Get today's date and format it as a string (e.g., "2024-09-28")
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    # Define the base directory depending on the operating system
    base_dir = os.path.join('C:\\news', 'economics')

    # Define the directory path where the file will be saved
    directory = os.path.join(base_dir, year, month)

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Define the file path
    economics_file_path = os.path.join(directory, f'{today}_경제_영역별_뉴스_모음.txt')

    # Store collected section and article data
    all_section_data = []
    all_article_data = []

    # Economics Crawling
    try:
        # Open the Naver News website and go to the "경제" section
        driver.get('https://news.naver.com/')

        # Select only the "경제" tab
        tab = "경제"

        try:
            # Find the tab element by its text and click it
            tab_element = driver.find_element(By.LINK_TEXT, tab)
            tab_element.click()

            # Wait for the page to load (adjust time if necessary)
            time.sleep(2)

            # Find the 'ct_snb_nav' class which contains the subsections
            nav_section = driver.find_element(By.CLASS_NAME, "ct_snb_nav")

            # Find all 'ct_snb_nav_item' within 'ct_snb_nav'
            nav_items = nav_section.find_elements(By.CLASS_NAME, "ct_snb_nav_item")

            # Collect the text and href of each 'ct_snb_nav_item_link'
            for item in nav_items:
                try:
                    link_element = item.find_element(By.CLASS_NAME, "ct_snb_nav_item_link")
                    subsection_text = link_element.get_attribute("textContent").strip()
                    subsection_url = link_element.get_attribute('href')

                    # Store the subsection data
                    all_section_data.append({
                        "subsection": subsection_text,
                        "url": subsection_url
                    })

                except NoSuchElementException:
                    continue
                except TimeoutException:
                    continue
                except StaleElementReferenceException:
                    continue

        except NoSuchElementException:
            pass

    except WebDriverException as e:
        print(f"An error occurred with the WebDriver: {e}")

    # Article Crawling
    try:
        for section_data in all_section_data:
            try:
                # Navigate to the subsection URL
                driver.get(section_data["url"])

                # Wait for the section to load and find 'section_latest' class
                latest_section = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "section_latest"))
                )

                # Find all section_article within 'section_latest_article'
                section_articles = latest_section.find_elements(By.CLASS_NAME, "section_article")

                # Loop through up to 4 section_article elements
                for section_article in section_articles[:4]:
                    try:
                        # Re-locate the section_article and its sa_list to avoid stale element reference
                        sa_list = section_article.find_element(By.CLASS_NAME, "sa_list")
                        sa_items = sa_list.find_elements(By.CLASS_NAME, "sa_item")

                        # Process each 'sa_item'
                        for sa_item in sa_items:
                            try:
                                # Extract title, link, summary, and press name
                                title_element = sa_item.find_element(By.CLASS_NAME, "sa_text_title")
                                article_title = title_element.text.strip()
                                article_url = title_element.get_attribute("href")

                                summary_element = sa_item.find_element(By.CLASS_NAME, "sa_text_lede")
                                summary_text = summary_element.text.strip()

                                press_element = sa_item.find_element(By.CLASS_NAME, "sa_text_press")
                                press_name = press_element.text.strip()

                                # Truncate the summary to 50 characters and add "..." if necessary
                                if len(summary_text) > 70:
                                    summary_text = summary_text[:70] + "..."

                                # Check if a similar article or the same URL already exists
                                duplicate_found = False
                                for existing_article in all_article_data:
                                    if are_similar(existing_article['title'], article_title) or \
                                            existing_article['url'] == article_url:
                                        duplicate_found = True
                                        break

                                if not duplicate_found:
                                    # Store the collected data for the article
                                    all_article_data.append({
                                        "subsection": section_data['subsection'],
                                        "title": article_title,
                                        "summary": summary_text,
                                        "press": press_name,
                                        "url": article_url
                                    })

                            except NoSuchElementException:
                                continue
                            except TimeoutException:
                                continue
                            except StaleElementReferenceException:
                                continue

                    except NoSuchElementException:
                        continue
                    except TimeoutException:
                        continue
                    except StaleElementReferenceException:
                        continue

            except NoSuchElementException:
                continue
            except TimeoutException:
                continue
            except StaleElementReferenceException:
                continue

    except WebDriverException as e:
        print(f"An error occurred with the WebDriver during the article crawling: {e}")

    # Writing Data to File
    try:
        with open(economics_file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} 경제 영역별 뉴스 모음 ===\n\n\n")

            # 목차 추가
            file.write("목차:\n")
            for idx, section_data in enumerate(all_section_data, 1):
                file.write(f"{idx}. === {section_data['subsection']} ===\n")
            file.write("\n\n")

            current_subsection = None

            for data in all_article_data:
                if current_subsection != data['subsection']:
                    current_subsection = data['subsection']
                    file.write(f"=== {current_subsection} ===\n\n")

                try:
                    # Navigate to the article URL to get the publication date
                    driver.get(data["url"])

                    # Wait for the article page to load and find the published date
                    date_elements = driver.find_elements(By.CLASS_NAME, "media_end_head_info_datestamp_time")
                    if len(date_elements) == 2:
                        published_date = date_elements[0].text.strip()
                        modified_date = driver.find_element(
                            By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME"
                        ).text.strip()
                    else:
                        published_date = date_elements[0].text.strip()
                        modified_date = None

                    # Write the details to the file
                    file.write(f"제목: {data['title']}\n내용: {data['summary']}\n언론사: {data['press']}\n")
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
        print(f"An error occurred while writing to the file: {e}")

    finally:
        # Ensure the browser is closed even if an error occurs
        driver.quit()

    # Confirm the file has been saved
    if economics_file_path:
        print(f"Economic news file saved at: {economics_file_path}")


if __name__ == "__main__":
    main()
