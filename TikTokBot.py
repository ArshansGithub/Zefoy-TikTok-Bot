# github.com/arshansgithub
# Developed by Arshan S

import base64
import io
import random
import string
import time
from urllib.parse import unquote, quote

import os
import bs4
import pytesseract
import requests
from PIL import Image
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

pytesseract.pytesseract.tesseract_cmd = "Fill This In"

session = requests.Session()
session.proxies.update(None) # Put your proxy here

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
operating_systems = [OperatingSystem.WINDOWS.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

user_agent = user_agent_rotator.get_random_user_agent()
encodedUserAgent = quote(user_agent)

# random window size
window_sizes = ["800x600", "1024x768", "1280x720", "1366x768", "1600x900", "1920x1080", "1536x730"]
window_size = random.choice(window_sizes)

def solveCaptcha(img):
    return pytesseract.image_to_string(Image.open(io.BytesIO(img))).strip()

def handleCaptcha(html):
    parser = bs4.BeautifulSoup(html, "html.parser")

    extractID = parser.find("input", {"class": "form-control form-control-lg text-center rounded-0 remove-spaces"}).get(
        "name")

    img = "https://zefoy.com/" + parser.find("img", {"class": "img-thumbnail card-img-top border-0"}).get("src")
    getImg = session.get(img, headers={"User-Agent": user_agent})

    captcha = solveCaptcha(getImg.content)

    open(f"captchas/{captcha}.png", "wb").write(getImg.content)

    solveRequest = session.post("https://zefoy.com",
                                headers={"User-Agent": user_agent, "Content-Type": "application/x-www-form-urlencoded"},
                                data=f"{extractID}={captcha}")

    if ".php?_CAPTCHA" in solveRequest.text:
        print("Captcha failed, solving again")
        return handleCaptcha(solveRequest.text)

    if solveRequest.status_code == 200:

        toScrape = bs4.BeautifulSoup(solveRequest.text, "html.parser")

        allCards = toScrape.find_all("div", {"class": "card m-b-20 card-ortlax"})

        statuses = toScrape.find_all("p", {"class": "card-text"})

        return statuses, allCards


def initSession():
    toReturn = {}

    req = session.get("https://zefoy.com", headers={"User-Agent": user_agent})

    session.cookies.set("window_size", window_size)
    session.cookies.set("user_agent", encodedUserAgent)

    if "captcha" in req.text:

        statuses, allCards = handleCaptcha(req.text)

        for status in statuses:
            title = status.parent.find("h5").text.strip()
            if status.text == "soon will be update":
                toReturn[title] = {"status": "Needs update"}
            else:
                extractInt = status.text.split(" ")[0]
                toReturn[title] = {"status": "Updated: " + extractInt + " days ago"}

        for card in allCards:
            title = card.find("h5").text.strip()
            toReturn[title]["form_action"] = card.find("form").get("action")
            toReturn[title]["input_name"] = card.find("input", {"class": "form-control"}).get("name")

        return toReturn
    else:
        print("No captcha found")
        print(req.text)
        return None


def handle_cooldown(html):
    val = None
    for line in html.split("\n"):
        if "var ltm" in line:
            val = int(line.split("=")[1].split(";")[0])
            break
    if val is None:
        return [0, 0]
    return [int(val / 60), int(val % 60)]


def handle_success(html):
    scraper = bs4.BeautifulSoup(html, "html.parser")
    form_action = scraper.find("form").get("action")
    input_name = scraper.find("input").get("name")
    input_value = scraper.find("input").get("value")
    video_likes = scraper.find("button").text.strip()

    return [form_action, input_name, input_value, video_likes]


def handle_final_success(html):
    scraper = bs4.BeautifulSoup(html, "html.parser")

    cooldown = handle_cooldown(html)

    result = scraper.findAll("span")[1].text.strip()

    return [cooldown, result]


def generate_boundary():
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

def send_request(url, headers, data):
    try:
        return session.post(url, headers=headers, data=data).text
    except requests.RequestException as e:
        print(f"Error in sending request: {e}")
        return None
def process_cooldown(result):
    cooldown = handle_cooldown(result)
    print(f"Cooldown: {cooldown[0]} minutes, {cooldown[1]} seconds")
    return (cooldown[0] * 60) + cooldown[1]

def process_success(result):
    success = handle_success(result)
    print(f"Is it the video with {success[3]} likes?")
    user_input = input("Y/N:\n\n> ")

    if user_input.lower() == "y":
        process_user_confirmation(success)
    else:
        input("Press enter to go back to menu")
        menu()

def process_user_confirmation_loop(success):
    boundary = generate_boundary()
    payload = f"------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"{success[1]}\"\r\n\r\n{success[2]}\r\n------WebKitFormBoundary{boundary}--\r\n"

    headers = {
        "User-Agent": user_agent,
        "origin": "https://zefoy.com",
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
    }

    req_text = send_request("https://zefoy.com/" + success[0], headers, payload)

    if req_text is not None:
        final = handle_final_success(decode(req_text))
        print(f"Result: {final[1]}")
        return (final[0][0] * 60) + final[0][1]
    else:
        print("Something went wrong")
        print(req_text)

def process_user_confirmation(success):
    boundary = generate_boundary()
    payload = f"------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"{success[1]}\"\r\n\r\n{success[2]}\r\n------WebKitFormBoundary{boundary}--\r\n"

    headers = {
        "User-Agent": user_agent,
        "origin": "https://zefoy.com",
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
    }

    req_text = send_request("https://zefoy.com/" + success[0], headers, payload)

    if req_text is not None:
        final = handle_final_success(decode(req_text))
        print(f"Result: {final[1]}")
        print(f"Cooldown: {final[0][0]} minutes, {final[0][1]} seconds")
        input("Press enter to go back to menu")
        menu()
    else:
        print("Something went wrong")
        print(req_text)
        input("Press enter to go back to menu")
        menu()

def handle_choice_loop(choice, title, tiktok, boundary=None):
    form_action = choice["form_action"]
    input_name = choice["input_name"]
    if boundary is None:
        boundary = generate_boundary()

    payload = f"------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"{input_name}\"\r\n\r\n{tiktok}\r\n------WebKitFormBoundary{boundary}--\r\n"

    headers = {
        "User-Agent": user_agent,
        "origin": "https://zefoy.com",
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
    }

    req_text = send_request("https://zefoy.com/" + form_action, headers, payload)

    if req_text is not None:
        result = decode(req_text)
        if title in ["Hearts", "Views", "Shares", "Favorites"]:
            if "seconds for your next submit!" in result:
                timeInSeconds = process_cooldown(result)
                print(f"Waiting {timeInSeconds} seconds")
                time.sleep(timeInSeconds)
                return handle_choice_loop(choice, title, tiktok, boundary)
            elif '<button type="submit" class="' in result:
                timeout = process_user_confirmation_loop(handle_success(result))
                if timeout is not None:
                    print(f"Waiting {timeout} seconds")
                    time.sleep(timeout)
                return handle_choice_loop(choice, title, tiktok, boundary)
            elif "Session expired." in result:
                print("Something went wrong")
                input("Press enter to go back to menu")
                return menu()
            elif "No an comment found." in result:
                print("No comments found on that video!")
                input("Press enter to go back to menu")
                return menu()
            elif "Too many requests. Please slow down." in result:
                print("Too many requests. Please slow down.")
                time.sleep(5)
                return handle_choice_loop(choice, title, tiktok, boundary)
            else:
                print(result)
                input("Press enter to go back to menu")
                return menu()
        elif title in ["Followers"]:
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
        elif title in ["Comments Hearts"]:
            print(result)
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
        elif title in ["Live Stream [VS+LIKES]"]:
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
    else:
        print("Something went wrong")
        print(req_text)
        input("Press enter to go back to menu")
        return menu()

def handle_choice(choice, title, tiktok):
    form_action = choice["form_action"]
    input_name = choice["input_name"]
    boundary = generate_boundary()

    payload = f"------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"{input_name}\"\r\n\r\n{tiktok}\r\n------WebKitFormBoundary{boundary}--\r\n"

    headers = {
        "User-Agent": user_agent,
        "origin": "https://zefoy.com",
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
    }

    req_text = send_request("https://zefoy.com/" + form_action, headers, payload)

    if req_text is not None:
        result = decode(req_text)
        if title in ["Hearts", "Views", "Shares", "Favorites"]:
            if "seconds for your next submit!" in result:
                process_cooldown(result)
            elif '<button type="submit" class="' in result:
                process_success(result)
            elif "Session expired." in result:
                print("Something went wrong")
                input("Press enter to go back to menu")
                return menu()
            elif "No an comment found." in result:
                print("No comments found on that video!")
                input("Press enter to go back to menu")
                return menu()
            else:
                print(result)
                input("Press enter to go back to menu")
                return menu()
        elif title in ["Followers"]:
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
        elif title in ["Comments Hearts"]:
            print(result)
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
        elif title in ["Live Stream [VS+LIKES]"]:
            print("This module is not supported yet")
            input("Press enter to go back to menu")
            return menu()
    else:
        print("Something went wrong")
        print(req_text)
        input("Press enter to go back to menu")
        return menu()



def decode(toDecode):
    reversed = toDecode[::-1]
    unquoted = unquote(reversed)
    decoded = base64.b64decode(unquoted).decode("utf-8")
    return decoded


def menu():
    os.system("cls")
    for key, value in enumerate(init):
        print("[" + str(key) + "] " + value + " - " + init[value]["status"])
    print(f"[{len(init)}] Loop Likes")
    print(f"[{len(init) + 1}] Loop Views")
    print("[x] Exit")

    userInput = input("\nChoice:\n\n> ")

    if userInput.lower() == "x":
        print("Exiting")
        exit()

    if int(userInput) < len(init):
        if userInput not in [str(x) for x in range(len(init))]:
            print("Invalid choice")
            input("Press enter to go back to menu")
            return menu()
        print("You chose " + list(init.keys())[int(userInput)])
        title = list(init.keys())[int(userInput)]
        choice = init[list(init.keys())[int(userInput)]]
        if choice["status"] == "Needs update":
            print("This module needs an update!")
            input("Press enter to go back to menu")
            return menu()
    elif int(userInput) >= len(init):
        difference = int(userInput) - len(init)
        if difference == 0:
            print("You chose to loop likes")
            title = "Hearts"
            choice = init["Hearts"]
        elif difference == 1:
            print("You chose to loop views")
            title = "Views"
            choice = init["Views"]

    areYouSure = input("Are you sure you want to continue? Y/N\n\n> ")
    if areYouSure.lower() == "n":
        print("Ok, exiting")
        exit()

    if areYouSure.lower() != "y":
        print("Invalid choice")
        input("Press enter to go back to menu")
        return menu()

    tiktok = input("TikTok Link/Username:\n\n> ")
    if int(userInput) < len(init):
        handle_choice(choice, title, tiktok)
    else:
        handle_choice_loop(choice, title, tiktok)

print("Initializing...")
init = initSession()
if init is None:
    print("No init")
    exit()

menu()
