# No local keyword extraction — the agent must decide the focus keyword.
# The tool takes a focus_keyword and returns selected HTML snippets from TAFE NSW search.

from google.adk.agents import Agent
from urllib.parse import quote_plus
import os
from typing import List

# Import selenium components for web scraping
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_tafe_courses_selenium(user_query: str, delay: float = 1.0) -> List[str]:
    """
    Scrapes raw HTML content of course divs from TAFE NSW course search page using Selenium.

    Args:
        user_query (str): The search keyword/query for courses
        delay (float): Delay to wait for content to load (default: 1.0 seconds)

    Returns:
        List[str]: List of raw HTML strings of the course divs
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # On Windows, Chrome should be in the default location
    # options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

    driver = None
    try:
        # Setup Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # URL encode the user query
        encoded_query = quote_plus(user_query)
        url = f"https://www.tafensw.edu.au/course-search?keyword={encoded_query}"

        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for the course results to load
        wait = WebDriverWait(driver, 20)  # Increased timeout for potentially slow loading
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'flex.items-start.px-3.py-4.lg\\:px-0')))

        print(f"Page loaded. Waiting for {delay} seconds for additional content.")
        time.sleep(delay)  # Additional delay to ensure all dynamic content loads

        # Find all divs with the specified class
        course_divs = driver.find_elements(By.CLASS_NAME, 'flex.items-start.px-3.py-4.lg\\:px-0')

        raw_html_contents = []
        for div in course_divs:
            raw_html_contents.append(div.get_attribute('outerHTML'))

        print(f"Successfully found {len(raw_html_contents)} course divs for query: '{user_query}'")
        return raw_html_contents

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit()  # Ensure the browser is closed


def realtime_courses_search__tool(focus_keyword: str) -> str:
    """
    Tool: Given a single focus keyword, hit the TAFE NSW course search,
    and return ONLY the HTML of divs with class="flex items-start px-3 py-4 lg:px-0".
    """
    focus_keyword = (focus_keyword or "").strip()
    if not focus_keyword:
        return "ERROR: focus_keyword is empty."

    try:
        # Use Selenium to scrape the course divs
        snippets = scrape_tafe_courses_selenium(focus_keyword, delay=0.0)
        
        if not snippets:
            return f"No course results found for keyword: {focus_keyword}"
            
        # Join all the HTML snippets with newlines for better readability
        combined = "\n\n".join(snippets)
        
        # Print the scraped content
        print(f"FOCUS_KEYWORD: {focus_keyword}")
        print(f"SOURCE_URL: https://www.tafensw.edu.au/course-search?keyword={quote_plus(focus_keyword)}")
        print(f"FOUND: {len(snippets)} course divs")
        print("HTML_SNIPPETS:")
        print(combined)

        # Return to the agent
        return f"""FOCUS_KEYWORD: {focus_keyword}
SOURCE_URL: https://www.tafensw.edu.au/course-search?keyword={quote_plus(focus_keyword)}
FOUND: {len(snippets)} course divs
HTML_SNIPPETS:
{combined}"""

    except Exception as e:
        error_msg = f"ERROR: Failed to retrieve course information: {str(e)}"
        print(error_msg)
        return error_msg


root_agent = Agent(
    name="consultant_agent",
    description="A Tafe NSW consultant agent who can answer questions about Tafe NSW courses.",
    instruction="""
    Role:
    - You are a consultant agent for Tafe NSW (https://www.tafensw.edu.au/).

    Responsibility:
    - You must choose the single most relevant focus keyword from the user's query yourself.
    - Call the tool 'realtime_courses_search__tool' with that focus keyword.
    - Read only the returned HTML and answer strictly based on that content.
    - If the tool returns an error or empty content, explain that you couldn't retrieve results.

    Knowledge:
    - Beyond the tool response, you know nothing else.

    
    """,
    model="gemini-2.5-flash",
    tools=[realtime_courses_search__tool],
)