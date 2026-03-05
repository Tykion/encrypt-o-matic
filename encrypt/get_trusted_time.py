import ntplib
import time

def get_trusted_time():
    try:
        c = ntplib.NTPClient()
        response = c.request('uk.pool.ntp.org')
        return response.tx_time
    except:
        #if no response just use system time
        return time.time()