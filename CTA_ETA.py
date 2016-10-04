import requests
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from Tkinter import *
import os
from pytz import timezone

# data dict containing info for all stations to pull data for.
# 'pos' is a key referring to x, y coords for displaying text in GUI
data = {'trains': {'Red': {'30121': {'dir': 'north', 'pos': (460, 123)},
                           '30122': {'dir': 'south', 'pos': (1004, 123)}},
                   'Brn': {'30155': {'dir': 'north', 'pos': (371, 294)},
                           '30156': {'dir': 'south', 'pos': (921, 294)}},
                   'P':   {'30155': {'dir': 'north', 'pos': (645, 294)},
                           '30156': {'dir': 'south', 'pos': (1193, 294)}}},

        'buses': {'156': {'1450': {'dir': 'north', 'pos': (460, 468)},
                          '1411': {'dir': 'south', 'pos': (1004, 468)}},
                  '22':  {'1902': {'dir': 'north', 'pos': (460, 565)},
                          '1847': {'dir': 'south', 'pos': (1004, 565)}},
                  '36':  {'1902': {'dir': 'north', 'pos': (460, 663)},
                          '1847': {'dir': 'south', 'pos': (1004, 663)}},
                  '72':  {'923': {'dir': 'west', 'pos': (422, 906)}}},

        'divvy': {'278': {'Clark St & Schiller St': {'pos': (1125, 950)}},
                  '112': {'Clark St & North Ave': {'pos': (1125, 840)}},
                  '266': {'Wells St & Concord Ln': {'pos': (830, 840)}},
                  '268': {'Wells St & Evergreen Ave': {'pos': (830, 950)}}}}

# CTA API keys. Insert your own as a string.
ctaBusKey = os.environ['CTA_BUS_KEY']
ctaTrainKey = os.environ['CTA_TRAIN_KEY']

