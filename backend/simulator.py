import time, random
import numpy as np

def stream_vitals():
    hr = random.randint(62, 98)
    temp = round(random.uniform(36.4, 37.6), 2)
    spo2 = random.randint(95, 100)
    sbp = random.randint(105, 138)
    dbp = random.randint(65, 88)
    while True:
        hr = int(np.clip(hr + random.randint(-3,3), 45, 150))
        temp = round(float(np.clip(temp + random.uniform(-.05,.05), 35.5, 40.5)),2)
        spo2 = int(np.clip(spo2 + random.randint(-1,1), 88, 100))
        sbp = int(np.clip(sbp + random.randint(-4,4), 85, 210))
        dbp = int(np.clip(dbp + random.randint(-3,3), 50, 130))
        yield {"heart_rate_bpm":hr,"temperature_c":temp,"spo2_pct":spo2,
               "systolic_bp":sbp,"diastolic_bp":dbp}
        time.sleep(1)
