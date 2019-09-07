from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
import Logger
from time import sleep

# I use MAC OS X so you need to change the path of ChromeDriver
path = "source/webdrivers/chromedriver"

# The loop of the bot is as follows:
# 1. Login
# 2. Check Status if in ER/ JAIL/ CAUGHT BY A COP
# 3. Check if there is enough energy for an attack (drinks if not enough energy)
# 4. Find a target
# 5. Attack until Battle Points are 0 (100 is max)


class GameBot:
    browser = None
    executable_path = path
    logger = Logger.Logger("Logger")

    def __init__(self, url, username, password, min_level, max_level, max_respect, url_search):
        self.url = url
        self.username = username
        self.password = password
        self.min_level = min_level
        self.max_level = max_level
        self.max_respect = max_respect
        self.url_search = url_search

    # Opening the browser and loading the main page
    def start(self):
        self.browser = webdriver.Chrome(executable_path=self.executable_path)
        self.browser.get(self.url)
        sleep(1)

    # Logging into the game
    def login(self):
        self.browser.find_element_by_name("login[usr]").send_keys(self.username)
        self.browser.find_element_by_name("login[submit]").click()  # Submit form
        sleep(1)
        self.browser.find_element_by_name("login[pwd]").send_keys(self.password)
        self.browser.find_element_by_name("login[submit]").click()  # Submit form
        self.logger.add_line("Logging into: " + self.username)
        sleep(1)

    # This is the FIND A FIGHT search with parameters to look for an opponent who we can beat
    def matchmaker(self):
        self.browser.get(self.url_search)
        sleep(1)
        self.browser.find_element_by_name("min_level").clear()
        self.browser.find_element_by_name("max_level").clear()
        self.browser.find_element_by_name("max_respect").clear()
        sleep(1)
        self.browser.find_element_by_name("min_level").send_keys(self.min_level)
        self.browser.find_element_by_name("max_level").send_keys(self.max_level)
        self.browser.find_element_by_name("max_respect").send_keys(self.max_respect)
        self.browser.find_element_by_class_name("gs-btn-body").click()
        sleep(1)
        self.browser.find_element_by_css_selector("a.beat.btn").click()
        sleep(1)
        self.check_status()

    # Here we check if energy is sufficient and refills (But currently I can't make it to click on a drink)
    def check_energy(self):
        full = 220
        energy = self.browser.find_element_by_xpath("//table/tbody/tr[1]/td[3]/a/u")
        if int(energy.text) < 60:
            bar = self.browser.find_element_by_css_selector("td.u-property:nth-child(3) > a:nth-child(1)")
            try:
                self.browser.execute_script("arguments[0].click();", bar)
            except StaleElementReferenceException as Exception:
                print('StaleElementReferenceException while trying to get to the bar, trying to find element again')
                bar.click()
            sleep(1)

            # Below is where the error pops up "selenium.common.exceptions.StaleElementReferenceException: Message:
            # stale element reference: element is not attached to the page document"

            while energy.text != full:
                sleep(1)
                table = self.browser.find_element_by_class_name("slotsw")
                drink = table.find_element_by_class_name("item")
                self.browser.execute_script("argument[0].click();", drink)
        else:
            self.battle_points()

    # Checking the current status of the account (If in Jail or Hospital or caught by a cop)
    def check_status(self):
        status = self.browser.find_element_by_class_name("mystatus")
        current_status = status.text

        # Checking status if in Hospital
        if current_status == "In ER":
            # uses card to go out of hospital
            self.browser.find_element_by_class_name("pad_item json").click()
            sleep(1)
            self.battle_points()
            # Checking if in Jail
        elif current_status == "Confined to jail":
            # goes to the GYM to train
            self.strength()
            sleep(1)
        # Checking if is caught by a cop
        elif current_status == "Caught by cop":
            # pays the higher price for 99% chance to break free
            self.browser.find_element_by_name("cop[paymax]").click()
            sleep(1)

        else:
            self.check_energy()

    # Training for more INTELLECT
    def intellect(self):
        points = self.browser.find_element_by_xpath("//div[2]/div[1]/div[2]/div[2]/a[1]/span")
        self.browser.find_element_by_xpath("//div[2]/div[1]/div[2]/div[2]/a[1]").click()
        sleep(2)
        while int(points.text) != 0:
            self.browser.find_element_by_class_name("pad_item training_train train_15_on").click()
            sleep(1)
        else:
            self.battle_points()

    # Gym training for more STRENGTH
    def strength(self):
        points = self.browser.find_element_by_xpath("//div[2]/div[1]/div[2]/div[2]/a[2]/span")
        self.browser.find_element_by_xpath("//div[2]/div[1]/div[2]/div[2]/a[2]").click()
        sleep(2)
        while int(points.text) != 0:
            self.browser.find_element_by_class_name("pad_item training_train train_5_on").click()
            sleep(1)
        else:
            self.intellect()

    # check if there are enough battlepoints (max is 100)
    def battle_points(self):
        points = self.browser.find_element_by_class_name("battle_points")
        while int(points.text) != 0:
            self.matchmaker()
        else:
            self.exit()

    # Collecting money from Rackets
    def rackets(self):
        # check how many rackets do you have
        self.browser.find_element_by_class_name("racket_buildings").click()
        sleep(1)
        rackets_all = self.browser.find_element_by_class_name("summary").text
        print(rackets_all)
        racket_top = self.browser.find_element_by_class_name("livenumber").text
        if int(racket_top) > 10000:
            rackets = self.browser.find_elements_by_class_name("btn-row next")
            for racket in rackets:
                racket.click()
                sleep(1)

    def submit(self):
        self.logger.submit()

    def submit_error(self):
        self.logger.add_line("There was an exception during runtime")
        self.logger.submit()

    def exit(self):
        self.browser.find_element_by_class_name("exit-btn smarttip day_night_exit").click()
        sleep(1)