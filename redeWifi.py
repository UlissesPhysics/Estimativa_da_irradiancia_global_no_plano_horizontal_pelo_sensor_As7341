def acessar():
    import network
    import ssd1306
    from machine import I2C, Pin, SoftI2C
    from time import sleep_ms
    
    scl      = Pin(22, Pin.OUT, Pin.PULL_UP)
    sda      = Pin(21, Pin.OUT, Pin.PULL_UP)
    i2c      = SoftI2C(scl=scl, sda=sda)
    oled     = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

    ssid     = "nome da rede"
    password = "senha da rede"
    
    station   = network.WLAN(network.STA_IF)
    
    if station.isconnected() == True:
        ip = station.ifconfig()
        oled.fill(0)
        oled.text('Conectado', 15, 10)
        oled.text('Ip de acesso:', 10, 20)
        oled.text(f'{ip[0]}', 10, 30)
        oled.show()
        return
    
    station.active(True)
    station. connect(ssid, password)
    
    while station.isconnected() == False:
        pass
    ip = station.ifconfig()
    oled.fill(0)
    oled.text('Conexao bem', 10, 10)
    oled.text('Sucedida!!!', 20, 20)
    oled.text('Ip de acesso:', 10, 40)
    oled.text(f'{ip[0]}', 10, 50)
    oled.show()
    sleep_ms(2500)


