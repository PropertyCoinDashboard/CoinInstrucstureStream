"""
KAKFA NEW TOPIC CREATE
"""

from pathlib import Path
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaError, KafkaException, ProduceError
from coin.core.util.create_log import log
from coin.core.setting.properties import BOOTSTRAP_SERVER

present_path = Path(__file__).parent.parent
logger = log(
    log_location=f"{present_path}/data_mq/log/kafka_topic_create.log",
    name="topic_create",
)


def new_topic_initialization(
    topic: str, partition: int, replication_factor: int
) -> None:
    """new topic create

    Args:
        topic (str): topicname
        partition (int): kafka partition
        replication_factor (int): replication in kafak partition
    """
    conf = {"bootstrap.servers": BOOTSTRAP_SERVER}
    admin_clinet = AdminClient(conf=conf)

    new_topics = [
        NewTopic(topic, num_partitions=partition, replication_factor=replication)
        for topic, partition, replication in zip(topic, partition, replication_factor)
    ]
    create_topic = admin_clinet.create_topics(new_topics=new_topics)

    for topic, f in create_topic.items():
        try:
            f.result()
            logger.info(f"Topic create -> {topic}")
        except (KafkaException, KafkaError, ProduceError) as error:
            if error.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                logger.error("Failed to create topic --> %s: %s", topic, error)


def delete_all_topics() -> None:
    """
    Delete all topics in the Kafka cluster.

    Parameters:
    - broker (str): The broker address, e.g., "localhost:9092"
    """

    # Initialize the Admin client
    conf = {"bootstrap.servers": BOOTSTRAP_SERVER}
    admin_client = AdminClient(conf=conf)

    # Fetch all topic metadata
    cluster_metadata = admin_client.list_topics(timeout=10)

    # Get all topic names
    all_topic_names = list(cluster_metadata.topics.keys())
    # Delete all topics
    deleted_topics_futures = admin_client.delete_topics(
        all_topic_names, operation_timeout=30
    )

    # Check the result of deletion
    for topic, future in deleted_topics_futures.items():
        try:
            future.result()  # The result itself is None
            print(f"Topic {topic} --> deleted successfully.")
        except Exception as e:
            print(f"Failed to delete topic {topic}: {e}")
