from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaError, KafkaException, ProduceError
from setting.create_log import log


logger = log()


def new_topic_initalization(
    topic: str, partition: int, replication_factor: int
) -> None:
    conf = {"bootstrap.servers": "kafka1:9092, kafka2:9093, kafka3:9094"}
    a = AdminClient(conf=conf)

    new_topics = [
        NewTopic(topic, num_partition=partition, replication_factor=replication)
        for topic, partition, replication in zip(topic, partition, replication_factor)
    ]
    fs = a.create_topics(new_topics=new_topics)

    for topic, f in fs.items():
        try:
            f.result()
            print(f"Topic create -> {topic}")
        except (KafkaException, KafkaError, ProduceError) as e:
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                logger.error(f"Failed to create topic --> {topic}: {e}")
        finally:
            a.close()