def busTimes(data, ctaBusKey):
    '''
    PURPOSE:    busTimes function pulls arrival times for each stop in
                data['buses']. It then saves formatted arr times (in mins)
                as a string in the 'txt' key of data['buses'][rt][stp]['txt']
                which is accessed by Tkinter.

    INPUT:      data (dict) - dict which includes bus stop details
                ctaBusKey (str) - API key to for CTA Bus Tracker Website

    OUTPUT:     None
    '''

    for rt in data['buses']:
        for stp in data['buses'][rt]:
            params = {'key': ctaBusKey, 'stpid': stp, 'rt': rt, 'top': '6'}
            bustimes = requests.get('http://www.ctabustracker.com/bustime/' +
                                    'api/v1/getpredictions', params=params)
            treeRoot = ET.fromstring(bustimes.text)    # xml parsing root
            error = treeRoot.findall('error/msg')      # error msgs from CTA
            predTimes = treeRoot.findall('prd/prdtm')  # list of pred arr times

            if error:
                data['buses'][rt][stp]['txt'] = error[0].text
            else:
                arrTimes = []
                for predTime in predTimes:
                    pred_time = dt.strptime(predTime.text, '%Y%m%d %H:%M')
                    pred_time = timezone('US/Central').localize(pred_time)
                    now = (
                        dt.now(timezone('UTC'))
                        .astimezone(timezone('US/Central'))
                    )
                    if pred_time > now:
                        arrTimes.append((pred_time - now).seconds // 60)
                    else:
                        arrTimes.append(0)

                txt = ', '.join([str(i) for i in arrTimes])
                data['buses'][rt][stp]['txt'] = txt


def trainTimes(data, ctaTrainKey):
    '''
    PURPOSE:    trainTimes function pulls arrival times for each stop in
                data['trains']. It then saves formatted arr times (in mins)
                as a string in the 'txt' key of data['trains'][rt][stp]['txt']
                which is accessed by Tkinter.

    INPUT:      data (dict) - dict which includes train stop details
                ctaTrainKey (str) - API key to for CTA Train Tracker Website

    OUTPUT:     None
    '''

    for rt in data['trains']:
        for stp in data['trains'][rt]:
            params = {'key': ctaTrainKey, 'stpid': stp, 'rt': rt, 'max': '7'}
            traintimes = requests.get('http://lapi.transitchicago.com/api/' +
                                      '1.0/ttarrivals.aspx', params=params)
            treeRoot = ET.fromstring(traintimes.text)   # xml parsing root
            predTimes = treeRoot.findall('eta/arrT')    # list pred arr times
            staNm = treeRoot.findall('eta/staNm')       # used to catch errors

            if staNm:
                arrTimes = []
                for predTime in predTimes:
                    pred_time = dt.strptime(predTime.text, '%Y%m%d %H:%M:%S')
                    pred_time = timezone('US/Central').localize(pred_time)
                    now = (
                        dt.now(timezone('UTC'))
                        .astimezone(timezone('US/Central'))
                    )
                    if pred_time > now:
                        arrTimes.append((pred_time - now).seconds // 60)
                    else:
                        arrTimes.append(0)

                txt = ', '.join([str(i) for i in arrTimes])
                data['trains'][rt][stp]['txt'] = txt
            else:
                data['trains'][rt][stp]['txt'] = 'None'


def bikeData(data):
    '''
    PURPOSE:    bikeData function pulls avail / total bikes from Divvy API
                for each bike station id in data['divvy']. It then saves
                formatted info as a string in data['divvy'][id][stn]['txt']
                which is accessed by Tkinter.

    INPUT:      data (dict) - dict which includes divvy station details

    OUTPUT:     None
    '''

    r = requests.get('https://feeds.divvybikes.com/stations/stations.json')
    for i in data['divvy']:
        for stn in data['divvy'][i]:
            txt = str(r.json()['stationBeanList'][int(i)]['availableBikes']) \
                  + ' / ' + \
                  str(r.json()['stationBeanList'][int(i)]['availableDocks'])
            data['divvy'][i][stn]['txt'] = txt


def collectData(root, canvas):
    '''
    PURPOSE:    collectData is a function to update arrival time and bike info
                in Tkinter display by calling trainTimes, busTimes, and
                bikeData. The function recursively calls itself every 15 sec.

    INPUT:      None

    OUTPUT:     None
    '''

    trainTimes(data, ctaTrainKey)
    busTimes(data, ctaBusKey)
    bikeData(data)
    updateDisplay(data, canvas)
    root.after(15000, collectData)  # loop collectData every 15 seconds


def initialize_display(data, cvs):
    '''
    PURPOSE:    Creates Tkinter canvas text object for each station in data
                and intializes text string for each station with 'Loading'

    INPUT:      data (dict) - dict which includes all station info
                cvs (Tkinter Canvas Object) - canvas object for displaying txt

    OUTPUT:     None
    '''

    for i in data:
        for j in data[i]:
            for k in data[i][j]:
                data[i][j][k]['txt'] = 'Loading'
                data[i][j][k]['obj'] = cvs.create_text(data[i][j][k]['pos'][0],
                                                       data[i][j][k]['pos'][1],
                                                       text=data[i][j][k]['txt'],
                                                       font=('Purisa', 36),
                                                       fill='white')


def updateDisplay(data, cvs):
    '''
    PURPOSE:    Updates TK canvas text objects on display with updated info
                pulled from trainTimes, busTimes, and bikeData

    INPUT:      data (dict) - dict which includes all station info
                cvs (Tkinter Canvas Object) - canvas object for displaying txt

    OUTPUT:     None
    '''

    for i in data:
        for j in data[i]:
            for k in data[i][j]:
                cvs.itemconfig(data[i][j][k]['obj'], text=data[i][j][k]['txt'])


def exitFullScreen():
    '''
    PURPOSE:    Function called by Tkinter button object to kill fullscreen
                mode, and quit the program

    INPUT:      None

    OUTPUT:     None
    '''

    root.attributes('-fullscreen', False)
    root.quit()


def main():
    '''
    PURPOSE:    Create Tkinter GUI, pull arrival time info from CTA Bus
                and Train Tracker APIs, pull bike data info from Divvy API
                and display info in Tkinter GUI. This code runs on a
                raspberry pi and triggered by a light switch in my home.
    '''

    # Tkinter GUI setup
    root = Tk()
    root.title('CTA and Divvy ETA')
    root.attributes('-fullscreen', True)
    photo = PhotoImage(file='Background_1280x1024.gif')
    canvas = Canvas(root, width=1280, height=1024)
    canvas.pack()
    canvas.create_image(0, 0, image=photo, anchor=NW)
    button = Button(root, text='x', command=exitFullScreen)
    canvas.create_window(0, 1024, anchor=SW, window=button)

    initialize_display(data, canvas)
    updateDisplay(data, canvas)
    collectData(root, canvas)
    root.after(10000, lambda: root.destroy())
    root.mainloop()
