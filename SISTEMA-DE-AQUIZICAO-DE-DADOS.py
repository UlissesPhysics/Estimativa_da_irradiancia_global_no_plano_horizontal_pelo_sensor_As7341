# Sobre o Programa:
# O programa foi escrito para promover a comunicação entre os componetes da Estação,
# entre a Estação e o usuário, bem como fazer o armazenamento de dados (contagem de fótons,
# parâmetrons de tempo, ganho, data e hora) e compartilhamento online desses dados.

# Módulos/Bibliotecas/Drivers
import sys
import json
import redeWifi        # Criado pelo autor, função para acessar uma rede wifi
                       # e exibir o ip de acesso no display oled.
import ssd1306
import urequests
import utime
import os
from microWebSrv import MicroWebSrv
from machine import I2C, Pin, SoftI2C, RTC
from time import sleep_ms
from as7341 import *   # Funciona em conjunto com as7341_smux_select.py


# Definições

scl                  = Pin(22, Pin.OUT, Pin.PULL_UP)
sda                  = Pin(21, Pin.OUT, Pin.PULL_UP)
url                  = "http://worldtimeapi.org/api/timezone/America/Sao_Paulo"
rtc                  = RTC()
ultima_peticion      = 0
intervalo_peticiones = 5
#response             = str
i2c                  = SoftI2C(scl=scl, sda=sda)

cont_medicao         =  0

horas                = list()
datas                = list()
ganho                = list()
atime                = list()
astep                = list()
chanel_1             = list()
chanel_2             = list()
chanel_3             = list()
chanel_4             = list()
chanel_5             = list()
chanel_6             = list()
chanel_7             = list()
chanel_8             = list()
chanel_nir           = list()
chanel_clear         = list()

dados                = {'horas':horas,
                        'datas':datas,
                        'ganho':ganho,
                        'atime':atime,
                        'astep':astep,
                        '415nm':chanel_1,
                        '445nm':chanel_2,
                        '480nm':chanel_3,
                        '515nm':chanel_4,
                        '555nm':chanel_5,
                        '590nm':chanel_6,
                        '630nm':chanel_7,
                        '680nm':chanel_8,
                        '910nm':chanel_nir,
                        'Clear':chanel_clear

                }


# Conexão de Internet
redeWifi.acessar()
sleep_ms(2000)

# Verificação da conexão do dispositivo i2c
print("Dispositivos detectados em endereços I2C:",
      " ".join(["0x{:02X}".format(x) for x in i2c.scan()]))

# Estabelecendo a comunicação do Esp com os dispositivos I2C 
sensor = AS7341(i2c)
oled   = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

if not sensor.isconnected():
    print("Falha ao contatar AS7341, encerrando")
    sys.exit(1)



# Configuração do fator de ganho, passo e tempo

for i in (2000, 800, 128, 4, 0, 0.7, 0.5, 0.3, 0):
    sensor.set_again_factor(i)
    print("factor in:", i, "code", sensor.get_again(), "result:", sensor.get_again_factor())

sensor.set_measure_mode(AS7341_MODE_SPM)

#print("Integration time:", sensor.get_integration_time(), "msec")

oled.fill(0)
oled.text('Medicao em', 30, 10)
oled.text('5 segundos', 30, 20)
oled.show()
sleep_ms(1000)

oled.fill(0)
oled.text('Medicao em', 30, 10)
oled.text('4 segundos', 30, 20)
oled.show()
sleep_ms(1000)

oled.fill(0)
oled.text('Medicao em', 30, 10)
oled.text('3 segundos', 30, 20)
oled.show()
sleep_ms(1000)

oled.fill(0)
oled.text('Medicao em', 30, 10)
oled.text('2 segundos', 30, 20)
oled.show()
sleep_ms(1000)

oled.fill(0)
oled.text('Medicao em', 30, 10)
oled.text('1 segundos', 30, 20)
oled.show()
sleep_ms(1000)

try:
    while True:
        
        cont_medicao += 1

        #dif          = 0.033
        teps         = 1000
        time         = 50
        gain         = 0              # ganho 0 correnponde ao fator exponecial 0.5

# Configuração de parâmetros

        sensor.set_atime(time)        # 1-255
        sensor.set_astep(teps)        # 1-65534  
        sensor.set_again(gain)        # 1-8

        ganho.append(gain)
        #difusor.append(dif)
        astep.append(time)
        atime.append(teps)

