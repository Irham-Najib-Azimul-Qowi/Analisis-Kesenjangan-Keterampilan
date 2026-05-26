# -*- coding: utf-8 -*-
"""
Script to pre-fetch Aiven Kafka data and save it as a local CSV cache.
This speeds up Streamlit dashboard rendering.
"""

import os
import json
import uuid
import time
import pandas as pd
from kafka import KafkaConsumer

print("==========================================================")
print("🚀 PRE-FETCHING KAFKA DATA FOR STEAMILIT OFFLINE CACHE 🚀")
print("==========================================================")

KAFKA_BROKER = "kafka-90a3cd4-cejors-676945.g.aivencloud.com:28174"
TOPIC_NAME = "unified_jobs"
CACHE_FILE = "cached_data.csv"

CA_FILE = "ssl/ca.pem"
CERT_FILE = "ssl/service.cert"
KEY_FILE = "ssl/service.key"

random_group_id = f"fetch-group-{uuid.uuid4().hex[:8]}"

try:
    print("-> Connecting to Aiven Kafka Cloud broker...")
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        security_protocol="SSL",
        ssl_cafile=CA_FILE,
        ssl_certfile=CERT_FILE,
        ssl_keyfile=KEY_FILE,
        auto_offset_reset='earliest', 
        enable_auto_commit=False,
        group_id=random_group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    assigned_partitions = []
    start_time = time.time()
    
    while not assigned_partitions:
        consumer.poll(timeout_ms=1000)
        assigned_partitions = list(consumer.assignment())
        if not assigned_partitions:
            print("   -> Waiting for partition assignments...")
            time.sleep(1)
        if time.time() - start_time > 15:
            print("   ⚠️ Partition allocation timed out.")
            break
            
    if not assigned_partitions:
        print("❌ Failed to get partitions.")
        consumer.close()
        exit(1)
        
    print(f"✅ Connected to partitions: {[tp.partition for tp in assigned_partitions]}")
    end_offsets = consumer.end_offsets(assigned_partitions)
    
    records = []
    poll_start_time = time.time()
    
    while True:
        all_completed = True
        for tp in assigned_partitions:
            if consumer.position(tp) < end_offsets[tp]:
                all_completed = False
                break
                
        if all_completed:
            print("✅ Reached the end offset of all partitions!")
            break
            
        msg_pack = consumer.poll(timeout_ms=2500)
        if msg_pack:
            batch_count = 0
            for tp, messages in msg_pack.items():
                batch_count += len(messages)
                for message in messages:
                    records.append(message.value)
            print(f"   -> Consumed {batch_count} messages (Total so far: {len(records)})...")
        else:
            print("   -> Waiting for next segment load...")
            time.sleep(1)
            
        if time.time() - poll_start_time > 120:
            print("   ⚠️ Maximum fetch timeout of 2 minutes reached.")
            break
            
    consumer.close()
    
    if records:
        df = pd.DataFrame(records)
        df.to_csv(CACHE_FILE, index=False)
        print(f"🎉 SUCCESS: Saved {len(df)} records into '{CACHE_FILE}'!")
    else:
        print("⚠️ No messages were fetched.")
        
except Exception as e:
    print(f"❌ Error occurred during Kafka consume: {e}")
