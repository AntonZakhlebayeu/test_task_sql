* Design and implement a database that can store the following objects:
* Grid - That stores the list of TSO/ISOs. You can use Grid1, Grid2 and Grid3 as
the entries.
* Grid Regions - Has a many-to-one relation with Grid. Use Region1, Region2 and
Region3 as the entries for each Grid.
* Grid Nodes - Has a many-to-one relation with Grid Regions. Use Node1, Node2
and Node3 as the entries for each Grid Region.
* Design a table (Measures) that can hold hourly timeseries values of Grid Nodes.
* This table should support storing the evolution of time series data.
Definition of evolution in this context (example) - At 9 AM, the Grid
Node can have a value of 100 for timestamp 11 PM of the following day.
The same Grid Node at 10 AM can have a value of 99 for the same
datetime 11 PM of the following day.
* Implement the Measures schema on a SQL database (PostgreSQL is an open-source
option, but you are free to use any database of your choice).
* Write a script to insert records for 1 week for all 3 Nodes including the hourly
evolution.
* Write an API that will accept a start datetime and end datetime. The API should return
the latest value for each timestamp in the date range.
* Write another API that will accept a start datetime, end datetime and collected
datetime. The API should return the value corresponding to the collected datetime for
each timestamp in the date range.


## 1. How to Use This Data Model to Insert Measurement Data for Grid
### To insert measurement data into this model, you would:
Identify the target Grid Node. Each measurement must be associated with a specific grid_node_id.
Insert time-series data into the measures table
For each prediction/measurement, insert:
```
grid_node_id: The node being measured
timestamp: The future time the prediction applies to ("2025-07-18 14:00:00")
collected_at: When the prediction was made ("2025-07-17 09:00:00")
value: The predicted/measured value
```
### Example SQL:
```sql
INSERT INTO measures (grid_node_id, timestamp, collected_at, value)
VALUES (1, '2025-07-18 14:00:00', '2025-07-17 09:00:00', 98.7);
```
### Handle Evolution
To update a prediction for the same timestamp, insert a new row with a later collected_at time.
Example: At 10 AM, update the prediction for 2 PM:

```sql
INSERT INTO measures (grid_node_id, timestamp, collected_at, value)
VALUES (1, '2025-07-18 14:00:00', '2025-07-17 10:00:00', 99.1);
```

## 2. Benefits of Timeseries Evolution
### Historical Tracking
Stores how predictions change over time (e.g., a 2 PM forecast made at 9 AM vs. 11 AM).
Enables analysis of prediction accuracy by comparing early vs. late forecasts.

### Auditability

Full traceability of who changed a prediction and when.

### Temporal Queries

Answer questions like:
"What did we predict for 2 PM at 9 AM yesterday?"
"How did our predictions for tomorrow evolve today?"

### Rollback Capability

Reconstruct the state of predictions at any past time.

## 3. API Performance Impact (1 Week vs. 1 Year of Data)
### Potential Issues:

#### Query Speed

Without optimization, queries like get_latest_measures could slow down as the table grows (e.g., from ~500 rows/week to ~26,000 rows/year per node).

#### Indexing

The current indexes ((grid_node_id, timestamp, collected_at DESC)) are good but may need partitioning for very large datasets.

### Solutions to Scale:

#### Query Optimization

Ensure queries use indexes (check with EXPLAIN ANALYZE).

Example: The get_latest_measures query already filters by timestamp range and uses collected_at DESC.

#### Data Partitioning

Partition the measures table by time ranges (e.g., monthly) to reduce scan size.

```sql
CREATE TABLE measures_2025_07 PARTITION OF measures
  FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
```

#### Caching

Cache frequent queries (e.g., latest values for the current day) in Redis.

#### Archiving

Move older data (e.g., >1 year) to cold storage or a data warehouse.

### API Changes Needed:

* Pagination for large date ranges (e.g., ?start=2025-01-01&end=2025-12-31&limit=1000).

* Asynchronous endpoints for heavy queries (e.g., /api/reports/yearly-summary).

### Summary
Inserting Data: Map measurements to grid_node_id and track evolution via (timestamp, collected_at).

Evolution Benefit: Enables temporal analysis and auditability.

Scaling API: Optimize queries, partition data, and add caching/pagination.

This model balances flexibility for time-series analysis with scalability for production use.
