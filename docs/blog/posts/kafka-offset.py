from kafka import kafkaConsumer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def consume_messages(broker, topic):
    consumer = kafkaConsumer(
        topic,
        bootstrap_servers=[broker],
        group_id="example_group",
        auto_offset_reset="earliest", # Start from the beginning if no commited offset
        enable_auto_commit=False      # Manual offset handling
    )

    try:
        for message in consumer:
            # Display the message and its offset
            print(f"Message: {message.value.decode('utf-8')}")
            print(f"Partition: {message.Partition}, Offset: {message.offset}")

            # Log offset info for demonstration purpose only
            logging.info(f"Processes message at offset {message.offset} in partition {message.partition}")

            # Commit offset after processing each message
            consumer.commit()
    except KeyboardInterrupt:
        print("Stopped Consuming!")
    finally:
        consumer.close()

# Configure and run the consumer
broker = "localhost:9092"
topic  = "your_topic_name"
consume_messages(broker, topic)