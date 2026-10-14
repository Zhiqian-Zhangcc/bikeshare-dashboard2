# CityRide Shared Bike Operations Command Center

An interactive Streamlit dashboard for a shared-bike operations manager. It turns historical hourly demand into a compact operating view for vehicle rebalancing and maintenance planning.

## Dataset

Source: [Bike Sharing Dataset on Kaggle](https://www.kaggle.com/datasets/marklvl/bike-sharing-dataset).

The data is a Washington D.C. Capital Bikeshare historical snapshot, aggregated at hourly level for 2011–2012. One row represents the aggregated bike-rental activity and weather conditions for one calendar hour; it is not an individual ride or station-level record.

## Decision and operational action

The intended decision-maker is the shared-bike operations manager. If the operations manager sees abnormally high demand in a time period, they will dispatch vehicles in advance and schedule maintenance resources, reducing the risk that no bikes are available during peak demand.

A dashboard is more useful than a one-off report because managers can repeatedly change the year, season, day type, and weather filters as daily operating conditions change. The view supports quick comparisons and repeatable decisions instead of a fixed, static conclusion.

## What the dashboard shows

The top KPIs are total rides, peak demand hour, and registered rider share. They provide the selected demand volume, the time that needs the earliest preparation, and the dominant customer base. The two supporting charts are the hourly demand profile (including a working-day versus weekend/holiday comparison when both are selected) and average demand by weather condition. These charts were selected because the EDA found meaningful hourly, day-type, and weather differences in demand.

Available filters are year, season, day type, and weather. Every filter updates both the KPIs and charts.

The dashboard intentionally does not show:

1. The raw hourly data table, because it is too dense for an operating screen and does not support rapid dispatch decisions.
2. Distribution charts for every weather variable, because they add analytical detail without directly improving the immediate rebalancing decision; the weather-condition demand comparison is more actionable.

## Data limitations and operating guidance

- Historical data covers only 2011–2012, so it should not be treated as a current demand forecast.
- Weather is represented by categorical severity codes, not a live weather forecast.
- The data has no station locations or real-time bike availability, so it cannot prescribe a specific station-level route.

In production, refresh the dashboard hourly. Managers should review it each morning, during severe weather, and before public holidays. A useful alert rule is: when rides in an hour exceed average demand by 20% for the same day type and weather condition, schedule additional vehicles.

## Run locally

From this folder:

```bash
uv run streamlit run app.py
```
