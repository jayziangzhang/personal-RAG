# Great Wall Motors — High-Frequency EOL Data Acquisition Platform

## Project Background

This project delivered a high-frequency End-of-Line (EOL) data acquisition and processing platform for Great Wall Motors. EOL refers to the final inspection and testing stage of an automotive production line: before a vehicle leaves the line, it passes through a series of tests covering current, voltage, pressure, temperature, equipment status, and test results.

Customer requirement: the EOL Testing System sends one test message every 100 ms over HTTP, and each message contains more than 70 key-value fields. The platform must reliably receive, buffer, organize, and store this stream, and ultimately produce test results and visual reports.

The core engineering problem is not simple HTTP ingestion but the combination of: high-frequency data intake, load leveling (peak shaving), asynchronous processing, temporary data caching, transformation of raw data into stable data, and final report calculation.

## Pain Points

Pain point 1 — high message frequency. Devices send a message every 100 ms. Writing each message directly to the database on receipt leads to slow database writes, blocked HTTP requests, device upload timeouts, and data loss.

Pain point 2 — one test is not one message. A complete EOL test consists of many raw data messages. A single message only represents the state at one moment and cannot represent the full test result. Raw data must be processed and consolidated into Stable EOL Testing Data before persistence.

Pain point 3 — different pipeline stages need different queues. The system uses four queues, each with a distinct responsibility: Q1 holds Raw EOL Testing Data, Q2 holds Tag + Timestamp, Q3 holds Stable EOL Testing Data, and Q4 holds Calculation Task Numbers. Separate queues give each stage a clear responsibility and make the pipeline easy to extend.

## Architecture

End-to-end pipeline (left to right):

```
EOL Testing System --HTTP--> Gin REST API --> RabbitMQ Q1 (raw data)
  --> Redis Writer (Docker) --write--> Redis (in-memory raw/current test data)
  Redis Writer --flag==true--> RabbitMQ Q2 (tag + timestamp)
  --> Redis Reader (Docker) --read by tag--> Redis
  Redis Reader --> RabbitMQ Q3 (stable data) --> MongoDB Writer --> MongoDB
  MongoDB Writer --end_test==true--> RabbitMQ Q4 (task number)
  --> Calculator --query by task number--> MongoDB
  Calculator --> Flask Web API --> Frontend / Upper-Level System
```

## Data Flow

### Step 1 — EOL device sends data

The EOL Testing System sends one message every 100 ms over HTTP. Each message contains more than 70 key-value fields, including VIN, Tag, Timestamp, Temperature, Pressure, Current, Voltage, Test Result, Flag, and End Test.

### Step 2 — Gin web server receives data

The backend implements a RESTful API with Go and Gin. Gin is a lightweight Go web framework, and Go's lightweight goroutines let the API layer handle many concurrent HTTP requests efficiently, which suits high-frequency ingestion. On receipt, Gin does not write to the database; it publishes the message to RabbitMQ.

### Step 3 — RabbitMQ Q1 (Raw EOL Testing Data Queue)

Q1 stores the raw messages exactly as the devices sent them. RabbitMQ provides load leveling, asynchronous decoupling, protection of the API from slow database writes, and ordered queue-based processing. After publishing to Q1, the API returns the HTTP response immediately.

### Step 4 — Redis Writer consumes Q1

Redis Writer is an independent Docker service that consumes raw data from Q1 and performs two tasks. First, it writes the raw/current testing data into Redis, an in-memory store used to hold data for tests currently in progress, keyed by tag (for example tag:12345 mapping to VIN, timestamp, temperature, pressure, current, flag, end_test, and other fields). Second, it checks the flag field of each message; when flag == true, the message must enter the next processing stage, so Redis Writer publishes the tag and timestamp to RabbitMQ Q2.

### Step 5 — RabbitMQ Q2 (Tag + Timestamp Queue)

Q2 carries only tag and timestamp, never the full payload. It acts as an index/trigger queue telling Redis Reader which tag to read from Redis next. Benefits: very small messages, no repeated transmission of large payloads, preserved processing order, and precise tag-based lookup by Redis Reader.

### Step 6 — Redis Reader consumes Q2

Redis Reader is another independent Docker service. It consumes tag + timestamp from Q2, reads the corresponding test data from Redis by tag, applies business logic to consolidate the data into Stable EOL Testing Data, and publishes the stable data to RabbitMQ Q3.

### Step 7 — RabbitMQ Q3 (Stable EOL Testing Data Queue)

Q3 contains data that has passed through the full preprocessing chain: raw data in Q1, written to Redis by Redis Writer, triggered by tag via Q2, then read and consolidated by Redis Reader. Summary rule: raw data enters Q1, stable data enters Q3.

