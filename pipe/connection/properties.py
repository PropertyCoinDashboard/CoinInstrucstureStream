import configparser
from pathlib import Path

path = Path(__file__).parent.parent
parser = configparser.ConfigParser()
parser.read(f"{path}/coin/core/config/urls.conf")

BTC_TOPIC_NAME: str = parser.get("TOPICNAME", "BTC_TOPIC_NAME")
ETH_TOPIC_NAME: str = parser.get("TOPICNAME", "ETHER_TOPIC_NAME")
OTHER_TOPIC_NAME: str = parser.get("TOPICNAME", "OTHER_TOPIC_NAME")

BTC_AVERAGE_TOPIC_NAME: str = parser.get("AVERAGETOPICNAME", "BTC_AVERAGE_TOPIC_NAME")
ETH_AVERAGE_TOPIC_NAME: str = parser.get("AVERAGETOPICNAME", "ETHER_AVERAGE_TOPIC_NAME")


BTC_TOPIC_NAME: str = parser.get("TOPICNAME", "BTC_TOPIC_NAME")
ETH_TOPIC_NAME: str = parser.get("TOPICNAME", "ETHER_TOPIC_NAME")
