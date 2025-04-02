import datetime
import json
import logging

import json5
import requests
from bs4 import BeautifulSoup

from custom_components.yuntrack_gpscj.const import REQUEST_TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)

# Some consts
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0"
MAIN_FRAME_URL = "https://www.gpscj.net/?hmm=3"
LOGIN_FORM_URL = "https://www.gpscj.net/logincj.aspx?language=en-us"
LOGIN_URL = "https://www.gpscj.net/logincj.aspx?language=en-us"
POSITIONS_URL = "https://www.gpscj.net/Ajax/DevicesAjax.asmx/GetDevicesByUserID"
TIMEZONE = "-3"
TIMEZONES = "-3:00"


def gpscj_login_and_get_device_position(p_username: str, p_password: str, p_user_id: str, p_device_id: str):
    session = gpscj_create_session_and_login(p_password, p_username)
    device = gpscj_get_position_from_session(p_device_id, p_user_id, session)
    session.close()
    return device


def gpscj_get_position_from_session(p_device_id, p_user_id, session):
    # Fetch positions
    headers = {
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"UserID": p_user_id, "isFirst": True, "TimeZones": TIMEZONES, "DeviceID": p_device_id})
    response = session.post(POSITIONS_URL, data=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    # Check we got a 2xx response.
    response.raise_for_status()
    _LOGGER.info(f"GPSCJ - got location info for device {p_device_id}")
    # Response is JSON. Parse it.
    json_with_json = response.json()
    # print(f"json_with_json: {json_with_json}")
    # This thing has JSON inside JSON. Extract it.
    positions_json = json_with_json["d"]
    # print(f"positions_json: {positions_json}")
    # position is a string with json, in a badly-formatted json (no quotes).
    # use json5 to pars as it's more lenient.
    positions = json5.loads(positions_json)
    # print(f"positions: {positions}")
    # dereference the 'devices' key
    devices = positions['devices']
    # print(f"devices: {devices}")
    # if more than one device, throw
    if len(devices) > 1:
        raise Exception("More than one device found. Not implemented.")
    # dereference the first device
    device = devices[0]
    # print(f"device: {device}")
    # values are all strings; convert lat/long to float direcly in the object
    device['latitude'] = float(device['latitude'])
    device['longitude'] = float(device['longitude'])
    device['baiduLat'] = float(device['baiduLat'])
    device['baiduLng'] = float(device['baiduLng'])
    # distance too
    device['distance'] = float(device['distance'])
    device['course_int'] = int(device['course'])
    # lets parse the 'datacontext' key
    # 'dataContext': '-0---51-18-0-10-0-4'
    # where: 51 is the battery level (51%)
    #        18 is the 4G signal level
    #        10 is the GPS signal level
    datacontext = device['dataContext']
    # split by dashes
    datacontext_values = datacontext.split("-")
    # pick at each by position
    device['battery'] = int(datacontext_values[4])
    device['signal_4g'] = int(datacontext_values[5])
    device['signal_gps'] = int(datacontext_values[7])
    # two date fields, in string format, in UTC. convert to proper modern Python datetime objects.
    # 'serverUtcDate': '2025-03-25 18:12:44'
    # 'deviceUtcDate': '2025-03-24 20:56:12'
    device['serverUtcDate'] = datetime.datetime.strptime(device['serverUtcDate'], "%Y-%m-%d %H:%M:%S")
    device['deviceUtcDate'] = datetime.datetime.strptime(device['deviceUtcDate'], "%Y-%m-%d %H:%M:%S")
    # last-update-time: current time in UTC
    device['last_cloud_update'] = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
    # ensure stopTimeMinute is an int
    device['stopTimeMinute'] = int(device['stopTimeMinute'])
    # calculate the date since which the device is stopped; take current datetime UTC, subtract the stopTimeMinute(s)
    # keep up to second precision, no subseconds
    # and make it explicit UTC timezone
    device['stopTime'] = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        minutes=device['stopTimeMinute'])).replace(microsecond=0).isoformat()
    # make them JSON serializable, with explicit UTC timezone
    device['serverUtcDate'] = device['serverUtcDate'].isoformat() + "Z"
    device['deviceUtcDate'] = device['deviceUtcDate'].isoformat() + "Z"
    # rename some keys so they match HA's standards
    device["server_utc_date"] = device.pop("serverUtcDate")
    device["device_utc_date"] = device.pop("deviceUtcDate")
    device["stop_time"] = device.pop("stopTime")
    device["stop_time_minute"] = device.pop("stopTimeMinute")
    # sort the keys in the device dict
    device = dict(sorted(device.items()))
    return device


def gpscj_create_session_and_login(p_password, p_username):
    session = requests.Session()
    # Set the Session's user agent to the one we want.
    session.headers.update({"User-Agent": USER_AGENT})
    # Hit the login form. This inits the ASP.NET cookie and the VIEWSTATE, server-side.
    login_form_response = session.get(LOGIN_FORM_URL, headers={"Referer": MAIN_FRAME_URL},
                                      timeout=REQUEST_TIMEOUT_SECONDS)
    _LOGGER.info(f"Login form status code: {login_form_response.status_code}")
    # Check we got a 2xx response.
    login_form_response.raise_for_status()
    login_form_response_text = login_form_response.text
    soup = BeautifulSoup(login_form_response_text, "html.parser")
    VIEWSTATE = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    VIEWSTATEGENERATOR = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    EVENTVALIDATION = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    # Login payload
    payload = {
        "__VIEWSTATE": VIEWSTATE,
        "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
        "__EVENTVALIDATION": EVENTVALIDATION,
        "txtUserName": "",
        "txtAccountPassword": "",
        "txtImeiNo": p_username,
        "txtImeiPassword": p_password,
        "btnLoginImei": "",
        "hidGMT": TIMEZONE
    }
    # Login request
    login_response = session.post(LOGIN_URL, data=payload,
                                  headers={"Content-Type": "application/x-www-form-urlencoded"},
                                  timeout=REQUEST_TIMEOUT_SECONDS)
    _LOGGER.info(f"Login status code: {login_response.status_code}")
    # Check we got a 2xx response.
    login_response.raise_for_status()
    login_response_text = login_response.text
    # If we log in too frequently, response will contain 频繁登陆
    if "频繁登陆" in login_response_text:
        _LOGGER.debug(f"Response text: {login_response_text}")
        raise Exception("Too many logins - ratelimited.")
    # If login worked, we should be redirected, via JS: 'parent.location.href='/Monitor.aspx'
    # Check the login_response_text for this string. If it's not there, login failed.
    if "parent.location.href='/Monitor.aspx" not in login_response_text:
        _LOGGER.debug(f"Response text: {login_response_text}")
        _LOGGER.error("GPSCJ Login failed.")
        raise Exception("Login failed.")
    _LOGGER.info("GPSCJ Login successful.")
    return session
