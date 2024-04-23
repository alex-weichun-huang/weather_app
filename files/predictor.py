from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, max, min, count
from pyspark.sql.types import StructType, StructField, StringType, DateType, DoubleType, IntegerType
from pyspark.sql.functions import date_add, month, year, dayofmonth
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassificationModel
from config import CONFIG


# get the configs for Kafka
brokers = []
for i in range(len(CONFIG["kafka"]["host_name"])):
    brokers.append(f'{CONFIG["kafka"]["host_name"][i]}:{CONFIG["kafka"]["port_num"][i]}')


# get the configs for Cassandra
host_port_pairs = []
for i in range(len(CONFIG["cassandra"]["host_name"])):
    host_port_pairs.append ( (CONFIG["cassandra"]["host_name"][i], CONFIG["cassandra"]["port_num"][i]))
replication_factor = CONFIG["cassandra"]["replication_factor"]


# get the configs for Spark
shuffle_partitions = CONFIG["spark"]["shuffle_partitions"]
awaitTermination = CONFIG["spark"]["awaitTermination"]
processingTime = CONFIG["spark"]["processingTime"]


# Create a SparkSession
spark = (SparkSession.builder
         .appName("weather-app")
         .config("spark.sql.shuffle.partitions", shuffle_partitions)
         .config("spark.ui.showConsoleProgress", False)
         .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0,"
                                        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.2,")
         .getOrCreate())


# initialize Kafka stream
stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", ",".join(brokers))
    .option("subscribe", "weather-stations-json")
    .option("startingOffsets", "earliest")
    .load()
)


# define schema 
schema = StructType([
    StructField("station", StringType()),
    StructField("date", DateType()),
    StructField("degrees", DoubleType()),
    StructField("raining", IntegerType())
])


# get features
df = stream.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
yesterday = df.select("station", date_add("date", -1).alias("date"), "degrees", "raining").withColumnRenamed("degrees", "prev1_degrees").withColumnRenamed("raining", "prev1_raining")
two_days_ago = df.select("station", date_add("date", -2).alias("date"), "degrees", "raining").withColumnRenamed("degrees", "prev2_degrees").withColumnRenamed("raining", "prev2_raining")
features = (
    df.withColumn("year", year("date"))
    .withColumn("month", month("date"))
    .withColumn("day", dayofmonth("date"))
    .join(yesterday, ["station", "date"])
    .join(two_days_ago, ["station", "date"]).repartition(1)
)


# get predictions
dt_model = DecisionTreeClassificationModel.load("/files/model/dt_model")
assembler = VectorAssembler(inputCols=["degrees", "raining", "year", "month", "day", "prev1_degrees", "prev1_raining", "prev2_degrees", "prev2_raining"], outputCol="features")
features = assembler.transform(features)
predictions = dt_model.transform(features).select("station", "year", "month", "day", "prediction")


# creat a connection to Cassandra
cluster = Cluster(host_port_pairs)
session = cluster.connect()
print("\n\n\nConnected to Cassandra!")


# create a keyspace in Cassandra
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS weather
    WITH REPLICATION = {{
        'class': 'SimpleStrategy',
        'replication_factor': {replication_factor}
    }}
""")


# create a table in Cassandra
session.set_keyspace("weather")
session.execute("""
    CREATE TABLE IF NOT EXISTS weather.predictions (
        station TEXT, 
        year INT,
        month INT,
        day INT,
        prediction DOUBLE, 
        PRIMARY KEY(station, year, month, day)
)""")


# write the predictions to Cassandra
query = (
    predictions.writeStream
    .format("org.apache.spark.sql.cassandra")
    .option("keyspace", "weather")
    .option("table", "predictions")
    .outputMode("append")
    .option("spark.cassandra.connection.host", ",".join(CONFIG["cassandra"]["host_name"]))
    .option("checkpointLocation", "/files/checkpoints/predictions")
    .trigger(processingTime=processingTime)
    .start()
)
query.awaitTermination(awaitTermination)
query.stop()