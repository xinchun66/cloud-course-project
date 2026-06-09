from pyspark.sql import SparkSession


spark = SparkSession.builder.appName("WordCount").getOrCreate()

# Read sample text from OBS. Replace <BUCKET> with the path provided by the teacher.
lines = spark.sparkContext.textFile("s3a://<BUCKET>/sample.txt")

word_counts = (
    lines.flatMap(lambda line: line.split())
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False)
)

print("Top 10 words:", word_counts.take(10))

spark.stop()
