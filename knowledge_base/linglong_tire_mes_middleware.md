# Ling Long Tire — MES Integration Middleware (Siemens)

## Context
Ling Long Tire operates a large number of automated production lines and warehouse-logistics systems. During raw-material loading, the plant uses Siemens RFID readers and barcode scanners to automatically identify material information and feed it into the MES for inventory management and production traceability. Three problems stood in the way. First, **protocol incompatibility**: the field RFID devices communicated over raw TCP sockets and transmitted data as XML, while the MES exposed only a standard business interface (HTTP API), so the devices couldn't talk to the MES directly. Second, **no device-layer visibility**: the MES tracks business data—material IDs, batch numbers, inbound records, production logs—but not whether an RFID reader is online, whether the network has dropped, whether a device rebooted, or when it last communicated, so operations staff had no view of equipment health. Third, **scan misreads**: in a complex industrial environment, RFID readers occasionally produce duplicate reads, unexpected-tag reads, missing tag data, or invalid code formats; if uploaded directly, these corrupt inventory records and break traceability. The customer needed a middleware layer to bridge devices and MES, provide device monitoring, and validate data before it reached the MES.

## Middleware Architecture
The middleware sat between the device layer and the business layer—connecting down to shop-floor equipment and up to the MES:

```
RFID Reader
      ↓ TCP / XML
 ┌─────────────────────────┐
 │   Middleware Platform   │
 │  • XML Parsing          │
 │  • Protocol Conversion  │
 │  • Device Monitoring    │
 │  • Heartbeat Tracking   │
 │  • Data Validation      │
 │  • Event Logging        │
 └─────────────────────────┘
      ↓ HTTP / REST
   MES System
```

It accepted TCP connections from the readers, parsed the XML payloads, converted and validated the data, and called the MES HTTP API—giving the previously incompatible device and business layers a reliable path to interoperate.

## Four Core Functions
**Device Monitoring** gave operations staff real-time visibility into equipment status—online state, last-communication time, current connection count, active alarms, and historical anomalies. The middleware maintained a device-state table, updating it whenever a device connected or sent a message, and surfaced device health through a web dashboard.

**Heartbeat Detection** caught dropped devices quickly. Readers sent periodic heartbeats; the middleware tracked the last heartbeat per device, and if none arrived within a configured window (e.g., 60 seconds) it automatically marked the device OFFLINE and raised an alarm—so operators no longer had to wait for the MES to throw an error before learning of a fault.

**Automated Data Validation** prevented bad data from reaching the MES through several rules: code-format validation (rejecting material IDs of abnormal length), duplicate-scan suppression (collapsing repeated reads of the same material within a few seconds into one to avoid double-counting inventory), null checks (blocking records missing required fields such as batch number), and illegal-tag filtering (dropping materials not belonging to the current work order). Only data that passed every check entered the MES.

**Production Data Synchronization** kept device-side data consistent with the MES, covering material loading, batch information, RFID read results, and inventory-change events. It was event-driven and real-time: an RFID read triggered middleware processing, an HTTP API call, and an MES update, all completing within seconds.

## Outcomes
Approximately 95% of material-identification and MES-reporting processes were automated through the RFID integration, significantly reducing manual scanning and data entry. Beyond that, the project delivered seamless device-to-MES integration, a unified device-monitoring platform, lower manual-entry workload, improved inventory-data accuracy, and faster detection of equipment faults.

## My Contribution
I was responsible for developing the middleware layer between shop-floor devices and the MES. My work included TCP communication handling, XML message parsing, protocol conversion, device-monitoring dashboards, heartbeat-detection logic, and automated data-validation workflows.
