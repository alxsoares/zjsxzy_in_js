# encoding: utf-8

import requests
import io
import pandas as pd

import const

def download(name):
    print("downloading %s..."%(name))
    url = const.URLS[name]
    response = requests.get(url)
    s = response.content
    # 删掉介绍
    if name == 'VXEEM' or name == 'TYVIX' or name == 'VXO' or name == 'VXN' or name == 'RVX' or name == 'VXEFA':
        # VXEMM、TYVIX、VXO、VXN、RVX、EFA前面有2行
        s = s.split('\n')[2:]
    elif name == 'VXD':
        # VXD前面有4行
        s = s.split('\n')[4:]
    else:
        s = s.split('\n')[1:]
    s = '\n'.join(s)

    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    fname = "%s/%s.csv"%(const.DATA_DIR, name)
    df.to_csv(fname, index=False)

def download_all():
    names = const.URLS.keys()
    for name in names:
        download(name)

if __name__ == "__main__":
    download_all()
    # download('VXEFA')
