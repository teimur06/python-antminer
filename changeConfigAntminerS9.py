'''
python -m pip install requests
python -m pip install lxml
python -m pip install pyjsparser
python -m pip install semantic_version
'''

import sys
import requests
from requests.auth import HTTPDigestAuth
from lxml import html
from antminer.base import BaseClient
from pyjsparser import PyJsParser
import socket
import time

class Antminer:
    def __init__(self,IP, user='', password=''):
        self.IP = IP
        self.config = None
        self.postData = None
        self.URL = 'http://'+IP
        self.URLGET = 'http://'+IP+'/cgi-bin/minerConfiguration.cgi'
        self.URLPOST = 'http://'+IP+'/cgi-bin/set_miner_conf.cgi'
        self.URLREBOOT = 'http://'+IP+'/cgi-bin/reboot.cgi?_=1532348375087'
        self.URLKILLBITMAIN = 'http://'+IP+'/cgi-bin/kill_bmminer.cgi?_=1542365058667'
        self.URLSENDFILE = 'http://'+IP+'/cgi-bin/upgrade.cgi'
        self.user = user
        self.password = password
        self.model = ''
        
        try:
            client = BaseClient(self.IP) 
            client.connect()
            self.model = client.version().get('model')
        except socket.timeout:
            print('Antminer API: TimeOut\n')
        except ConnectionRefusedError:
            print('Antminer API: Asik close conection\nTrying model Antminer S9!!!\n')
            self.model = 'Antminer S9'
        except Exception :
            print('Antminer API: Exception\nTrying model Antminer S9!!!\n')
            self.model = 'Antminer S9'
    
    def isS9(self):
        return self.model == 'Antminer S9' or self.model == 'Antminer S9i' or self.model == 'Antminer T9'


    def isD3(self):
        return (self.model == 'Antminer D3')


    def getModel(self):
        return self.model

    def reboot(self):
        try:
            r = requests.get(self.URLREBOOT, auth=HTTPDigestAuth(self.user, self.password), timeout=3)
            print("reboot status {0}\n".format(r.status_code))
        except requests.exceptions.Timeout:
            print('reboot TimeOut\n')
        
        except requests.RequestException:
            print('reboot Request Error\n')
           
    def getConfig(self):
        try:
            r = requests.get(self.URLGET, auth=HTTPDigestAuth(self.user, self.password), timeout=3)
            htmlInput = html.fromstring(r.text.encode('cp1251'))
            script = htmlInput.xpath('//script')

            try:
                p = PyJsParser()
                scriptToPython = p.parse(script[3].text)
                listbody = scriptToPython.get('body')
                self.config = [
                        {'url':      listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[0].get('properties')[0].get('value').get('value'),
                         'worker':   listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[0].get('properties')[1].get('value').get('value'),
                         'password': listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[0].get('properties')[2].get('value').get('value')},

                        {'url':      listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[1].get('properties')[0].get('value').get('value'),
                         'worker':   listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[1].get('properties')[1].get('value').get('value'),
                         'password': listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[1].get('properties')[2].get('value').get('value')},

                        {'url':      listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[2].get('properties')[0].get('value').get('value'),
                         'worker':   listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[2].get('properties')[1].get('value').get('value'),
                         'password': listbody[0].get('expression').get('right').get('properties')[0].get('value').get('elements')[2].get('properties')[2].get('value').get('value')},

                        listbody[0].get('expression').get('right').get('properties')[6].get('value').get('value'),
                        
                        
                        ]
                
                if (self.isS9()):
                    self.config.append(listbody[0].get('expression').get('right').get('properties')[7].get('value').get('value'))

                return self.config

            except AttributeError:
                 print('minerConfiguration.cgi error get config: AttributeError\n')
                 return None    
            except IndexError:
                 print('minerConfiguration.cgi error get config: IndexError\n')
                 return None                

        except requests.exceptions.Timeout:
            print('Get minerConfiguration.cgi TimeOut\n')
            return None
        
        except requests.RequestException:
            print('GET minerConfiguration.cgi Request Error\n')
            return None


        

    def sendConfig(self,config):
        if (config == None):
            return
        postData = {'_ant_pool1url' : config[0].get('url'),
                    '_ant_pool1user' : config[0].get('worker'),
                    '_ant_pool1pw' : config[0].get('password'),

                    '_ant_pool2url' : config[1].get('url'),
                    '_ant_pool2user' : config[1].get('worker'),
                    '_ant_pool2pw' : config[1].get('password'),

                    '_ant_pool3url' : config[2].get('url'),
                    '_ant_pool3user' : config[2].get('worker'),
                    '_ant_pool3pw' : config[2].get('password'),

                    '_ant_nobeeper' : 'false',
                    '_ant_notempoverctrl' : 'false',
                    '_ant_fan_customize_switch' : 'false',
                    '_ant_fan_customize_value' : '',
                    '_ant_freq' : config[3],
                    
                    }
        if (self.isS9()):
            postData.update({'_ant_voltage' : config[4]})
            
        try:
            r = requests.post(self.URLPOST, auth=HTTPDigestAuth(self.user, self.password), data=postData)
            
            return r.text
        except requests.RequestException:
            print('POST set_miner_conf.cgi Request error\n')
            return None

    def sendFile(self,filename):
            r = requests.get(self.URLKILLBITMAIN,  auth=HTTPDigestAuth(self.user, self.password))

            files = {'file': open(filename, 'rb')}
            r = requests.post(self.URLSENDFILE, auth=HTTPDigestAuth(self.user, self.password), files=files)
            statuscode = r.status_code

            r = requests.get(self.URLREBOOT, auth=HTTPDigestAuth(self.user, self.password))

            return statuscode



