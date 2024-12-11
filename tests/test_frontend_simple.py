from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import unittest


class TestPourfectAIFrontend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure Chrome 
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=chrome_options)

        # Load the HTML file for our website
        html_file_path = os.path.abspath("index.html")
        print(html_file_path)
        cls.driver.get(f"file:///{html_file_path}")
    

    @classmethod
    def tearDownClass(cls):
        # Quit the browser after all tests are run
        cls.driver.quit()

    # Testing the main page title is correct
    def test_page_title(self):
        """Test that the page title is correct."""
        print(f"Title: {self.driver.title}")
        self.assertEqual(self.driver.title, "Pourfect AI", "Page title is incorrect.")

    # Testing that the nav links are correct
    def test_navigation_links(self):
        """Test that the navigation links are present and correct."""
        nav_links = self.driver.find_elements(By.CLASS_NAME, "nav-link")
        self.assertEqual(len(nav_links), 5, "Navigation links are missing.")
        self.assertEqual(nav_links[0].text, "HOME", "First nav link should be Home.")
        self.assertEqual(nav_links[1].text, "ABOUT", "Second nav link should be About.")
        self.assertEqual(nav_links[2].text, "FOUNDER'S FAVORITES", "Third nav link should be Founder's favorites.")
        self.assertEqual(nav_links[3].text, "PERSONAL BARTENDER", "Fourth nav link should be Personal Bartender.")
        self.assertEqual(nav_links[4].text, "SAVED RECIPES", "Fifth nav link should be Saved Recipes.")

    # Testing the hero section text and buttons are correct
    def test_hero_section_text(self):
        """Test that the hero section text is correct."""
        hero_title = self.driver.find_element(By.CLASS_NAME, "hero-title").text
        self.assertEqual(
            hero_title, "Where every pour is perfectly yours!", "Hero title text is incorrect."
        )

    def test_hero_button_link(self):
        """Test that the hero button link is correct."""
        hero_button = self.driver.find_element(By.CLASS_NAME, "btn-hero")
        self.assertTrue(
            hero_button.get_attribute("href").endswith("/chat.html"), "Hero button link is incorrect."
        )

    # Testing the about section text is correct
    def test_about_section_heading(self):
        """Test that the About section heading is correct."""
        about_heading = self.driver.find_element(By.ID, "about").find_element(By.TAG_NAME, "h2").text
        self.assertEqual(about_heading, "About Us", "About section heading is incorrect.")


if __name__ == "__main__":
    unittest.main()
