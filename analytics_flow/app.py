import warnings
import json
import pandas as pd
from tqdm import tqdm
import time
from datetime import datetime

from analytics_flow.utils.analytics_utils import getReport
from analytics_flow.utils.db_connection import pushToLake, pushToPostgres
from analytics_flow.resources.configs import ANALYTICS
from analytics_flow.secrets.get_token import getSecret


from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient

def main():

  tempo_inicial = time.time()
  warnings.filterwarnings("ignore")

  ## --- AUTHORIZATION --- ##

  SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
  KEY_FILE_LOCATION = json.loads(getSecret(ANALYTICS)) # GET SECRETS FROM AWS SECRET MANAGER
  KEY_FILE_LOCATION['private_key'] = KEY_FILE_LOCATION['private_key'].replace('\\n','\n')

  credentials =  service_account.Credentials.from_service_account_info(KEY_FILE_LOCATION)
  scoped_credentials = credentials.with_scopes(SCOPES)

  client = BetaAnalyticsDataClient(credentials=scoped_credentials)

  ## --- PUSH PROPERIES --- ##

  property_id = ['000000000'] # List of properies to extract data
  dateStart = pd.date_range(end=pd.datetime.now(), periods=1, freq='D').strftime("%Y-%m-%d").tolist()[0] # Return de last 1 day

  ## --- GETTING ORDERS --- ##

  dfFullErros = pd.DataFrame() # Creating a DataFrame to store integrations errors
  dfFull = pd.DataFrame() 

  for i in tqdm(range(len(property_id))):

    try: 
      orders = getReport(property_id[i], dateStart, client) 
      dfFull = dfFull.append(orders)

    except Exception as e:
      data = [["propriedade: " + property_id[i], e, 'GA4']]
      df_erros = pd.DataFrame(data, columns=['account', 'error', 'scope'])   
      dfFullErros = dfFullErros.append(df_erros)

  try:
    pushToLake(dfFull, 'raw-data')

  except Exception as e:
    print(e)

  try:

    # TRANSFORMING THE DATA

    dfFull = dfFull[['date','client_id','totalRevenue','checkouts', 'addToCarts', 'activeUsers','transactions','sessions','property_id']]
    dfFull = dfFull.rename({"totalRevenue":"revenue", "addToCarts": "add_to_cart", "activeUsers":"users"}, axis=1) 
    dfFull["inserted_at"] = datetime.datetime.now()

    pushToLake(dfFull, 'processed-data')
    # pushToPostgres(dfFull)

  except Exception as e:
      print(e)

  print('Complete\n')

  tempo_final = time.time()
  tempo_total = tempo_final - tempo_inicial
  print(f"Tempo Total de Execução:  {int(tempo_total/60)} minutos")
  
main()