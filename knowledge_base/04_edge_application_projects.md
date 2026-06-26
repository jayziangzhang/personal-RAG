# Edge Application Projects (Siemens)

## Overview
Two of my most representative Siemens projects were edge-application builds on the Siemens Industrial Edge platform: a high-frequency data-acquisition platform for Great Wall Motors, and an energy-management platform for Swire Coca-Cola. Both share the same core pattern—pushing data acquisition and processing to the edge, close to the equipment—but they target different problems: real-time machine-health data at extreme sampling rates versus plant-wide energy visibility and sustainability.

## Great Wall Motors — High-Frequency Data Acquisition: Context
Great Wall Motors wanted to capture and analyze high-frequency vibration signals from production equipment in real time, to support equipment health monitoring and predictive maintenance. Traditional MES and SCADA systems are built for production management and typically sample at second- or even minute-level intervals, so they can't fully capture fast-changing signals like vibration or current waveforms. As a result, large volumes of critical transient data were simply discarded and unavailable for fault analysis or condition assessment. The customer needed a platform capable of ingesting on the order of a million data points per second, enabling real-time acquisition and analysis of high-frequency industrial data.

## Great Wall Motors — Solution & Architecture
I helped develop a high-frequency data-acquisition platform on Siemens Industrial Edge. The pipeline was:

```
PLC / Sensor
      ↓
 Edge Application
      ↓
   HTTP API
      ↓
 Redis Buffer
      ↓
  RabbitMQ
      ↓
MES / Data Platform
```

An edge application continuously acquired high-frequency vibration data from the equipment; a high-throughput HTTP service handled fast ingestion; Redis served as an in-memory buffering layer; RabbitMQ decoupled producers from consumers; and backend systems consumed the stream asynchronously, writing it into the enterprise data platform.

## Great Wall Motors — Technical Challenges & How I Solved Them
**High write pressure:** writing million-point-per-second data straight to a database makes the database the bottleneck. I used Redis for short-term caching, RabbitMQ for traffic shaping/peak shaving, and asynchronous persistence, avoiding excessive database connections and I/O during peaks. **Real-time reliability:** shop-floor networks occasionally jitter, so Redis acted as a temporary buffer, RabbitMQ provided message persistence, and a retry mechanism prevented data loss, keeping the acquisition pipeline stable. **Scalability:** equipment count and sampling rates vary widely between plants, so I used a modular edge-application design, standardized HTTP interfaces, and RabbitMQ's horizontal-scaling capability to make the solution easy to replicate to other production lines.

## Great Wall Motors — My Contribution & Outcomes
I was responsible for the edge-application development, the HTTP data-acquisition service, the Redis caching logic, the RabbitMQ messaging design, and system deployment and on-site testing, working with automation engineers on the equipment-side integration. The platform achieved acquisition of around one million data points per second, established a real-time high-frequency industrial-data architecture, supported vibration monitoring and downstream predictive-maintenance analysis, and laid the data foundation for later industrial-AI and equipment-health-management use cases.

## Swire Coca-Cola — Energy Management Platform: Context
Before this project, the plant's energy data relied on manual meter readings and Excel reports. Data was fragmented, real-time visibility was poor, energy anomalies were detected only after the fact, and there was no unified platform for visualization and analysis. The customer wanted a digital energy-management platform to cut costs and improve efficiency while supporting its carbon-neutrality and sustainability goals.

## Swire Coca-Cola — Solution
I developed an energy-management application on Siemens Industrial Edge. **Data acquisition:** it collected PLC, electricity-meter, water-meter, steam-meter, and compressed-air data into a unified energy data model. **KPI computation:** it automatically calculated electricity, water, and steam consumption per unit of output, plus overall energy-utilization efficiency, helping management evaluate production efficiency. **Visualization & analysis:** built with Node-RED and custom JavaScript, it provided real-time dashboards, trend analysis, energy-consumption rankings, peak/off-peak (time-of-use) electricity analysis, and automated report generation, with branded UI customized to the customer.

## Swire Coca-Cola — Example Insight, Outcomes & My Contribution
A concrete example: on one filling line, with output essentially stable, the platform showed electricity consumption per unit running persistently above the historical average. Investigation revealed excessive equipment standby/idle time driving up no-load energy use, and the customer adjusted its operating strategy accordingly. Overall, the platform delivered centralized energy-data management, real-time visual monitoring, and automated energy reporting—moving the customer from after-the-fact reporting to real-time monitoring and proactive analysis. Because it used a standardized asset model and a configurable dashboard architecture, it was successfully replicated to two additional plants. I was responsible for the energy-management application development, Node-RED flow design, KPI-calculation logic, dashboard development, data-visualization and reporting features, and on-site deployment and customer communication.
