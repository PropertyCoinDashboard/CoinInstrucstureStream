import configparser

"""
setting 
"""
parser = configparser.ConfigParser()
parser.read("./urls.conf")

UPBIT_URL = parser.get("APIURL", "UPBIT")
BITHUMB_URL = parser.get("APIURL", "BITHUM")
KORBIT_URL = parser.get("APIURL", "KORBIT")
