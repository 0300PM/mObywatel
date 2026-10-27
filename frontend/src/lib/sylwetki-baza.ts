export const BAZA: Record<string, [string, number, number, number]> = {
  // Toyota
  'toyota corolla touring sports':['kombi',4650,1460,2700],'toyota corolla sedan':['sedan',4630,1435,2700],'toyota corolla cross':['suv',4460,1620,2640],'toyota corolla':['hatch',4370,1435,2640],
  'toyota yaris cross':['crossover',4180,1590,2560],'toyota yaris':['hatch',3940,1500,2560],'toyota aygo x':['crossover',3700,1510,2430],'toyota aygo':['mini',3470,1460,2340],
  'toyota c-hr':['crossover',4360,1555,2640],'toyota rav4':['suv',4600,1690,2690],'toyota auris':['hatch',4330,1475,2600],'toyota avensis':['sedan',4750,1480,2700],
  'toyota prius':['liftback',4600,1430,2750],'toyota land cruiser':['suv',4890,1880,2850],'toyota proace':['van',4960,1900,3275],'toyota hilux':['pickup',5325,1815,3085],
  // Skoda
  'skoda octavia combi':['kombi',4690,1470,2690],'skoda octavia':['liftback',4690,1470,2690],'skoda superb combi':['kombi',4900,1480,2840],'skoda superb':['liftback',4870,1470,2840],
  'skoda fabia combi':['kombi',4260,1470,2470],'skoda fabia':['hatch',4110,1460,2560],'skoda scala':['hatch',4360,1470,2650],'skoda kamiq':['crossover',4240,1530,2650],
  'skoda karoq':['suv',4390,1620,2640],'skoda kodiaq':['suv',4700,1680,2790],'skoda enyaq':['suv',4650,1620,2770],'skoda citigo':['mini',3600,1480,2420],'skoda rapid':['liftback',4480,1460,2600],
  // Volkswagen
  'volkswagen golf iv':['hatch',4150,1440,2510],'volkswagen golf v':['hatch',4200,1480,2580],'volkswagen golf vi':['hatch',4200,1480,2580],'volkswagen golf vii':['hatch',4260,1450,2620],
  'volkswagen golf variant':['kombi',4630,1480,2670],'volkswagen golf':['hatch',4280,1460,2630],'volkswagen polo':['hatch',4070,1450,2560],'volkswagen up':['mini',3600,1480,2420],
  'volkswagen passat variant':['kombi',4890,1510,2790],'volkswagen passat':['sedan',4770,1460,2790],'volkswagen tiguan':['suv',4510,1670,2680],'volkswagen t-roc':['crossover',4240,1570,2600],
  'volkswagen touran':['mpv',4530,1660,2790],'volkswagen sharan':['mpv',4850,1720,2920],'volkswagen arteon':['liftback',4860,1430,2840],'volkswagen id.3':['hatch',4260,1570,2770],
  'volkswagen id.4':['suv',4580,1640,2770],'volkswagen caddy':['kombivan',4500,1830,2750],'volkswagen transporter':['van',4900,1990,3000],'volkswagen crafter':['furgon',5990,2590,3640],
  'volkswagen amarok':['pickup',5250,1880,3270],'volkswagen touareg':['suv',4880,1710,2900],
  // Opel
  'opel astra sports tourer':['kombi',4640,1480,2730],'opel astra':['hatch',4370,1460,2680],'opel corsa':['hatch',4060,1440,2540],'opel insignia':['liftback',4900,1460,2830],
  'opel mokka':['crossover',4150,1530,2560],'opel grandland':['suv',4480,1610,2680],'opel zafira':['mpv',4660,1680,2760],'opel meriva':['mpv',4290,1620,2640],'opel vivaro':['van',4960,1900,2980],
  'opel combo':['kombivan',4400,1840,2790],'opel movano':['furgon',5410,2500,3450],'opel vectra':['sedan',4600,1460,2700],
  // Ford
  'ford focus kombi':['kombi',4670,1480,2700],'ford focus':['hatch',4380,1470,2700],'ford fiesta':['hatch',4040,1480,2490],'ford mondeo':['liftback',4870,1480,2850],
  'ford kuga':['suv',4610,1680,2710],'ford puma':['crossover',4190,1540,2590],'ford s-max':['mpv',4800,1660,2850],'ford transit custom':['van',4970,1980,2930],'ford transit':['furgon',5530,2540,3300],
  'ford ranger':['pickup',5370,1880,3270],'ford mustang':['coupe',4790,1390,2720],
  // Fiat
  'fiat panda':['mini',3650,1550,2300],'fiat 500':['mini',3570,1490,2300],'fiat tipo kombi':['kombi',4570,1510,2640],'fiat tipo':['sedan',4530,1500,2640],'fiat punto':['hatch',4070,1490,2510],
  'fiat seicento':['mini',3340,1440,2200],'fiat 126p':['mini',3050,1340,1840],'fiat doblo':['kombivan',4400,1850,2750],'fiat ducato':['furgon',5410,2520,3450],'fiat bravo':['hatch',4340,1500,2600],
  // Renault, Dacia
  'renault clio':['hatch',4050,1440,2580],'renault megane':['hatch',4360,1450,2670],'renault captur':['crossover',4230,1580,2640],'renault kadjar':['suv',4490,1610,2650],
  'renault austral':['suv',4510,1620,2670],'renault scenic':['mpv',4630,1650,2800],'renault trafic':['van',5000,1970,3100],'renault master':['furgon',5550,2500,3680],
  'dacia duster':['suv',4340,1650,2660],'dacia sandero':['hatch',4090,1500,2600],'dacia logan':['sedan',4400,1500,2650],'dacia jogger':['kombi',4550,1630,2900],'dacia spring':['mini',3730,1520,2420],
  // Hyundai, Kia
  'hyundai i10':['mini',3670,1480,2430],'hyundai i20':['hatch',4040,1450,2580],'hyundai i30 kombi':['kombi',4590,1470,2650],'hyundai i30':['hatch',4340,1450,2650],
  'hyundai tucson':['suv',4500,1650,2680],'hyundai kona':['crossover',4350,1580,2660],'hyundai santa fe':['suv',4790,1700,2815],'hyundai ioniq 5':['crossover',4640,1600,3000],
  'kia picanto':['mini',3600,1480,2400],'kia rio':['hatch',4070,1450,2580],'kia ceed sw':['kombi',4600,1470,2650],'kia ceed':['hatch',4320,1450,2650],'kia sportage':['suv',4520,1650,2680],
  'kia niro':['crossover',4420,1550,2720],'kia stonic':['crossover',4140,1520,2580],'kia sorento':['suv',4810,1700,2815],'kia ev6':['crossover',4680,1550,2900],
  // BMW, Audi, Mercedes
  'bmw seria 1':['hatch',4320,1430,2670],'bmw seria 3 touring':['kombi',4710,1440,2850],'bmw seria 3':['sedan',4710,1440,2850],'bmw seria 5':['sedan',4960,1480,2980],
  'bmw x1':['suv',4500,1640,2690],'bmw x3':['suv',4710,1680,2860],'bmw x5':['suv',4920,1750,2970],'bmw 3':['sedan',4710,1440,2850],'bmw 5':['sedan',4960,1480,2980],
  'audi a3 sportback':['hatch',4340,1430,2640],'audi a3':['hatch',4340,1430,2640],'audi a4 avant':['kombi',4760,1430,2820],'audi a4':['sedan',4760,1430,2820],
  'audi a6 avant':['kombi',4940,1470,2920],'audi a6':['sedan',4940,1460,2920],'audi q3':['suv',4480,1610,2680],'audi q5':['suv',4680,1660,2820],'audi q7':['suv',5060,1740,3000],
  'mercedes-benz klasa a':['hatch',4420,1440,2730],'mercedes-benz klasa c':['sedan',4750,1440,2870],'mercedes-benz klasa e':['sedan',4950,1470,2960],'mercedes-benz glc':['suv',4720,1640,2890],
  'mercedes-benz vito':['van',5140,1910,3200],'mercedes-benz sprinter':['furgon',5930,2650,3660],'mercedes-benz tourismo':['autokar',12140,3680,6080],
  // inne popularne
  'peugeot 208':['hatch',4060,1430,2540],'peugeot 308 sw':['kombi',4640,1440,2730],'peugeot 308':['hatch',4370,1440,2680],'peugeot 2008':['crossover',4300,1550,2610],'peugeot 3008':['suv',4540,1640,2680],
  'peugeot partner':['kombivan',4400,1840,2790],'citroen c3':['hatch',4010,1480,2540],'citroen c4':['crossover',4360,1520,2670],'citroen berlingo':['kombivan',4400,1840,2790],'citroen c5 aircross':['suv',4500,1670,2730],
  'nissan qashqai':['suv',4430,1630,2670],'nissan juke':['crossover',4210,1590,2640],'nissan micra':['hatch',4000,1450,2530],'nissan x-trail':['suv',4680,1720,2700],'nissan leaf':['hatch',4490,1540,2700],
  'mazda 3':['hatch',4460,1440,2730],'mazda 6':['sedan',4870,1450,2830],'mazda cx-30':['crossover',4400,1540,2650],'mazda cx-5':['suv',4580,1680,2700],'mazda mx-5':['kabriolet',3920,1230,2310],
  'honda civic':['hatch',4550,1410,2730],'honda jazz':['mini',4090,1530,2520],'honda cr-v':['suv',4700,1680,2700],'honda hr-v':['crossover',4330,1590,2610],
  'suzuki swift':['hatch',3860,1500,2450],'suzuki vitara':['crossover',4180,1610,2500],'suzuki ignis':['mini',3700,1600,2440],'suzuki s-cross':['crossover',4300,1580,2600],
  'seat leon':['hatch',4370,1460,2690],'seat ibiza':['hatch',4060,1450,2560],'seat arona':['crossover',4150,1550,2570],'seat ateca':['suv',4380,1620,2630],'cupra formentor':['crossover',4450,1520,2680],
  'tesla model 3':['sedan',4720,1440,2880],'tesla model y':['crossover',4750,1620,2890],'volvo xc40':['suv',4440,1650,2700],'volvo xc60':['suv',4710,1660,2870],'volvo xc90':['suv',4950,1780,2980],
  'volvo v60':['kombi',4760,1430,2870],'volvo v90':['kombi',4940,1480,2940],'mitsubishi asx':['crossover',4230,1590,2640],'mitsubishi outlander':['suv',4710,1740,2710],'mitsubishi space star':['mini',3850,1520,2450],
  'lexus nx':['suv',4660,1660,2690],'lexus ux':['crossover',4500,1540,2640],'jeep renegade':['suv',4240,1690,2570],'jeep compass':['suv',4400,1640,2640],'mg zs':['crossover',4320,1640,2585],
  'byd atto 3':['crossover',4460,1620,2720],'porsche 911':['coupe',4520,1300,2450],'mini cooper':['mini',3880,1430,2500],'smart fortwo':['mini',2700,1550,1870],
 };
