from py4j.protocol import Py4JJavaError

def pull_stock_info(url, db_host, table_path):
    response = requests.get(url)
    if response.status_code == 200 or response.status_code == 201:
        content = response.content.decode('utf-8')
        content = content.replace('Summary Quote', 'SummaryQuote')
        delete_path(spark, db_host, table_path)
        df = spark.createDataFrame([[content]], ['info_csv'])

        # Sometimes there is a race condition that caused FileAlreadyExistsException error.
        # In that case, do not do anything.
        try:
            df.rdd.map(lambda x: x['info_csv'].replace("[","").replace("]", "")).saveAsTextFile(db_host+table_path)
            logger.warn("Stored data from {} to {}.".format(url, db_host+table_path))
        except Py4JJavaError as e:
            logger.warn("Table {} already exists.".format(db_host+table_path))
            pass
    else:
        logger.warn("Failed to connect to {}. We will use existing stock info data if they have been created.".format(url))
        
    
pull_stock_info(URL_NASDAQ, DB_HOST, TABLE_STOCK_INFO_NASDAQ)
pull_stock_info(URL_NYSE, DB_HOST, TABLE_STOCK_INFO_NYSE)