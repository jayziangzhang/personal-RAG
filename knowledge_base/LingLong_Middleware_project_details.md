# Linglong Tire — RFID Edge Middleware for MES Integration

## Project Background

The customer was Linglong Tire, one of China's leading tire manufacturers. The factory was highly automated: robots handled material transport, palletizing, loading, and unloading across the production lines. Each production line was equipped with multiple RFID readers that identified raw materials (rubber compounds, rims, and other components) before they entered manufacturing.

When a robot delivered a pallet onto the conveyor, the RFID reader scanned the tag and sent the material information to the factory's Manufacturing Execution System (MES) for inventory tracking and production management. The process worked in principle, but the workshop had several operational pain points.

## Pain Points

### Pain Point 1 — MES was too centralized

The factory-wide MES covered production scheduling, inventory, quality management, equipment management, reporting, and manufacturing execution, and was maintained by an external software vendor. Consequences: shop-floor engineers could not customize its behavior; even small logic changes required modifying the MES, with long approval processes and high deployment risk; and maintenance staff only needed to monitor RFID devices, not the entire factory. Using the MES to solve workshop-level problems was too heavyweight.

### Pain Point 2 — Duplicate RFID scans

RFID readers occasionally produced duplicate scans. When a pallet vibrated while passing a reader, the same tag could be scanned several times within a few seconds, producing repeated "Material A" events for a single physical pallet. Forwarding every scan directly to the MES inflated inventory counts and required manual correction.

### Pain Point 3 — Difficult device maintenance

The workshop had over one hundred RFID readers. When a reader stopped communicating, engineers had no centralized tool to determine which production line was affected, whether the TCP connection had dropped, whether the device had failed, whether communication had timed out, or whether automatic reconnection was working. Faults were diagnosed by physically inspecting devices on the floor.

## Solution

Instead of modifying the MES, an Edge Middleware Application was developed and deployed on an industrial PC inside the workshop, sitting between the RFID devices and the MES.

Middleware responsibilities: managing TCP connections to RFID readers, receiving XML messages, preprocessing data, removing duplicate scans, validating incoming messages, monitoring device health, logging device events locally, and forwarding only clean inventory events to the MES. The workshop could customize its own workflow without touching the factory-wide MES.

## Architecture

Data path (left to right):

```
RFID Readers + PLC Devices --TCP/XML--> Edge Middleware --inventory events only--> MES
```

Edge Middleware internal modules: TCP Connection Manager, XML Parser, FIFO Message Queue, Validation Engine, Deduplication Engine, Heartbeat Monitor, Auto Reconnection, Local Log Service, and Monitoring Dashboard.

## End-to-End Data Flow

### Step 1 — RFID scans material

A robot places raw material on the conveyor; the RFID reader scans the tag.

### Step 2 — RFID sends XML over TCP

Each reader maintained a persistent TCP connection with the middleware and transmitted scan events as XML messages, for example a Scan element containing ReaderID (RFID-05), TagID (ABC123456), and Timestamp (2026-07-01T10:15:20). TCP was chosen because industrial devices require low-latency, persistent communication rather than stateless HTTP requests. XML was used because it was the protocol supported by the Siemens RFID hardware.

### Step 3 — TCP connection management

The middleware maintained a dedicated TCP connection per reader and continuously monitored connection status, communication timeouts, device availability, and heartbeat messages. On connection loss, it automatically reconnected using an exponential backoff strategy, avoiding excessive reconnect attempts while restoring communication quickly.

### Step 4 — Message queue

Received XML messages were placed into a FIFO message queue. Benefits: buffering bursts when many readers scanned simultaneously, preventing business logic from blocking TCP communication, and decoupling device communication from downstream processing.

### Step 5 — Data validation

Worker processes consumed the queue and validated messages for missing fields, invalid XML format, invalid RFID tags, empty messages, and timestamp validity. Invalid messages were written to local logs instead of being forwarded.

### Step 6 — Deduplication

Duplicate scans were removed before reaching the MES. If the same Reader ID + RFID Tag combination appeared multiple times within a configurable 5-second time window, only the first event was forwarded and subsequent duplicates were discarded. The deduplication key was Reader ID + RFID Tag + Time Window. This prevented inventory overcounting from repeated scans. The window was configurable rather than hardcoded, so different production lines could tune sensitivity without changing the application.

### Step 7 — Event classification

After preprocessing: valid inventory events were forwarded to the MES; duplicate events were discarded; device errors were logged locally and shown on the dashboard; communication failures triggered alarms for maintenance personnel.

### Step 8 — MES updates inventory

The MES received only clean business events such as Material Arrived and Material Removed. It never saw duplicate scans, communication retries, or hardware logs, significantly reducing unnecessary processing inside the MES.

## Monitoring Dashboard

A lightweight web-based dashboard for workshop operators displayed RFID online/offline status, heartbeat status, TCP connection status, device reconnection history, local logs, alarm notifications, reader configuration, and a production line overview. Maintenance engineers could identify faults across the workshop from a single interface instead of checking devices individually.

## Responsibilities

Developed the edge middleware on Siemens Industrial Edge technology; implemented TCP/XML communication with RFID devices; managed asynchronous message processing with a FIFO queue; designed data validation and configurable deduplication logic ahead of MES forwarding; implemented heartbeat monitoring and automatic reconnection for device reliability; built local logging and device monitoring for workshop maintenance engineers; supported deployment and testing on industrial PCs in the production workshop.

## Project Results

The middleware eliminated duplicate RFID scans before they reached the MES, improved inventory data accuracy, reduced manual troubleshooting time through centralized device monitoring, enabled workshop-specific customization without modifying the factory-wide MES, improved communication reliability via heartbeat monitoring and automatic reconnection, and reduced the workload and risk of changing the core MES platform.

## Design Rationale

Edge middleware instead of modifying the MES: the MES is the factory's core production system, maintained by another vendor; any modification required lengthy approval, testing, and deployment and could affect the whole factory. The middleware isolated workshop-specific logic without impacting the core MES.

Message queue: buffers traffic spikes when many readers scan simultaneously, prevents TCP communication from being blocked by business processing, and decouples device communication from downstream logic, making the system easier to extend and maintain.

TCP instead of HTTP: industrial RFID devices need long-lived, low-latency communication; persistent TCP connections have lower overhead than repeatedly creating HTTP requests, making TCP better suited to real-time industrial communication.

XML instead of JSON: the Siemens RFID readers already communicated in XML; the middleware followed the device protocol rather than adding protocol conversion.

Offline detection: the middleware monitored heartbeat messages and TCP connection status; a reader missing heartbeats beyond the configured timeout was marked offline and surfaced on the dashboard.

Automatic reconnection: lost TCP connections were re-established with exponential backoff, avoiding excessive retries while restoring communication efficiently.

FIFO ordering: inventory events must preserve chronological order; FIFO guarantees that material arrival and departure events are processed in the sequence they occurred on the line.

Deduplication at the edge rather than in the MES: duplicate filtering is a device-level concern, not a business-level concern. Edge-side filtering reduces unnecessary traffic, lowers MES processing load, and allows workshop-specific rules without modifying the core production system.

MES unavailability: the middleware buffered validated events in the local message queue; when the MES connection recovered, queued events were replayed in order, preventing data loss while preserving event sequencing.
