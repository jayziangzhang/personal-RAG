# Swire Coca-Cola — Edge-Based Energy Management Platform

## Project Background

Swire Coca-Cola has sustainability goals aligned with carbon-reduction initiatives and internal ESG targets. Energy consumption had become one of the highest operating costs across its manufacturing plants. Although factories already collected data from PLCs and utility meters, the information was fragmented and difficult to analyze, making energy-optimization opportunities hard to identify.

The project objective was to build an edge-based energy management platform capable of collecting, calculating, and visualizing production and energy data in real time.

## Pain Points

### Pain Point 1 — Heterogeneous PLC vendors

Different production lines used PLCs from different vendors (Siemens, Mitsubishi, and others such as Rockwell and Omron), and each PLC exposed data differently.

### Pain Point 2 — Heterogeneous communication protocols

Lines communicated over different industrial protocols, including OPC UA, Siemens S7, and Modbus TCP. Every production line therefore required a different integration method, and no unified data interface existed.

### Pain Point 3 — Production data and energy data were disconnected

The PLC layer knew production output (for example 50,000 bottles produced in a day) but not energy usage; the utility meters knew consumption (for example 1,200 kWh in a day) but not output. Neither side alone could compute Electricity per Bottle — the metric at the core of the project's business value.

### Pain Point 4 — No unified visualization

Each PLC had its own HMI screens and each meter its own vendor software, with no unified dashboard.

## Edge vs Cloud Rationale

This is the project's central architectural decision.

Bandwidth cost: industrial equipment continuously generates telemetry. Uploading every sensor value to the cloud would significantly increase bandwidth and cloud storage costs. Raw data was therefore processed locally, and only aggregated results or KPIs were uploaded when necessary — the design uploads aggregates, not nothing.

Low latency: the project focused on energy management rather than real-time machine control, but local processing still gave much lower latency for dashboards, KPI calculation, and alarms. For latency-sensitive industrial scenarios such as blast furnaces or high-speed production lines, milliseconds matter, and the same Siemens Edge Platform can be reused for those applications.

Data security: manufacturing data is valuable operational data. Many customers prefer keeping production data inside the factory network instead of continuously transmitting raw data to public cloud services. Edge computing reduces external exposure while satisfying internal IT security policies.

Offline capability: if the factory's external network fails, the edge platform continues to collect data, calculate KPIs, and store results locally, then synchronizes after connectivity is restored.

## System Architecture

Data path (left to right):

```
PLCs + Energy Meters (electricity/water)
  --OPC UA / S7 / Modbus TCP-->
Siemens Industrial Edge Runtime:
  Data Acquisition → Data Normalization → Local Storage → Asset Model
  → KPI Calculation → Node-RED Dashboard + REST API → Browser Visualization
```

## Asset Model

The asset model maps raw PLC addresses to a business-oriented hierarchy. Instead of referencing a raw address such as DB100.DBW0, the model organizes equipment, energy sources, and sensors into a unified structure, for example: Filling Line 1 → Bottle Counter → Power Meter → Water Meter → Steam Meter.

KPI calculations then reference business entities ("Line 3 → Electricity Meter") rather than PLC addresses. This decouples analytics from the control layer: if a PLC address changes, dashboards and KPI logic remain unchanged.

## Data Flow

PLC → Industrial Protocol → Edge Runtime → Data Acquisition → Tag Normalization → Local Database → Asset Model → KPI Engine → Node-RED Dashboard → Browser.

Tag normalization converts raw PLC tags from different vendors and protocols into a unified business-oriented data model. Beyond mapping tag names to standardized names, it also normalizes data types, units, timestamps, and status values, allowing the dashboard, KPI engine, and APIs to work independently of the underlying PLC implementation.

## KPI Definitions

- Electricity per Bottle = Electricity (kWh) / Bottle Count
- Water per Case = Water Consumption / Number of Cases
- Energy Intensity = Total Energy / Production Output
- Daily Consumption = Current reading − Previous day's reading
- Year-over-Year (YoY) = (Current Month − Same Month Last Year) / Same Month Last Year

Industrial energy KPIs are deliberately simple ratio and delta formulas; the engineering value lies in unifying the data sources that feed them.

## Data Quality

Shop-floor data is imperfect, so the platform performs baseline quality processing before KPI calculation: outlier filtering, missing-data handling during communication interruptions, deduplication, and timestamp alignment. Standardization and quality checks keep KPI results reliable.

## Historical Data Storage

Raw data is stored first on the edge device for real-time analysis and short-term historical queries. KPIs and aggregated results are retained for long-term trend analysis and can be synchronized to enterprise systems on demand.

## Responsibilities

Main focus areas: edge application development, data acquisition, KPI calculation logic, dashboard customization with Node-RED, JavaScript template customization, REST APIs, and Docker deployment.

## Design Rationale

Versus SCADA: SCADA focuses on machine operation and monitoring; this platform focuses on energy analytics across multiple production lines, reusing production data but adding higher-level KPI calculation and visualization.

Versus MES: MES manages production execution, not energy optimization. The MES knows production; the energy platform knows production efficiency. The responsibilities are distinct.

Node-RED: visual flow programming significantly reduced dashboard development time while still allowing JavaScript customization for complex UI components.

Docker: containerization simplified deployment, version management, and updates across different factories while ensuring a consistent runtime environment.

Not connecting PLCs directly to a dashboard: the intermediate layers provide data normalization, KPI calculation, the asset model, local caching, access control, and APIs — none of which a PLC provides.

Asset model necessity: it prevents business logic from binding to PLC addresses, so address changes never break the dashboard.

Cloud database role: edge-first processing does not exclude cloud storage; the cloud serves long-term historical analysis, and industrial deployments typically use this hybrid architecture.

Sampling rates: acquisition frequency depends on the signal — high-frequency sensor data around 100 ms–1 s, energy meters typically every few seconds, KPI aggregation every minute or hour. There is no single fixed rate.

KPI computation location: KPIs are computed on the edge device, not in the PLC. PLC CPU resources are reserved for control logic; running analytics on the Edge IPC avoids impacting real-time control performance.
