import pandas as pd
import json

from google.protobuf.json_format import MessageToJson

from google.analytics.data_v1beta.types import (
      DateRange,
      Dimension,
      Metric,
      RunReportRequest
  )

def getReport(property_id, start_date, client):
      
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="addToCarts"), 
            Metric(name="checkouts"),
            Metric(name="transactions"),
            Metric(name="totalRevenue"),
            Metric(name="sessions"),
            Metric(name="activeUsers")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date="today")],
    )
    response = client.run_report(request)

    json_str = MessageToJson(response._pb)
    data = json.loads(json_str)

    df = convertToDataFrame(data, property_id)
    
    return df

def convertToDataFrame(data, property_id):

    # Extract the dimension and metric headers
    dimension_headers = [header['name'] for header in data['dimensionHeaders']]
    metric_headers = [header['name'] for header in data['metricHeaders']]

    # Extract the data rows
    rows = []
    for row in data['rows']:
        row_values = [dim_value['value'] for dim_value in row['dimensionValues']]
        metric_values = [metric_value['value'] for metric_value in row['metricValues']]
        rows.append(row_values + metric_values)

    # Create a Pandas DataFrame
    df = pd.DataFrame(rows, columns=dimension_headers + metric_headers)
    df['property_id'] = property_id

    return df