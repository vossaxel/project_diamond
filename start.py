from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import sys
import random

chrome_options = Options()
# chrome_options.add_argument("--user-data-dir=selenium")
chrome_options.add_argument("headless")
chrome_options.add_argument("window-size=1920,1080")
chrome_options.add_argument("disable-gpu")
browser = webdriver.Chrome(chrome_options=chrome_options)
print("Opening browser, this may take a while...",
      "|", time.asctime(time.localtime(time.time())))
browser.get('https://www.diamondhunt.co/')

wait = WebDriverWait(browser, 5)

seed_list = ['wheatSeeds',
             'redMushroomSeeds',
             'dottedGreenLeafSeeds',
             'blewitMushroomSeeds',
             'greenLeafSeeds',
             'limeLeafSeeds',
             'snapegrassSeeds',
             'carrotSeeds',
             'tomatoSeeds']

potion_list = [
    'seedPotion',
    'smeltingPotion'
]

nav_table = {
    'farming': '//*[@id="tab-container-bar-farming"]',
    'woodcutting': '//*[@id="tab-container-bar-woodcutting"]',
    'crafting': '//*[@id="tab-container-bar-crafting"]',
    'combat': '//*[@id="tab-container-bar-combat"]',
    'brewing': '//*[@id="tab-container-bar-brewing"]'
}


def login():
    try:
        browser.find_element_by_xpath(
            '//*[@id="two-buttons-panel"]/span[2]').click()
    except:
        print("Skipped init-login")
    wait.until(EC.element_to_be_clickable((By.ID, 'username')))
    with open('login.txt', 'r') as f:

        username, password = f.readlines()
        print("Logging in:", username[:-1],
              "|", time.asctime(time.localtime(time.time())))
        userfield = browser.find_element_by_id('username')
        userfield.clear()
        userfield.send_keys(username)
        browser.find_element_by_id('password').send_keys(password)
        browser.find_element_by_id('loginSubmitButton').click()


def wait_for_setup():
    xpath = '//*[@id="tab-container-bar-farming"]'
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        return
    else:
        return


def navigate(tab_name):
    try:
        tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, nav_table[tab_name])))
    except TimeoutException:
        return
    else:
        click_paus()
        tab.click()


def xpath_get_text(xpath):
    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        return ""
    else:
        return element.text


def xpath_click(xpath):
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        return
    else:
        click_paus()
        element.click()


def close_dialog():
    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()


def brewing():
    close_dialog()
    navigate('brewing')
    potion_dict = fetchdata(potion_list)
    for potion, amount in potion_dict.items():
        pot_time = browser.execute_script('return %sTimer' % potion)
        if pot_time == 0:
            if amount > 0:
                xpath_click('//*[@id="item-box-%s"]' % potion)
                click_paus()
                navigate('brewing')
                click_paus()
                xpath_click('//*[@id="dialogue-confirm-yes"]')
                click_paus()
                close_dialog()
                print("Drinking %s" % potion, "|", time.asctime(
                    time.localtime(time.time())))
            else:
                print("No %ss" % potion)


def combat():
    close_dialog()
    navigate('combat')
    fight_time = browser.execute_script('return combatGlobalCooldown')
    energy = browser.execute_script('return energy')
    if fight_time == 0:
        if energy > 100:
            xpath_click('//*[@id="tab-sub-container-combat"]/span[1]')
            click_paus()
            xpath_click('//*[@id="forest-tr"]/td[2]/img')
            click_paus()
            xpath_click('//*[@id="dialogue-confirm-yes"]')
            click_paus()
            close_dialog()
            print("Entered forest", "|", time.asctime(
                time.localtime(time.time())))
        else:
            print("No energy")
    else:
        sys.stdout.write("%i seconds left on fighting cooldown" %
                         fight_time + '     \r')
        time.sleep(3)
        sys.stdout.write('                                        \r')


def farming():
    close_dialog()
    navigate('farming')
    seed_dict = fetchdata(seed_list)
    plant = False
    for i in range(1, 5):
        if xpath_get_text('//*[@id="farming-patch-text-%d"]' % i) in ("Click to harvest", "Click to grow"):
            plant = True
            break
    if plant:
        for seed, amount in seed_dict.items():
            if amount > 0:
                xpath_click('//*[@id="item-box-planter"]')
                click_paus()
                xpath_click('//*[@id="dialogue-plant-%s"]' % seed)
                click_paus()
                close_dialog()
                print("Planted", seed,  "|", time.asctime(
                    time.localtime(time.time())))
                return


def fishing():
    if(browser.execute_script('return fightMonsterId') != 0):
        print("In combat, skipping boat")
        return
    close_dialog()
    navigate('combat')
    boat_time = browser.execute_script('return canoeTimer')
    bait = browser.execute_script('return fishingBait')
    if boat_time == 0:
        if bait > 0:
            xpath_click('//*[@id="item-box-boundCanoe"]')
            click_paus()
            navigate('combat')
            click_paus()
            xpath_click('//*[@id="dialogue-id-boat"]/input[2]')
            click_paus()
            close_dialog()
            print("Sent boat",
                  "|", time.asctime(time.localtime(time.time())))
        else:
            print("No bait")
    else:
        sys.stdout.write("%i seconds left on boat" % boat_time + '     \r')
        time.sleep(3)
        sys.stdout.write('                                        \r')


def woodcutting():
    close_dialog()
    navigate('woodcutting')
    for i in range(1, 5):
        if xpath_get_text('//*[@id="wc-div-tree-lbl-%d"]' % i) == "(ready)":
            xpath_click('//*[@id="wc-img-tree-%d"]' % i)
            click_paus()
            xpath_click('//*[@id="dialogue-loot"]/input')
            click_paus()
            close_dialog()
            print("Chopped wood in slot", i,
                  "|", time.asctime(time.localtime(time.time())))


def crafting(bar_type, amount):
    close_dialog()
    navigate('crafting')
    smelt_perc = browser.execute_script('return smeltingPerc')
    if smelt_perc == 0:
        xpath_click('//*[@id="item-box-boundGoldFurnace"]')
        click_paus()
        xpath_click('//*[@id="input-furnace-%s-bar"]' % bar_type)
        click_paus()
        browser.find_element_by_id('input-smelt-bars-amount').clear()
        browser.find_element_by_id(
            'input-smelt-bars-amount').send_keys(amount)
        xpath_click('//*[@id="dialogue-furnace-mats-needed-area"]/input')
        click_paus()
        close_dialog()
        print("Added %s %sbars to furnace" % (amount, bar_type),
              "|", time.asctime(time.localtime(time.time())))
    else:
        sys.stdout.write("Smelting %i%% done" % smelt_perc + '     \r')
        time.sleep(3)
        sys.stdout.write('                                        \r')


def fetchdata(key_list):
    data_dict = {}
    for key in key_list:
        data_dict[key] = browser.execute_script('return %s' % key)
    return data_dict


def click_paus():
    st = random.uniform(0.5, 1.5)
    time.sleep(st)


def pause():
    sec = int(random.uniform(1, 5)*random.uniform(30, 35))
    while sec > 0:
        if sec % 10 == 0:
            close_dialog()
        sys.stdout.write("Sleeping for %s seconds" % str(sec) + '     \r')
        sec -= 1
        time.sleep(1)
    sys.stdout.write('                                        \r')


def main():
    login()
    wait_for_setup()
    while True:
        close_dialog()
        farming()
        fishing()
        brewing()
        crafting("bronze", "150")
        combat()
        pause()


main()
