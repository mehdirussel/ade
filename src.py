import time
import datetime
import urllib.request
import json

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import StaleElementReferenceException,ElementClickInterceptedException,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def my_date_format(str_date):
    months_list = [
    'janvier',
    'février',
    'mars',
    'avril',
    'mai',
    'juin',
    'juillet',
    'août',
    'septembre',
    'octobre',
    'novembre',
    'décembre'
    ]
    list_words = str_date.split()
    month = months_list.index(list_words[0]) + 1
    year = list_words[1]

    return datetime.datetime.strptime(str(month) + ' ' + str(year), "%m %Y")

def set_date_to_cal(driver,date_to_input,is_end_date,timeout_for_wait=10):# if to set end date make is_end_date = 1; date_to_input should be datetime object
    print("set_date_to_cal",end=':')
    end_or_start_list = ['Date de début','Date de fin']
    print(end_or_start_list[is_end_date])
    #input start and end date
    calendar_buttons = driver.find_elements(By.XPATH,"//input[contains(@title, 'Press Down arrow to select date from a calendar grid')]") # get the calendar icons to show calendar
    calendar_buttons[is_end_date].click()
    #get left and right buttons by their images
    try:
        left_button = WebDriverWait(driver, timeout_for_wait).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,".x-date-left-icon")) 
        )
    except TimeoutException:
        print("Could not find element!!")

    try:
        right_button = WebDriverWait(driver, timeout_for_wait).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,".x-date-right-icon"))
        )
    except TimeoutException:
        print("Could not find element!!")
    
    print("found both buttons")
    # get selected month and year -> text inside calendar, in 'str(month) yyyy' format and make datetime object with it
    cal_current_date = my_date_format(driver.find_element(By.CSS_SELECTOR,"em.x-btn-arrow > button").text) # returns datetime object

    #setting the date
    # keep clicking left/right to get to wanted month & year
    while (cal_current_date.month != date_to_input.month or cal_current_date.year != date_to_input.year):
        if date_to_input < cal_current_date:
            left_button.click()
            print("clicked on left arrow")
        elif date_to_input > cal_current_date:
            right_button.click()
            print("clicked on right arrow")
        else:
            break
        # refresh calendar date
        cal_current_date = my_date_format(driver.find_element(By.CSS_SELECTOR,"em.x-btn-arrow > button").text) # returns datetime object

    id_of_first_day_of_month_button = driver.find_element(By.CSS_SELECTOR,".x-date-inner tr:nth-of-type(1) .x-date-active, .x-date-inner tr:nth-of-type(2) .x-date-active").get_attribute("id") # will be smthg like this x-auto-i
    # get the i
    i = int(id_of_first_day_of_month_button.split('-')[-1])
    #the button we want to click on is x-auto-{i+day-1}
    day_button = driver.find_element(By.ID,f"x-auto-{str(int(i+date_to_input.day)-1)}")
    day_button.click()
    print("clickd on the wanted date")

def download_and_save_if_different(url, local_file_path,new_file_folder_path):
    """Download a file from the given URL and save it locally if it's different."""
    # Download the file
    response = urllib.request.urlopen(url)
    data = response.read()

    # Check if the files are different
    if cmp_calendar(local_file_path, data):
        print("Calendars are different. Downloading the new one...")
        # Save the downloaded file with the original file name
        with open(new_file_folder_path+"\ADECal.ics", 'wb') as file:
            file.write(data)
        print("new calendar downloaded successfuli")
    else:
        print("Files are identical. No need to download.")




