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