def setAsicConfig(ip, sets):


    def workerIncrement(worker, i):
        index = ''
        if i < 10: index = '00{0}'.format(i)
        if (i >= 10) and (i < 100): index = '0{0}'.format(i)
        if (i >= 100) and (i < 1000): index = '{0}'.format(i)
        i += 1
        return worker + index

    errorWorker = False
    print('IP: ' + ip)
    asik = Antminer(ip, 'root', 'root')

    if not asik.isS9() and not asik.isD3():
        if asik.getModel() != '': print('{0} not supported!'.format(asik.getModel()))
        return False

    if sets.get('reboot'):
        asik.reboot()
        return False

    configs = asik.getConfig()

    print('model = {0} \n'.format(asik.getModel()))

    if sets.get('update'):
        timeStart = time.time()
        try:
            print("Send file: {}\n".format(sets.get('filename')))
            statuscode = asik.sendFile(sets.get('filename'))
            print("Status send file: {}\n".format(statuscode))
        except requests.exceptions.RequestException as e:
            print("Exeption send File: {0}\n".format(e))

        timeEnd = time.time()
        timeSecond = timeEnd - timeStart;
        timeMinute = timeSecond / 60
        print("Time run {0:.0f} second\n".format(timeSecond))
        print("Time run {0:.0f} minute\n".format(timeMinute))

        return False

    workerNew = sets.get('workerNew')
    if sets.get('incrementWorker'):
        startIncrementWorker = sets.get('startIncrementWorker')
        workerNew = workerIncrement(workerNew, startIncrementWorker)
        startIncrementWorker += 1
        sets.update({'startIncrementWorker': startIncrementWorker})


    if configs != None:
        i = 1
        for config in configs:
            print('======================\nPool {0}:\n     URL: {1}\n     Worker: {2}\n     Password: {3}\n======================'.format( i,config.get('url'),config.get('worker'), config.get('password') ) )
            if sets.get('testWorker'):
                worker = config.get('worker')
                if worker.find(sets.get('testWorkerText')) == -1:
                    errorWorker = True
                    break

            if sets.get('changePool'):
                config.update({'url' : pools[i-1]})

            if sets.get('replaceWorker') :
                worker = config.get('worker')
                worker = worker.replace(sets.get('replaceWorkerTextOld'),sets.get('replaceWorkerTextNew'))
                config.update({'worker' : worker})

            if sets.get('changeWorker'):
                worker = workerNew
                config.update({'worker' : worker})

            i+=1
            if i==4:
                break

        if (not errorWorker) :     
            print('_ant_freq: {0}'.format(configs[3]))
            if (asik.isS9()): print('_ant_voltage: {0}\n'.format(configs[4]))
                        
            if ( sets.get('saveChange') ):
                print('Send POST Data: \n')

                print('\
                         _ant_pool1url={0}&\n \
                        _ant_pool1user={1}&\n \
                        _ant_pool1pw={2}&\n \
                        _ant_pool2url={3}&\n \
                        _ant_pool2user={4}&\n \
                        _ant_pool2pw={5}&\n \
                        _ant_pool3url={6}&\n \
                        _ant_pool3user={7}&\n \
                        _ant_pool3pw={8}&\n \
                        _ant_nobeeper=false&\n \
                        _ant_notempoverctrl=false&\n \
                        _ant_fan_customize_switch=false&\n \
                        _ant_fan_customize_value=&\n \
                        _ant_freq={9}&'.format(configs[0].get('url'),configs[0].get('worker'),configs[0].get('password'),
                                                             configs[1].get('url'),configs[1].get('worker'),configs[1].get('password'),
                                                             configs[2].get('url'),configs[2].get('worker'),configs[2].get('password'),
                                                             configs[3]))
                if (asik.isS9()):
                    print('\
                         _ant_voltage={0}&\n'.format(configs[4]))

                response = asik.sendConfig(configs)           
                if response: print('Get POST response: {0}\n'.format(response))
        else:
            print('Worker "{0}" != "{1}" does not match\n'.format(sets.get('testWorkerText'),configs[0].get('worker')))




