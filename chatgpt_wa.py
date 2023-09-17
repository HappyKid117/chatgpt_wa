from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import warnings
import re
warnings.filterwarnings("ignore")

latest_message_class_name = '_21Ahp'
inp_class_name = '_3Uu1_'
chatgpt_input_box_xpath = '//*[@id="prompt-textarea"]'
current_chat_class_name = '_3W2ap'
search_box_xpath = '//*[@id="side"]/div[1]/div/div/div[2]/div/div[1]/p'
chatgpt_response_xpath = "//*[contains(@class, 'markdown prose w-full break-words dark:prose-invert light')]"

base_prompt = "Reply with greater burstiness and perplexity but keep it short. "

char_names = ["Jack",
              "Serena",
              "Stellar West"
              ]

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def newline():
    ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()

def get_current_chat():
    print("printing current chat...")
    current_chat_elements = driver.find_elements(By.CLASS_NAME, current_chat_class_name)
    current_chat_name = current_chat_elements[len(current_chat_elements)-1].get_attribute("innerText")
    print(">Current chat = "+current_chat_name)
    return current_chat_name

def go_to_chat(chat_name):
    search_box = driver.find_element("xpath", (search_box_xpath))
    print(">Going to chat "+chat_name)
    search_box.send_keys(chat_name+Keys.ENTER)

def get_latest_message():
    messages = driver.find_elements(By.CLASS_NAME, latest_message_class_name)
    latest_message = messages[len(messages)-1].get_attribute("innerText")
    return latest_message

def send_message(string, char):
    driver.switch_to.window(driver.window_handles[2])
    input_box = driver.find_element(By.CLASS_NAME, inp_class_name)
    messages = convert(string)
    input_box.send_keys("_*.{}:*_ ".format(char_names[char]))
    newline()
    for i in messages:
        input_box.send_keys(i)
        newline()
    input_box.send_keys(Keys.ENTER)
    print(">Message sent")

def send_intro():
    input_box = driver.find_element(By.CLASS_NAME, inp_class_name)
    input_box.send_keys('_*.Stellar West*_')
    newline()
    input_box.send_keys('Two characters {} and {} have joined this chat. Talk to them by calling out their name first'.format(char_names[0], char_names[1]))
    input_box.send_keys(Keys.ENTER)

def convert(lst):
    return (lst.splitlines())

def read_chatgpt_response(x):
    response = driver.find_elements(By.XPATH, chatgpt_response_xpath)
    response = response[len(response)-1].get_attribute("innerText")
    print(">Response : " + response)
    return response

def get_chatgpt_response(x, char):
    driver.switch_to.window(driver.window_handles[char])
    chatgpt_input_box = driver.find_element("xpath", (chatgpt_input_box_xpath))
    chatgpt_input_box.send_keys(base_prompt+x+Keys.ENTER)
    time.sleep(3)
    response = read_chatgpt_response(x);
    send_message(remove_emojis(response), char)

def functionality(x):
    print(">Latest message = "+x)
    if(x.startswith("soupy go to ")):
        chat_name = x.replace('soupy go to ', '')
        current_chat = get_current_chat()
        if(current_chat==home_chat):
            send_message("I am going to "+chat_name, 2)
            go_to_chat(chat_name)
            send_intro()
        else:
            send_message("You can't ask me to go to "+chat_name+" from "+current_chat, 2)
        return

    elif(x == "go home soupy"):
        send_message("bye", 2)
        go_to_chat(home_chat)
        send_intro()
        return
    
    elif(x.startswith(".")):
        return
    
    elif(x.startswith("jack ")):
        print(x)
        get_chatgpt_response(x, 0)

    elif(x.startswith("serena ")):
        print(x)
        get_chatgpt_response(x, 1)

def initialize():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:8989")
    func_driver = webdriver.Chrome(options=chrome_options)
    func_driver.switch_to.window(func_driver.window_handles[2])
    print(">Keep the tab active till your home chat appears")
    return func_driver

print(">Starting Bot...")
home_chat = 'bot home chat' # set your private chat
print("Home chat = " + home_chat)
print(">Initializing driver...")
driver = initialize()
go_to_chat(home_chat)
send_intro()
print(">Driver initialized.")
old = ""
while(True):
    try:
        x = get_latest_message().lower()
        if old==x:
            continue
        old = x
        functionality(x)
    except:
        # send_message("Something went wrong")
        print(">ERROR")
    time.sleep(1)