# Medição e armazenamento

        sensor.start_measure("F1F4CN")
        f1,f2,f3,f4,clr,nir = sensor.get_spectral_data()

        chanel_1.append(f1)
        chanel_2.append(f2)
        chanel_3.append(f3)
        chanel_4.append(f4)

        sensor.start_measure("F5F8CN")
        f5,f6,f7,f8,clr,nir = sensor.get_spectral_data()

        chanel_5.append(f5)
        chanel_6.append(f6)
        chanel_7.append(f7)
        chanel_8.append(f8)
        chanel_clear.append(clr)
        chanel_nir.append(nir)
        
# Marcade tempo da medição      
        
        if (utime.time() - ultima_peticion) >= intervalo_peticiones:
            response = urequests.get(url)

            if response.status_code == 200:
                datos_objeto  = response.json()
                fecha_hora    = str(datos_objeto["datetime"])
                año           = int(fecha_hora[0:4])
                mes           = int(fecha_hora[5:7])
                día           = int(fecha_hora[8:10])
                hora          = int(fecha_hora[11:13])
                minutos       = int(fecha_hora[14:16])
                segundos      = int(fecha_hora[17:19])
                sub_segundos  = int(round(int(fecha_hora[20:26]) / 10000))

                rtc.datetime((año, mes, día, 0, hora, minutos, segundos, sub_segundos))

                d            = "{2:02d}/{1:02d}/{0:4d}" .format(*rtc.datetime())
                h            = "{4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
                ultima_peticion = utime.time()
                
                datas.append(d)
                horas.append(h)
        
# Status da medição
        
        oled.fill(0)
        oled.text(f'Medicao {cont_medicao}', 30, 10)
        oled.text('ganho:{:d}'.format(gain), 30, 20)
        oled.text('astep:{:d}'.format(time), 30, 30)
        oled.text('atime:{:d}'.format(teps), 30, 40)
        oled.show()
        sleep_ms(10000)

        oled.fill(0)
        oled.text('415nm: {:d}'.format(f1),   10, 5)
        oled.text('445nm: {:d}'.format(f2),   10, 15)
        oled.text('480nm: {:d}'.format(f3),   10, 25)
        oled.text('515nm: {:d}'.format(f4),   10, 35)
        oled.text('555nm: {:d}'.format(f5),   10, 45)
        oled.text(f'{d}'               ,   10, 55)
        oled.show()
        sleep_ms(25000)

        oled.fill(0)
        oled.text('590nm: {:d}'.format(f6),   10, 5)
        oled.text('630nm: {:d}'.format(f7),   10, 15)
        oled.text('680nm: {:d}'.format(f8),   10, 25)
        oled.text('910nm: {:d}'.format(nir),  10, 35)
        oled.text('Clear: {:d}'.format(clr),  10, 45)
        oled.text(f'{h}'                ,  10, 55)
        oled.show()
        sleep_ms(25000)

        

        if cont_medicao==30:      # o valor define o tamanho do ciclo de medição

#Armazenamento FIFO
            
            i = os.listdir('www')
            os.remove('www/medicao_mais_antiga.json')
            i = os.listdir('www')
            os.rename('www/medicao_antiga.json', 'www/medicao_mais_antiga.json')
            os.rename('www/medicao_recente.json', 'www/medicao_antiga.json')
            i = os.listdir('www')

            dados = json.dumps(dados)

            with open('www/medicao_recente.json','w') as file:
                file.write(dados)

            i = os.listdir('www')
            print(f'{i}')
            print("Medição completa")

            oled.fill(0)
            oled.text('Medicao', 35, 30)
            oled.text('Concluida!', 25, 40)
            oled.show()

            break

except KeyboardInterrupt:

    print(" from keyboard")
    oled.fill(0)
    oled.text('Interrupted', 35, 30)
    oled.text('from', 45, 40)
    oled.text('keyborard', 35, 50)
    oled.show()

sensor.disable()
sleep_ms(3000)
oled.fill(0)
oled.show()

# Conexão de internet

redeWifi.acessar()


# Coloca o servidor local na ar

def _httpHandler(httpClient, httpResponse):
    httpResponse.WrinteResponseFile(filepath = 'www/index.html', contentType = 'text/html', headers =None)

mws = MicroWebSrv(webPath='www')
mws.Start(threaded = True)
mws.IsStarted()


