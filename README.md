# Akademiska-prakse-II-programmaturas-faili
# Akadēmiskā prakse II – PEO perifērijas sistēmas vadības programmatūra

Šajā repozitorijā ir apkopota akadēmiskās prakses laikā izstrādātā programmatūra laboratorijas PEO (plazmas elektrolītiskās oksidēšanas) iekārtas perifērijas sistēmas vadībai. Programmatūra realizē modulāru un slāņveida arhitektūru, kas nodala augsta līmeņa procesa orķestrēšanu no zema līmeņa aparatūras vadības.

Programmatūra ir izstrādāta, izmantojot Python un MicroPython programmēšanas valodas, un paredzēta darbam ar mikrokontrolieru balstītām perifērijas ierīcēm.

## Repozitorija struktūra

- `devices/`  
  Satur augsta līmeņa perifērijas ierīču abstrakcijas (piemēram, šļirces sūkņi, solenoīda vārsti), kas apvieno aparatūras draiverus funkcionālos moduļos.

- `drivers/`  
  Satur zema līmeņa aparatūras draiverus (GPIO vadība, soļu motoru kontrole, komunikācijas interfeisi), kas nodrošina tiešu mijiedarbību ar fiziskajām ierīcēm.

- `modes/`  
  Satur sistēmas darbības režīmus un algoritmus, kas realizē dažādus perifērijas sistēmas darba scenārijus (piemēram, inicializācijas ciklus un dozēšanas secības).

- `config.py`  
  Centralizēts konfigurācijas fails sistēmas parametru definēšanai (pieslēgumu iestatījumi, laika parametri, aparatūras konfigurācija).

- `main.py`  
  Programmatūras ieejas punkts, kas realizē sistēmas inicializāciju un koordinē atsevišķu moduļu un režīmu darbību.

## Funkcionalitāte

Izstrādātā programmatūra nodrošina:
- soļu motoru darbinātu šļirces sūkņu vadību,
- solenoīda vārstu un citu perifērijas ierīču komutāciju,
- modulāru sistēmas paplašināšanu ar jauniem ierīču tipiem un darbības režīmiem,
- teksta komandu protokolu saziņai caur USB seriālo interfeisu.

## Piezīme

Šī programmatūra ir izstrādāta akadēmiskās prakses ietvaros un paredzēta pētnieciskām un eksperimentālām vajadzībām laboratorijas vidē.
