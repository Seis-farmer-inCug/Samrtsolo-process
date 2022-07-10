import csv
import os
from tokenize import PlainToken
import numpy as np
import sys
import glob
import subprocess
from obspy.core import read
from obspy import UTCDateTime, read, Trace, Stream
from obspy.core import UTCDateTime
from obspy.geodetics import gps2dist_azimuth,kilometers2degrees
from obspy.taup import TauPyModel

##mkdir_by_catalog##
##catalog:download the catalog from usgs;input the path of catalog
##pathmk:input the sac data where you want to save;the name of dir should be the name of the station
##seismo:output the imformation from catalog
def mkdir_by_catalog(catalog,save_path):
    catalog = csv.reader(open(catalog))
    seismo = []
    for seism in catalog:
        seismo.append(seism)
    for i in range(1,len(seismo)):
        dirname = os.path.join(save_path,str(i))
        if os.path.exists(dirname):
            pass
        else:
            os.mkdir(dirname)
    return seismo
def get_p_wave(seismo,stla,stlo,path,save_path):
    starttime = []
    pt = []
    sttime = []
    begin = []
    end = []
    pt = []
    for i in range(1,len(seismo)):
        starttime.append(seismo[i][0])
        evla = float(seismo[i][1])
        evlo = float(seismo[i][2])
        depth = float(seismo[i][3])
        dist,az,baz = gps2dist_azimuth(evla,evlo,stla,stlo)
        dist /= 1000.0
        gcarc = kilometers2degrees(dist)
        model = TauPyModel(model="iasp91")
        pt.append(model.get_travel_times(depth,gcarc)[0].time)
    sttime = []
    begin = []
    end = []
    for i in range(0,len(starttime)):
        time = UTCDateTime(starttime[i])
        timebegin = time+pt[i]-60
        timeend = time+pt[i]+240
        sttime.append(time)
        begin.append(timebegin)
        end.append(timeend)
    time_title = []  
    time_title_list = []
    for i in range(0,len(starttime)):
        stt = []
        sttt = starttime[i].split(':')[0].split('-')
        stt.append(sttt[0])
        stt.append(sttt[1])
        stt.append(sttt[2])
        stt.append('00')
        time_title_list.append(stt)
        time_title.append(''.join(stt))
    startmin = []
    for i in range(0,len(starttime)):
        min = starttime[i].split(':')[1]
        startmin.append(int(min))
    
    last = ['_E.miniseed','_N.miniseed','_Z.miniseed']
    last1 = ['_E.sac','_N.sac','_Z.sac']
    for i in range(0,len(starttime)):
        date = starttime[i].split('T')[0]
        pathsm = os.path.join(path,date)
        if startmin[i] < 30:
            for j in range(0,len(last)): 
                pathsm1 = os.path.join(pathsm,''.join([time_title[i],last[j]]))
                if os.path.exists(pathsm1):  
                    st = read(pathsm1)       
                    tr = st[0]
                    b = begin[i]
                    e = end[i]
                    tr1 = tr.trim(b,e)
                    st = Stream(tr1)
                    st.write(os.path.join(save_path,str(i+1),''.join(['smartsolo_',str(i+1),last1[j]])),format='SAC')
        else:
            for j in range(0,len(last)):
                pathsm1 = os.path.join(pathsm,''.join([time_title[i],last[j]]))
                if os.path.exists(pathsm1):
                    fn = []
                    t = int(time_title_list[i][2].split('T')[1])+1
                    time2_title = []
                    time2_title.append(time_title_list[i][0])
                    time2_title.append(time_title_list[i][1])
                    time2_title.append(time_title_list[i][2].split('T')[0])
                    time2_title.append('T')
                    if t<10:
                        time2_title.append('0')
                    time2_title.append(str(t))
                    time2_title.append('00')
                    fn.append(''.join(time2_title))
                    fn.append(last[j])
                    st = read(pathsm1)
                    pathsm2 = os.path.join(pathsm,''.join(fn))
                    if os.path.exists(pathsm2):
                        st += read(pathsm2)
                        st.merge(method=1,fill_value=0)
                        tr = st[0]
                        b = begin[i]
                        e = end[i]
                        tr1 = tr.trim(b,e)
                        st = Stream(tr1)
                        st.write(os.path.join(save_path,str(i+1),''.join(['smartsolo_',str(i+1),last1[j]])),format='SAC')


catalog = ['/home/wanxinluo/Smartsolo_compare/Seism_wave/catalogWHA.csv','/home/wanxinluo/Smartsolo_compare/Seism_wave/catalogWHN.csv','/home/wanxinluo/Smartsolo_compare/Seism_wave/catalogXNI.csv']
save_path = ['/home/wanxinluo/Smartsolo_compare/Seism_wave/WHA','/home/wanxinluo/Smartsolo_compare/Seism_wave/WHN','/home/wanxinluo/Smartsolo_compare/Seism_wave/XNI']
stla = [30.506000,30.542800,29.715800]
stlo = [114.506700,114.353900,114.410900]
path = ['/media/wanxinluo/One Touch/data/smartsolo_rename/WHA','/media/wanxinluo/One Touch/data/smartsolo_rename/WHN','/media/wanxinluo/One Touch/data/smartsolo_rename/XNI']
for i in range(0,len(stlo)):
    seismo = mkdir_by_catalog(catalog[i],save_path[i])
    print('mkdir by catalog complete!')
    get_p_wave(seismo,stla[i],stlo[i],path[i],save_path[i])
    print('Success!')
print('Completed!')