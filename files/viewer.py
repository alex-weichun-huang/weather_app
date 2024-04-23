from cassandra.cluster import Cluster
from config import CONFIG


# get the configs
host_port_pairs = []
for i in range(len(CONFIG["cassandra"]["host_name"])):
    host_port_pairs.append ( (CONFIG["cassandra"]["host_name"][i], CONFIG["cassandra"]["port_num"][i]))


# connect to Cassandra
cluster = Cluster(contact_points=host_port_pairs)
session = cluster.connect()
print("Connected to Cassandra!")


# TODO: play around with these queries !
session.set_keyspace("weather")
output = session.execute("""
    SELECT COUNT(*) FROM predictions;
""")
print("Number of rows in Cassandra:")
print(output.one().count)


# TODO: play around with these queries !
print("Data from Cassandra:")
pred_1 = session.execute("""
    SELECT * FROM predictions
    WHERE prediction = 1.0
    LIMIT 10
    ALLOW FILTERING;
""")
for row in pred_1:
    print(row)