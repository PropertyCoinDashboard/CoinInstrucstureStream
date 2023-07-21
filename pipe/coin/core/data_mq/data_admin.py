"""
KAKFA NEW TOPIC CREATE
"""
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaError, KafkaException, ProduceError
from coin.core.config.create_log import log

logger = log()


def new_topic_initialization(
    topic: str, partition: int, replication_factor: int
) -> None:
    """new topic create

    Args:
        topic (str): topicname
        partition (int): kafka partition
        replication_factor (int): replication in kafak partition
    """
    conf = {"bootstrap.servers": "kafka1:19092, kafka2:29092, kafka3:39092"}
    admin_clinet = AdminClient(conf=conf)

    new_topics = [
        NewTopic(topic, num_partitions=partition, replication_factor=replication)
        for topic, partition, replication in zip(topic, partition, replication_factor)
    ]
    create_topic = admin_clinet.create_topics(new_topics=new_topics)

    for topic, f in create_topic.items():
        try:
            f.result()
            print(f"Topic create -> {topic}")
        except (KafkaException, KafkaError, ProduceError) as error:
            if error.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                logger.error("Failed to create topic --> %s: %s", topic, error)