### Step 8 — MongoDB Writer consumes Q3

MongoDB Writer consumes stable data from Q3 and writes it to MongoDB. MongoDB therefore stores Stable EOL Testing Data records, not individual raw partial messages. MongoDB fits this workload because EOL records have many fields with a flexible structure, and each test record maps naturally to a document.

### Step 9 — end_test triggers Q4

MongoDB Writer checks the end_test field. When end_test == true, the test session is complete, and MongoDB Writer generates a calculation task. It does not re-send the full data; it publishes only the test/task number to RabbitMQ Q4.

### Step 10 — Calculator consumes Q4

Calculator consumes task numbers from Q4, retrieves the complete stable test record from MongoDB by test number, and computes PASS/FAIL results, test duration, KPIs, statistics, and report data.

### Step 11 — Flask Web API and dashboard

Calculation results are exposed through a Flask Web API to the frontend and upper-level systems. The frontend queries Flask over HTTP to display completed test data, production statistics, KPIs, visual reports, and management summaries. Managers see finished test results, never intermediate raw data.

## Component Responsibilities

- Gin Web Server: receives HTTP requests, performs basic validation, publishes raw data to RabbitMQ Q1. No heavy computation, no direct database writes.
- RabbitMQ: asynchronous decoupling, load leveling, staged queue processing. Q1 = Raw EOL Testing Data; Q2 = Tag + Timestamp; Q3 = Stable EOL Testing Data; Q4 = Calculation Task Number.
- Redis Writer (independent Docker service): consumes Q1 raw data, writes raw/current testing data to Redis, evaluates the flag field, and on flag == true publishes tag + timestamp to Q2.
- Redis: in-memory database serving as temporary data cache and running-state store, supporting fast tag-based reads of current test data. It is not the system of record.
- Redis Reader (independent Docker service): consumes Q2 tags, reads data from Redis by tag, consolidates it into stable testing data, and publishes to Q3.
- MongoDB: persistent store for Stable EOL Testing Data, complete test records, and historical traceability.
- MongoDB Writer: consumes Q3, writes to MongoDB, evaluates end_test, and on end_test == true publishes a task number to Q4.
- Calculator: consumes Q4, fetches data from MongoDB by task number, and computes test results, KPIs, and report data.
- Flask Web API: query interface for the frontend and upper-level systems, returning precomputed test results and visualization data.

## Design Rationale

Go + Gin for ingestion: Go's lightweight goroutine model handles high-concurrency HTTP efficiently, and Gin is a high-performance, developer-friendly REST framework, making the pair well suited to industrial data-acquisition APIs.

RabbitMQ in addition to Gin: Gin solves request-level concurrency (accepting the HTTP traffic); RabbitMQ solves processing-level decoupling (what happens when downstream cannot keep up). Direct database writes would let a slow database block the API; queued messages let the API return quickly even when downstream services or databases slow down.

Role of Redis: an in-memory temporary store for raw/current testing data. Redis Writer stores raw data into Redis; Redis Reader retrieves it by tag to reconstruct stable testing records.

Location of business logic: business logic lives in the Redis Writer and Redis Reader Go services, not inside Redis. Redis serves purely as a fast in-memory data store.

Q2 carries only tag + timestamp: full messages exceed 70 key-value fields; a lightweight index message avoids re-transmitting large payloads. The full data is already in Redis, so Redis Reader retrieves it by tag.

Definition of Stable EOL Testing Data: the processed, reconstructed test record generated from raw messages by the Redis Writer / Redis Reader stages — stable enough for persistence and downstream calculation.

MongoDB content and choice: MongoDB stores stable records from Q3, not raw messages from Q1. The document model suits semi-structured records with many flexible key-value fields and avoids rigid schema migrations as fields evolve.

Calculation gated on end_test == true: final KPIs and results are only meaningful after a complete test session; intermediate data cannot represent the final outcome.

Q4 carries only the task number: the full stable record is already persisted in MongoDB, so the Calculator only needs to know which test to compute and fetches the data itself.

Architectural highlight: the pipeline splits high-frequency processing into decoupled asynchronous stages — raw data ingestion, Redis-based temporary storage, tag-based retrieval, stable data generation, MongoDB persistence, calculation trigger, and dashboard reporting — with RabbitMQ decoupling each stage so a slow stage never blocks the whole system. Redis provides fast temporary data access, making the platform scalable and reliable for high-frequency industrial data.

## Summary

The platform uses Go and Gin for high-frequency EOL data ingestion, RabbitMQ for multi-stage asynchronous processing, Redis Writer and Redis Reader for transforming raw testing data into stable testing data, MongoDB for stable data persistence, and a Calculator service that produces final results and reports once the end_test signal is received, exposed to consumers through a Flask Web API.
