from common_imports import *


def my_date_format(str_date): # example: "octobre 2020" -> appropiate datetime object
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

    return datetime.strptime(str(month) + ' ' + str(year), "%m %Y")

def set_date_to_cal(driver,date_to_input,is_end_date,timeout_for_wait=10):# if to set end date make is_end_date = 1; date_to_input should be datetime object
    print("set_date_to_cal",end=':')
    if is_end_date:
        print("fin")
    else:
        print("début")
    time.sleep(3)
    calendar_buttons = driver.find_elements(By.XPATH,"//input[contains(@title, 'Press Down arrow to select date from a calendar grid')]") # get the calendar icons to show calendar
    calendar_buttons[is_end_date].click()
    #get left and right arrows by their images
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
    
    print("found both arrows")
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
        # refresh calendar date text
        cal_current_date = my_date_format(driver.find_element(By.CSS_SELECTOR,"em.x-btn-arrow > button").text) # returns datetime object

    print("reached the wanted month & year")
    id_of_first_day_of_month_button = driver.find_element(By.CSS_SELECTOR,".x-date-inner tr:nth-of-type(1) .x-date-active, .x-date-inner tr:nth-of-type(2) .x-date-active").get_attribute("id") # will be smthg like this 'x-auto-i'
    # get the i
    i = int(id_of_first_day_of_month_button.split('-')[-1])
    #the button we want to click on is x-auto-{i+day-1}
    day_button = driver.find_element(By.ID,f"x-auto-{str(int(i+date_to_input.day)-1)}")
    #time.sleep(20000)
    day_button.click()
    print("clickd on the wanted day")

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

def keep_doing_until(elt,arg_list): 
    # arg_list is list of arguments:
    # in this case args_list = [function_tokeep_doing,[stop_condition,[stopc_args_mode,string,stop_args]]]
    action,[stop_condition,[stopc_args_mode,stop_args]] = arg_list

    stopc_args_options = {
        "elt":elt,
        "custom_args":stop_args,
        "both":[elt,stop_args]
    }

    try:
        while not stop_condition(stopc_args_options[stopc_args_mode]):
            if action=="click":
                elt.click()
                print("clicked on the element !")
            else: # click on a 
                action(elt)
                print("acted on the element !")
    except StaleElementReferenceException: # here you can add other exceptions that act as stop condition too
        return

def generic_ec_wait_and_act(driver,timeout,element_selector_tuple,action_todo=None,actual_name=None):
    # actual name is an extra name used for print and debugging
    # action_todo syntax: [action_string,action_args]
    selector_name = actual_name if actual_name else element_selector_tuple[1]
    if action_todo and len(action_todo):
        action_on_it = True
        action,action_args = action_todo
    else:
        action_on_it = False
    
    try:
        elt = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(element_selector_tuple)
        )
        action_mapping_dict = {
            "click":elt.click, # action_args = None
            "text-input":elt.send_keys, # action_args = string to input
            "keep-doing-until":partial(keep_doing_until,elt) # action_args = [function_tokeep_doing,[stop_condition,[stopc_args_mode,stop_args]]]
            # stopc_args_mode allows to determine what arguments stop_condition need
            # stopc_args_mode can be either:
            #   - "elt"  
            #   - "custom_args" for custom arguments, also use this in case there are no arguments, simply add an empty argument in your stop condition implementation
            #   - "both": the list [elt,stop_args] is the arument 

            
        }
        print("found: ",selector_name)
        if action_on_it:
            if action_args:
                action_mapping_dict[action](action_args)
                print("acted on it: ",action," with arguments ", action_args if action!="keep-doing-until" else "(too many arguments to print)")
            else: # action_args is none
                action_mapping_dict[action]()
                print("acted on it with no arguments: ",action)
        print("******************")
        return elt
    except TimeoutException:
        print(selector_name," not found!")
        return None


def array_ec_action(driver,timeout,selectors_list_with_action):
    #input list: [selector_tuple,[action_string,action_args]]
    for s,a,name in selectors_list_with_action:
        generic_ec_wait_and_act(driver,timeout,s,a,actname)

def check_presence(arg_list):
    driver,selector = arg_list
    return len(driver.find_elements(*selector)) # asterisk to unpack the tuple elements instead of inputing the tuple whole