class edt_retriever():
  # launches the firefox webdriver, down_path for where to save pdf and ics file
  def __init__(self,choix_edt, down_path,timeout=4,driver_path=0,headless_mode=1):
    """
    Args:
        choix_edt (list): doit etre liste ordonnéee des boutons cliqués (majuscule ou miniscule doesnt matter), they will all be collpased until the last one which will be clicked on; eg: ["eTudiants","EnsiSa","inGénieuRS","1A","infOrMatique"]
        timeout (int): maximum time in seconds for selenium to wait for elements to appear, should be at least 8 for all the functions to work : login(needs 4s) and get_ics(sometimes needs 8s)
        down_path (string): Path where downloaded files will be stored
        driver_path (string): is the path of the firefox driver, if no value is given then webdriver_manager is used

    """
    self.timeout = timeout
    self.down_path = down_path
    self.choix_edt = choix_edt
    
    # browser settings
    opts = webdriver.FirefoxOptions()
    if headless_mode:
        opts.add_argument("--headless")
    # set lang to french
    # important car sinon c'est anglais = cant click on 1st row
    opts.set_preference('intl.accept_languages', 'fr-fr')
    # disable showing download progress
    opts.set_preference("browser.download.manager.showWhenStarting", False)
    opts.set_preference("browser.helperApps.alwaysAsk.force", False)
    opts.set_preference("pdfjs.disabled", True)
    opts.set_preference("pdfjs.enabledCache.state",False)
    opts.set_preference("browser.download.improvements_to_download_panel", True)
    # dir
    opts.set_preference("browser.download.folderList", 2)
    opts.set_preference("browser.download.useDownloadDir", True)
    # TODO this doesn work, file is still donwlaoded in Downloads folder
    opts.set_preference("browser.download.dir", down_path)
    # dont ask for pdf and calendar files
    opts.set_preference("browser.helperApps.neverAsk.saveToDisk",
                       "application/pdf, text/calendar, application/octet-stream") 

    if driver_path: #driver path is given
        self.driver = webdriver.Firefox(service=Service(driver_path), options=opts)
    else:
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=opts)

  def __del__(self):
    
    # logout from session
    self.driver.get("https://cas.uha.fr/cas/logout")
    
    # close the webdriver
    self.driver.quit()
    print("logged out and exit the program")

  def login(self, email, passwd):  # login au site et sélectionne l'edt
    # enter login website
    self.driver.get(
        "https://cas.uha.fr/cas/login?service=https%3A%2F%2Fwww.emploisdutemps.uha.fr%2Fdirect%2F")

    # si on est déja connecté
    if (not str(self.driver.current_url).startswith("https://www.emploisdutemps.uha.fr")):  # pas déja connecté
      self.driver.find_element(By.ID, "username").send_keys(email)
      self.driver.find_element(By.ID, "password").send_keys(passwd)
      self.driver.find_element(By.NAME, "submit").click()
      print("logged in successfully")

    # attendre redirection
    WebDriverWait(self.driver, 100).until(
        EC.url_matches("https://www.emploisdutemps.uha.fr/*")
        )
    # acces a l"emploi de temps souhaité

    # Set the self.timeout
    

    # Wait for the presence of the element before clicking
    for idx,elt in enumerate(self.choix_edt):
        try:
            main_tag = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'*[aria-label*="{elt}" i]'))
            )
            icon_list = main_tag.find_elements(by=By.TAG_NAME, value='img')
            # waits until tag is found, and grabs the list of all images under that tag
            # 1st element is an empty image, 2nd is the collapse icon, 3rd is the folder icon on which we can click to access the folder

            if idx == (len(self.choix_edt)-1):
                icon_list[2].click() # last element open folder
                print(f"Clicked on {elt}'s folder icon")
            else:
                icon_list[1].click() # not last element collapse folder
                print(f"Clicked on {elt}'s collapse icon")
        except TimeoutException:
            print(f"Could not find element: {elt}")
        
    

    #wait for the planning to appear

    WebDriverWait(self.driver, self.timeout).until(  # wait 8 seconds for planning to load
        EC.presence_of_element_located(
            (By.CLASS_NAME, "grilleDispo"))
    )
    print("found the planning grid")
    
    
  def get_pdf(self):  # get pdf
    print("pdf retrieval")
    # find pdf button
    pdf_button = self.driver.find_element(By.ID,'x-auto-28') # will find a table
    # keep ckicking until window show up :)
    pdf_button.click()
    print("clicked on print button! (1st time)")
    try:
        while not len(self.driver.find_elements(by=By.XPATH, value="//span[contains(.,'Génération du planning dans un fichier PDF')]")):
            pdf_button.click()
            print("clicked again on print button !")
    except StaleElementReferenceException:
        pass
    print("found the pdf window!! ")
    
    
  
    ok_button = WebDriverWait(self.driver, self.timeout).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,\'Ok\')]"))
    )
    # click ok
    ok_button.click()
    print("pressed ok btton")
    # wait till pdf downloaded
    time.sleep(5) 
    # TODO find a better way to detect if file is downloaded
    print("file donwloaded")

  def get_ics(self, start_date, end_date):  # get ics file
    """
        Args:
            function (callable): Get latest version of planning and compares it to old ics file if specified. The old file needs to have the same start and end dates !!
            start_date (string): dd-mm-yyyy
            end_date (string): dd-mm-yyyy
        Returns:
            ics file link (string): can be accessed wihout login
        """
    print("ics retrieval")
    #check dates

    try:
        start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
        print("Dates are valid")
    except ValueError:
        print("Dates are invalid")
        return None



    # find export button
    export_button = self.driver.find_element(By.ID,'x-auto-29') # will find a table
    #keep ckicking until window show up 
    export_button.click()
    print("clicked on export button! (1st time)")
    try:
        while not len(self.driver.find_elements(by=By.XPATH, value="//span[contains(.,'Export ICalendar ou VCalendar')]")):
            export_button.click()
            print("clicked again on export button !")
    except StaleElementReferenceException:
        pass
    print("found the export window!! ")
    
    set_date_to_cal(self.driver,start,0,self.timeout)
    set_date_to_cal(self.driver,end,1,self.timeout)


    # Generate URL
    generate_url_button = WebDriverWait(self.driver, self.timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Générer URL')]"))
    )
    generate_url_button.click()

    # Get link
    link_element = WebDriverWait(self.driver, timeout=self.timeout).until(
        EC.presence_of_element_located((By.XPATH, "//fieldset/div/div/a"))
    )
    link = link_element.get_attribute("href")
    print("retrieved ics file link")
    

    # close the popup
    btn_fermer = WebDriverWait(self.driver, self.timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Fermer')]"))
    )
    btn_fermer.click()
    
    btn_annuler = WebDriverWait(self.driver, self.timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Annuler')]"))
    )
    btn_annuler.click()

    return link
    


"""
credentials.json file format:
{
    "username":"your email",
    "password":"your password"
}

"""

creds_path = "credentials.json"
with open(creds_path, "r") as creds_file:
    credentials = json.load(creds_file)


email = credentials["username"]
pwd = credentials["password"]

edt = ["eTudiants","EnsiSa","inGénieurS","1A","InFormatiqUe"]

test = edt_retriever(edt,"C:/Users/mehdi/Desktop/edt ensisa/",4,headless_mode=0)

test.login(email,pwd)
print(test.get_ics("11-11-2023","12-12-2023"))
test.get_pdf()
