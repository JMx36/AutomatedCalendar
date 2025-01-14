from collections import namedtuple
import time
import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# UCI credentials
username = ""
password = ""
UCI_REGISTAR_URL = "https://www.reg.uci.edu/access/student/studylist/?seg=U"
ClassInfo = namedtuple("ClassInfo", ["class_name", "class_time", "days", "front_label", "location"])
TimeInfo = namedtuple("TimeInfo", ["start_hour", "start_min", "end_hour", "end_min", "isPm1", "isPm2"])

_service = Service(executable_path=r"chromedriver.exe")


def login(driver : webdriver.Chrome, waitToClick : int, username : str, password : str, waitTime : int) -> bool:
    """
        Logins into the UCI account of the username

    Args:
        driver (webdriver.Chrome): Driver to use for webscraping
        waitToClick (int): how long to wait until click the login button
        waitTime (int): how long to wait for the button to appear
        
    Returns:
        True if login was successful, false otherwise
    """
    
    try:
        user_entry = WebDriverWait(driver, waitTime).until(
            EC.presence_of_element_located((By.ID, "j_username"))
        )
        
        user_entry.send_keys(username)
        driver.find_element("id", "j_password").send_keys(password)
        time.sleep(waitToClick)
        driver.find_element("name", "submit_form").click()
        
        button = WebDriverWait(driver, waitTime).until(
            EC.presence_of_element_located((By.ID, "trust-browser-button"))
        )
        button.click()
    
    except TimeoutException as e:
        print(e)
        return False

    return True



def SetUp(url : str) -> webdriver.Chrome:
    """
        Sets up the chrome driver and loads the page 

    Args:
        url (str): The url to load the chrome driver

    Returns:
        driver: WebDriver
    """
    # initialize the Chrome driver
    driver = webdriver.Chrome(service=_service)
    # Load webpage
    driver.get(url)
    
    return driver

def get_table_info(driver : webdriver.Chrome, waitTime : int) -> list:
    """
        Gets the info from the UCI Registar account

    Args:
        driver (webdriver.Chrome): Driver to use for webscraping
        waitTime (int): how long to wait for the button to appear

    Returns:
        list: returns a list of data gotten from the table of UCI registar account
    """
    try:

        table_body = WebDriverWait(driver, waitTime).until(
            EC.presence_of_element_located((By.XPATH, "//table[@id='studylistTable']/tbody"))
        )
        '''We use the ./ to find the elements from the next level of the current node. Using .// finds from all levels of the current node'''
        all_trs = table_body.find_elements(By.XPATH, './tr')
        
        '''
        TRs are all the rows in the table body. Based on the website, the information that I want starts
        on row 3 (with the headers of the table). 
        Notes:
            1) There is a weird td nesting that happens on the 9th element of the columns
        '''
        row_data = []
        for tr in all_trs[3:]:
            data = []
            all_tds = tr.find_elements(By.XPATH, "./td")
            for pos, td in enumerate(all_tds):
                if pos >= 9:
                    inner_td = td.find_element(By.TAG_NAME, "td")
                    data.append(inner_td.text)
                else:
                    data.append(td.text)
            row_data.append(data)
        
        #TESTING CODE
        # ------------
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(row_data)
        ## -----------9    
        return row_data
    
    except TimeoutException as e:
        print(e)
    
    return []

def parse_time(time_string : str) -> str:
    time_info = []
    isPM = False
    for index in range(len(time_string)):
        if time_string[index] == ":":
            time_info.append(int(time_string[max(0, index-2): index])) #hour
            time_info.append(int(time_string[index+1: index+3])) #mins
            if time_string[min(index + 3, len(time_string) - 1)] == "p":
                isPM = True
    
    # Following returns includes 12 as PM, however it messes up calculating military times later on
    return TimeInfo(time_info[0], time_info[1], time_info[2], time_info[3], ((isPM and time_info[0] > 0) or (isPM and 12 > time_info[0] > 6)) and time_info[0] != 12, isPM and time_info[2] != 12)


def parse_info(info):
    parsed_info = []
    for index, class_info in enumerate(info):
        class_name = " ".join(class_info[1:3])
        days = class_info[9].split()
        class_time = parse_time(class_info[10])
        front_label = class_info[4] # label like Disc or Lab in case of those type of classes
        location = class_info[11]
        parsed_info.append(ClassInfo(class_name, class_time, days, front_label, location))
      
    # Testing code  
    # ------------
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(parsed_info)
    # ------------
    
    return parsed_info

def get_info():
    driver = SetUp(UCI_REGISTAR_URL)
    login(driver, 1, username, password, 20)
    info = get_table_info(driver, 20)
    # we exclude the last item of the list because we don't need that information
    return parse_info(info[:len(info)-1])

def main():
    driver = SetUp(UCI_REGISTAR_URL)
    login(driver, 1, username, password, 20)
    info = get_table_info(driver, 20)
    parse_info(info[:len(info)-1])

if __name__ == "__main__":
    main()




 