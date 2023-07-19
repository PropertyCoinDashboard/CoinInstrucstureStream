import configparser

"""
setting 
"""
parser = configparser.ConfigParser()
parser.read("./urls.conf")

UPBIT_URL = parser.get("APIURL", "UPBIT")
BITHUMB_URL = parser.get("APIURL", "BITHUM")
KORBIT_URL = parser.get("APIURL", "KORBIT")
BIT_TOPIC_NAME = parser.get("TOPICNAME", "BIT_TOPIC_NAME")
ETHER_TOPIC_NAME = parser.get("TOPICNAME", "ETHER_TOPIC_NAME")
OTHER_TOPIC_NAME = parser.get("TOPICNAME", "OTHER_TOPIC_NAME")
