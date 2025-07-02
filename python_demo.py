import os
import json

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from pyflink.common import Configuration, Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.connectors import DeliveryGuarantee
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema
from pyflink.common import WatermarkStrategy

import os
import time
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay



# Verzeichnis für Export
ordner = "/opt/flink/"
os.makedirs(ordner, exist_ok=True)

# Flink-Konfiguration mit Kafka-Connector
config = Configuration()
config.set_string(
    "pipeline.jars",
    "file:///opt/flink/lib/flink-sql-connector-kafka-1.17.2.jar"
)

env = StreamExecutionEnvironment.get_execution_environment(configuration=config)
env.set_parallelism(4)

# Kafka-Quelle konfigurieren
source = KafkaSource.builder() \
    .set_bootstrap_servers("my-kafka:9092") \
    .set_topics("input2") \
    .set_group_id("flink-group") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Source"
)

mapped_stream = stream.map(
    lambda msg: f"{msg}",
    output_type=Types.STRING()
)

# Kafka-Daten sammeln
result = mapped_stream.execute_and_collect()

log = EventLog()

while True:

    # baue aus neuer Nachricht LOG Datei, die von pm4py eingelesen werden kann

    ##############################################################

    # Nur ein Trace (JSON-Liste von Events) einlesen

    for i in range (5):
        raw_msg = next(result)
        event_list = json.loads(raw_msg)  # Erwartet: JSON-Liste von Event-Dictionaries

        # Umwandlung in PM4Py EventLog
        trace = Trace([Event(e) for e in event_list])
        log.append(trace)

    # Export als XES
    xes_datei = os.path.join(ordner, "eventlog.xes")
    xes_exporter.apply(log, xes_datei)

    #############################################################

    # 📥 Modell laden (PNML)
    net, initial_marking, final_marking = pnml_importer.apply("/opt/flink/modell.pnml")

    time.sleep(2)

    xes_path = "/opt/flink/eventlog.xes"

    # 📥 Log laden (XES)
    log = xes_importer.apply(xes_path)

    # 🔍 Conformance Checking
    replay_result = token_replay.apply(log, net, initial_marking, final_marking)

    # 📊 Ergebnisse
    for i, res in enumerate(replay_result):
        print(f"\nTrace {i+1}:")
        print(f"  Fitness:           {res['trace_fitness']}")
        print(f"  Consumed Tokens:   {res['consumed_tokens']}")
        print(f"  Missing Tokens:    {res['missing_tokens']}")
        print(f"  Produced Tokens:   {res['produced_tokens']}")
        print(f"  Remaining Tokens:  {res['remaining_tokens']}")
