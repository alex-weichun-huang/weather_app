import weather
from report_pb2 import Report
from config import CONFIG


from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import UnknownTopicOrPartitionError


# get the configs
num_partitions = int(CONFIG["kafka"]["num_partitions"])
replication_factor = int(CONFIG["kafka"]["replication_factor"])
brokers = []
for i in range(len(CONFIG["kafka"]["host_name"])):
    brokers.append(f'{CONFIG["kafka"]["host_name"][i]}:{CONFIG["kafka"]["port_num"][i]}')


# initialize admin client
admin_client = KafkaAdminClient(bootstrap_servers=brokers)
print("Admin client initialized")


# create topic and producer
try:
    admin_client.delete_topics(["weather-stations", "weather-stations-json"])
    print("Deleted topics successfully")
except UnknownTopicOrPartitionError:
    print("Cannot delete topic/s (may not exist yet)")


# create topics
print("Creating topic...")
admin_client.create_topics([NewTopic("weather-stations", num_partitions=num_partitions, replication_factor=replication_factor)])
admin_client.create_topics([NewTopic("weather-stations-json", num_partitions=num_partitions, replication_factor=replication_factor)])
producer = KafkaProducer(bootstrap_servers=brokers)


# Runs infinitely because the weather never ends
print("Producing weather data...")
for date, station_name, temp, raining in weather.get_next_weather(sleep_sec=0.1):
    
    
    # send to "weather-stations" using protobuf
    report = Report(date=date, station=station_name, degrees=temp, raining=raining)
    key = bytes(station_name, encoding="utf-8")
    producer.send("weather-stations", report.SerializeToString(), key=key)
    
    
    # send to "weather-stations-json" using json
    value = f'{{"date":"{date}","station":"{station_name}","degrees":{temp},"raining":{int(raining)}}}'
    producer.send("weather-stations-json", value.encode("utf-8"), key=key)


# Close producer
producer.close()
print("Producer closed")
