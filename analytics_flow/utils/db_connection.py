import json 
from sqlalchemy import create_engine
from io import StringIO 
import boto3
import time
import psycopg2

from analytics_flow.secrets.get_token import getSecret
from analytics_flow.resources.configs import DATA_SOURCE, RDS, AWS_ACCESS_ID, AWS_ACCESS_KEY

def pushToLake(df_data, name):
    bucket = 'etl-portfolio' # already created on S3
    csv_buffer = StringIO()
    df_data.to_csv(csv_buffer, encoding="utf8", index=False)
    schema = name + '/'
    s3_resource = boto3.resource('s3',
                                aws_access_key_id= AWS_ACCESS_ID,
                                aws_secret_access_key= AWS_ACCESS_KEY
    )
    file_name = "metrics_"+ name + ".csv"
    s3_resource.Object(bucket, 
                       DATA_SOURCE + schema + str(time.strftime('%Y/%m/%d/')) + file_name).put(Body=csv_buffer.getvalue())
    
def pushToPostgres(df):
    
    # Connect to the database
    secrets = json.loads(getSecret(RDS))
    conn_string = 'postgresql://'+str(secrets['username'])+':'+str(secrets['password'])+'@'+str(secrets['host'])+':5432/'+str(secrets['dbname'])
    db = create_engine(conn_string)
    conn = db.connect()
    table_name = 'google_analytics'
    schema = 'public'
    df.to_sql(table_name, con=conn, schema=schema, if_exists='append', chunksize=10000, index=False)

    removeDuplicatesPostgres()

def removeDuplicatesPostgres():

    # Connect to the database
    secrets = json.loads(getSecret(RDS))
    conn = psycopg2.connect(host=secrets['host'],dbname=secrets['dbname'],user=secrets['username'], password=secrets['password'])
    con = conn
    cur = con.cursor()

    # Query to remove duplicates.
    query = """
        WITH cte AS (
        SELECT
            date,
            max(inserted_at) AS max_data
        FROM
            google_analytics
            
            GROUP BY
                date
        )
        
        DELETE FROM google_analytics t USING cte
                AND t.inserted_at <> max_data
                AND t.date IN (
                    SELECT date
                        FROM google_analytics
                        GROUP BY date
                        ORDER BY date DESC
                        LIMIT 3
            )
    """

    try:
        cur.execute(query)
        con.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        con.rollback()
        cur.close()
        return 1
    
    cur.close()