#!/usr/bin/python

import config
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, re
import termux

link = config.link

options = webdriver.FirefoxOptions()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)
driver.get(link)

posts = driver.find_elements(By.CLASS_NAME, 'page-link')[0]
posts_num = int(posts.get_attribute('innerText').split(' ')[1])

if not config.pc_debug_no_termux:
  if config.show_toasts:
    termux.API.generic(["termux-toast", "-g", "middle", "-s", "Fakt Mobile: starting script"])

time.sleep(0.5)

driver.get(f"{link}&start={posts_num-config.num_of_latest_codes}")
messages = driver.find_elements(By.CLASS_NAME, 'content')
filtered = []

for message in messages:
  text = message.get_attribute("innerText")
  regex = re.findall("((( ?[tT][Oo0]\\.? +\\.?)|(-?> *)|( *- *)|( *[:;][\\n )]*)|(= *))([a-zA-Z0-9]{3,}))|([kK][oO][dD] +([a-zA-Z0-9]{3,})( +[nN][Aa])?)|(([a-zA-Z0-9]{3,})(( *-)|( tylko)))|(([a-zA-Z0-9]{3,}) *$)|( +([a-zA-Z0-9]{3,}) *,)", text)
  for possible_code in regex:
    possible_code_positions = [7, 9, 12, 17, 19]
    possible_codes = []
    for position in possible_code_positions:
      possible_codes.append(possible_code[position])
    filtered.extend([code for code in possible_codes if code.strip() != ""])

driver.close()

if config.pc_debug_no_termux:
  print(filtered)
else:
  for code in filtered:
    termux.API.generic(["termux-sms-send", "-n", "4949", "-s", config.sim, code])
    time.sleep(config.sms_send_timeout)

  if config.show_toasts:
    termux.API.generic(["termux-toast", "-g", "middle", "-s", "Fakt Mobile: end of script"])

  if config.vibrate_at_end:
    termux.API.vibrate()