class edt_retriever():
  # launches the firefox webdriver, down_path for where to save pdf and ics file
  def __init__(self,choix_edt, down_path,timeout=15,driver_path=0,headless_mode=1):
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
    self.driver.set_window_size(800, 800)
    print('browser started')


  def __del__(self):
    
    # logout from session
    self.driver.get("https://cas.uha.fr/cas/logout")
    
    # close the webdriver
    self.driver.quit()
    print("logged out and exit the program")

  def login(self,creds_path):  # login au site et sélectionne l'edt
    
    with open(creds_path, "r") as creds_file:
        credentials = json.load(creds_file)
    email = credentials["username"]
    passwd = credentials["password"]
    print("found credentials file")
    
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
    WebDriverWait(self.driver, 20).until(
        EC.url_matches("https://www.emploisdutemps.uha.fr/*")
        )
    
    # accès a l"emploi de temps souhaité

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
            (By.CLASS_NAME, "grilleDispo")
        )
    )
    print("found the planning grid")
    

  def get_pdf(self):
    """
        Args:
            None
        Returns:
            None - downloads current week's pdf timetable into the directory specified at init
        """

    print("pdf retrieval")

    # pdf button
    generic_ec_wait_and_act(self.driver,self.timeout,(By.ID,"x-auto-28"),["keep-doing-until", # [function_tokeep_doing,[stop_condition,[stopc_args_mode,stop_args]]]
        ["click",
            [check_presence,
                ["custom_args",[self.driver,(By.XPATH,"//span[contains(.,'Génération du planning dans un fichier PDF')]")]]
            ]
        ]
    ],actual_name="pdf window button")
    # ok button
    generic_ec_wait_and_act(self.driver,self.timeout,(By.XPATH, "//button[contains(.,\'Ok\')]"),["click",None],actual_name="ok button")
    # wait till pdf downloaded
    time.sleep(5)
    # TODO find a better way to detect if file is downloaded
    print("file donwloaded")

  def get_ics(self, start_date, end_date,save_ics_to_path=0):  # get ics file
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
        start = datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.strptime(end_date, "%d-%m-%Y")
        print("Dates are valid")
    except ValueError:
        print("Dates are invalid")
        return None



    # find export button; will find a table
    generic_ec_wait_and_act(self.driver,self.timeout,(By.ID,'x-auto-29'),["keep-doing-until", # [function_tokeep_doing,[stop_condition,[stopc_args_mode,stop_args]]]
        ["click",
            [check_presence,
                ["custom_args",[self.driver,(By.XPATH,"//span[contains(.,'Export ICalendar ou VCalendar')]")]]
            ]
        ]
    ],actual_name="export button") 
    
    # input tag containing number of loaded events
    input_num_of_loaded_events = self.driver.find_element(By.XPATH, '//label[contains(.,"Nombre d\'activités à être exportées")]/following-sibling::div//input')
    
    try: # wait until number of elements is loaded
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: input_num_of_loaded_events.get_attribute("value") != ''
                )
    except TimeoutException:
        print("number of elements to import not loaded")
    
    og_num = input_num_of_loaded_events.get_attribute("value")
    
    set_date_to_cal(self.driver,start,0,self.timeout)
    set_date_to_cal(self.driver,end,1,self.timeout)

    try: # need to xait before setting the date and after setting it
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: input_num_of_loaded_events.get_attribute("value") != ''
                )
    except TimeoutException:
        print("number of elements to import not loaded")

    try: # wait a bit incase it changes
            WebDriverWait(self.driver, 4).until(
                lambda driver: input_num_of_loaded_events.get_attribute("value") != og_num
                )
    except TimeoutException: # user chose dates that contain same num of events in this week (og_num) 
        pass
    
    print(input_num_of_loaded_events.get_attribute("value")," events to be exported")


    # Generate URL
    generate_url_button = WebDriverWait(self.driver, self.timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'URL')]"))
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

    if(save_ics_to_path):
        filename = self.down_path + f"ade-{datetime.now().hour}.ics"
        u_r.urlretrieve(link, filename)
        return filename

    return link
    


"""
credentials.json file format:
{
    "username":"your email",
    "password":"your password"
}

"""
def main():
    creds_path = "credentials.json"

    edt = ["eTudiants","EnsiSa","inGénieurS","1A","InFormatiqUe"]

    retriever = edt_retriever(edt,"C:/Users/mehdi/Desktop/edt ensisa/",15,headless_mode=0)

    retriever.login(creds_path)
    print(retriever.get_ics("02-12-2023","20-03-2024",save_ics_to_path=1))
    # retriever.get_pdf()
    

if __name__ == "__main__":
    main()