#------------------------------Config--------------------------------------

# kazic
startIp1 = 1
endIp1 = 5

startIp2 = 8
endIp2 = 8


sets = {

    'rack_start': 8,
    'rack_end': 8,

    'shelf_start': 9,
    'shelf_end': 9,

    'asik_on_rack_start': 4,
    'asik_on_rack_end': 5,

    'ferma': '40',
    'pools': ['eu.ss.btc.com:1800','eu.ss.btc.com:443','eu.ss.btc.com:25'],

    'replaceWorkerTextOld': 'yersinmukay_',
    'replaceWorkerTextNew': 'YersinMukay.0',

    'workerNew': 'gigalinx.',
    'startIncrementWorker': 992,

    'testWorkerText': 'yersinmukay_',

    'filename': 'D:\\update.tar.gz',

    'update': False,
    'reboot': False,
    'changePool': False,
    'replaceWorker': False,
    'changeWorker': False,
    'incrementWorker': True,
    'saveChange': False,
    'testWorker': False,

}
#--------------------------------------------------------------------------




#================================ MAIN ====================================

#kazic


# try:
#     for s in range(startIp2, endIp2+1):
#         for j in range(startIp1, endIp1+1):
#             ip = '10.{2}.{1}.{0}'.format(j,s,ferma)
#             workerNewTemp = workerNew
#             if incrementWorker:
#                 workerNewTemp = workerIncrement(workerNew,startIncrementWorker)
#                 startIncrementWorker += 1
#             setAsicConfig(ip, reboot, changePool, replaceWorker,
#                           changeWorker, saveChange, testWorker,
#                           pools, replaceWorkerTextOld, replaceWorkerTextNew, workerNewTemp,
#                           testWorkerText)
# except KeyboardInterrupt:
#     print('Exit!')


# Container
try:
    for rack in range(sets.get('rack_start'), sets.get('rack_end') + 1):
        for shelf in range(sets.get('shelf_start'), sets.get('shelf_end') + 1):
            for asik in range(sets.get('asik_on_rack_start'), sets.get('asik_on_rack_end') + 1):
                ip = '10.{0}.{1}.{2}{3}'.format(sets.get('ferma'),rack,shelf,asik)
                setAsicConfig(ip, sets)
except KeyboardInterrupt:
    print('Exit!')
