# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 09:30:00 2018

@author: bhautik
"""

import zipfile
import urllib
import pandas as pd
import json
from redis import StrictRedis
import sys
from zipfile import BadZipfile

try:
    d = sys.argv[1]
    redis_url = sys.argv[2]
    date = int(d)
    if len(d) == 6 and isinstance(date, int):
        if redis_url:
            redis_conn = StrictRedis.from_url(redis_url)
            #r = StrictRedis.from_url("redis://h:p381ef8e02280716529f06c01a40c2ef52267dd19591f274b6d5112b871e25641@ec2-34-197-61-164.compute-1.amazonaws.com:46289/0")
            #==============================================================================
            print "Getting data"
            file_name_zip = "EQ"+d+"_CSV.ZIP"
            try:
                urllib.urlretrieve("https://www.bseindia.com/download/BhavCopy/Equity/"+file_name_zip, "/tmp/today.zip")
                print "Got Data"
                try:
                    zip_file = zipfile.ZipFile("/tmp/today.zip", 'r')
                    zip_file.extractall("/tmp/today")
                    zip_file.close()
                    try: 
                        pda = pd.read_csv("/tmp/today/EQ160218.CSV", usecols=["SC_CODE","SC_NAME","OPEN","HIGH","LOW","CLOSE"])
                        pda["diff"] = pda["CLOSE"] - pda["OPEN"]
                        pda = pda.sort_values(by=["diff"], ascending=0)
                        lis_record = pda.values.tolist()
                        # 
                        print "Calculation Done. Inserting data to redis"
                        score = 1
                        for i in lis_record:
                            print i
                            d = {"sc_code": i[0], "sc_name": i[1].strip(), "open": i[2], "high": i[3], "low": i[4], "close": i[5], "Gain": i[6]}
                            if score < 11:
                                redis_conn.zadd("equity",score,json.dumps(d))
                                redis_conn.set(i[1].strip(), json.dumps(d))
                            else:
                                redis_conn.set(i[1].strip(), json.dumps(d))
                            score += 1
                    except Exception as e:
                        print "Error in parsing data from csv file"
                except BadZipfile:
                    print "File is not zip file"
            except Exception as e:
                print "Not able to retrieve file. "+str(e)
        else:
            print "Enter Redis DB URI as second argument"
    else:
        print "Enter date in ddmmyy format. Eg: if date is 31-May-2017 then python bhavcopys.py 310517 redis://localhost:6379/0"
except IndexError:
    print "Run script with date argument,please. Eg: if date is 31-May-2017 then python bhavcopys.py 310517 redis://localhost:6379/0"