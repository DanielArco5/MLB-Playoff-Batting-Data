"""Real towers the generated buildings on the city page are modelled on, roughly tallest and best known first.
One line per tower: "Name, City; code". The four-character code holds the traits the model follows:

  1. form   B box or slab        S setbacks            T tapering slab       R round tower
            O polygonal tower    W twisting tower      U bundled tubes       Y wings around a core
            L closes to a rounded tip                  N twin towers         A square turning into triangles (faceted)
            F flared tiers
  2. crown  f flat roof   m mast   t twin masts   p pyramid   c metal crown and needle
            s stepped top and mast   d dome   n spire
  3. facade 0 punched windows in masonry   1 ribbon windows   2 glass curtain wall   3 glass between metal fins
  4. colour index into PALETTE in skyline_city.py, as a letter (a = first)

These are simplified likenesses: overall form, crown, facade type and colour follow the real tower; exact
proportions and details do not. The twelve landmark models (Burj Khalifa etc.) are separate and not listed here."""

TOWERS = """
Merdeka 118, Kuala Lumpur; An3a
Abraj Al-Bait Clock Tower, Mecca; Sn0h
Ping An Finance Centre, Shenzhen; Tn3n
Lotte World Tower, Seoul; Lf2a
Guangzhou CTF Finance Centre, Guangzhou; Sm3j
Tianjin CTF Finance Centre, Tianjin; Lf2a
CITIC Tower (China Zun), Beijing; Tf2n
Shanghai World Financial Center, Shanghai; Tf2l
International Commerce Centre, Hong Kong; Tf2d
Wuhan Greenland Center, Wuhan; Lf2a
Central Park Tower, New York; Sf2a
Lakhta Center, St Petersburg; Wn2l
Landmark 81, Ho Chi Minh City; Un2l
The Exchange 106, Kuala Lumpur; Bp2l
Changsha IFS Tower T1, Changsha; Bm2a
Zifeng Tower, Nanjing; Tn2a
KK100, Shenzhen; Bd2a
Guangzhou International Finance Center, Guangzhou; Lf2a
111 West 57th Street, New York; Sf3m
One Vanderbilt, New York; Tn2a
432 Park Avenue, New York; Bf0j
Marina 101, Dubai; Bn2l
Trump International Hotel and Tower, Chicago; Sn2a
Jin Mao Tower, Shanghai; Fn3n
Princess Tower, Dubai; Od0h
Al Hamra Tower, Kuwait City; Wf2c
Two International Finance Centre, Hong Kong; Tc2a
CITIC Plaza, Guangzhou; Bt2l
Shun Hing Square, Shenzhen; Bt2g
23 Marina, Dubai; Op0h
Elite Residence, Dubai; Sd0h
Central Plaza, Hong Kong; Op2o
Goldin Finance 117, Tianjin; Tp2a
Bank of China Tower, Hong Kong; At2a
Bank of America Tower, New York; Am2a
Almas Tower, Dubai; Bm2l
The Pinnacle, Guangzhou; Tn2a
Emirates Office Tower, Dubai; An2n
85 Sky Tower, Kaohsiung; Nm2d
Aon Center, Chicago; Bf0j
The Center, Hong Kong; Om2a
ADNOC Headquarters, Abu Dhabi; Bf2a
Comcast Technology Center, Philadelphia; Sm2a
Wilshire Grand Center, Los Angeles; Tm2a
Mercury City Tower, Moscow; Sf2m
Rose Rayhaan by Rotana, Dubai; Bn2a
China World Trade Center Tower III, Beijing; Tf3a
Ryugyong Hotel, Pyongyang; Yn2l
Keangnam Hanoi Landmark Tower, Hanoi; Bf2l
Al Yaqoub Tower, Dubai; Sn0h
The Index, Dubai; Bf1h
The Landmark, Abu Dhabi; Rf2a
Q1, Gold Coast; Rn2l
Burj Al Arab, Dubai; Tm2j
Nina Tower, Hong Kong; Bf2a
New York Times Building, New York; Bm3c
Bank of America Plaza, Atlanta; Sp0r
U.S. Bank Tower, Los Angeles; Os1c
Menara Telekom, Kuala Lumpur; Tf2j
Jumeirah Emirates Towers Hotel, Dubai; An2d
One57, New York; Sf2l
Franklin Center, Chicago; Ss0r
JPMorgan Chase Tower, Houston; Bf0c
Baiyoke Tower II, Bangkok; Sm0h
Two Prudential Plaza, Chicago; Sp1c
Wells Fargo Plaza, Houston; Bf2g
Kingdom Centre, Riyadh; Tf2a
The Address Downtown, Dubai; Sn2c
Capital City Moscow Tower, Moscow; Uf2c
Gate to the East, Suzhou; Nf2a
First Canadian Place, Toronto; Bt0j
Eureka Tower, Melbourne; Sf2l
Comcast Center, Philadelphia; Bf2a
Yokohama Landmark Tower, Yokohama; Tf0c
Emirates Crown, Dubai; Bd2l
311 South Wacker Drive, Chicago; Od0r
SEG Plaza, Shenzhen; Ot2l
70 Pine Street, New York; Sn0b
Key Tower, Cleveland; Sp0c
Plaza 66, Shanghai; Bd2a
One Liberty Place, Philadelphia; Sc2l
Columbia Center, Seattle; Uf2k
Tomorrow Square, Shanghai; Ap2a
Cheung Kong Center, Hong Kong; Bf2a
40 Wall Street, New York; Sp0b
Bank of America Plaza, Dallas; Af2l
Citigroup Center, New York; Bf1j
Scotia Plaza, Toronto; Sf0r
Williams Tower, Houston; Sp2d
Republic Plaza, Singapore; Af2d
UOB Plaza One, Singapore; Af0c
One Raffles Place, Singapore; Af1c
Renaissance Tower, Dallas; Bt2l
Bank of America Corporate Center, Charlotte; Sc0h
Federation Tower, Moscow; Nm2l
Gran Torre Santiago, Santiago; Tn2a
Australia 108, Melbourne; Bf2p
30 Hudson Yards, New York; Tf2a
Salesforce Tower, San Francisco; Lf3a
Abeno Harukas, Osaka; Sf2a
MahaNakhon, Bangkok; Sf2n
Bitexco Financial Tower, Ho Chi Minh City; Lf2d
Azabudai Hills Mori JP Tower, Tokyo; Tf2n
China Resources Headquarters, Shenzhen; Lf3n
Hanking Center, Shenzhen; Tf3d
Shimao International Plaza, Shanghai; At2d
Iconic Tower, New Administrative Capital; Lf2n
Mohammed VI Tower, Rabat; Lf2l
PIF Tower, Riyadh; Af2n
Al Faisaliyah Center, Riyadh; Td3n
Aspire Tower, Doha; Rn3n
Doha Tower, Doha; Lf3n
Tornado Tower, Doha; Rf2l
Bahrain World Trade Center, Manama; Nn2a
Cayan Tower, Dubai; Wf2n
JW Marriott Marquis, Dubai; Nm2l
Ocean Heights, Dubai; Wf2l
The Torch, Dubai; Bd2l
Burj Mohammed Bin Rashid, Abu Dhabi; Tf2l
Etihad Towers Tower 2, Abu Dhabi; Tf2f
Capital Gate, Abu Dhabi; Wf2a
Four Seasons Place, Kuala Lumpur; Bf2l
Menara Maybank, Kuala Lumpur; Tf1j
Marina Bay Sands, Singapore; Nf2a
Guoco Tower, Singapore; Bf2f
Wisma 46, Jakarta; Tn2l
One Canada Square, London; Bp3n
22 Bishopsgate, London; Af2a
Heron Tower, London; Sm2a
Leadenhall Building, London; Tf2a
20 Fenchurch Street, London; Bf3a
Tower 42, London; Uf1k
8 Canada Square, London; Bf2d
One Blackfriars, London; Rf2a
Commerzbank Tower, Frankfurt; Om2c
Messeturm, Frankfurt; Sp0r
Westendstrasse 1, Frankfurt; Bc0j
Main Tower, Frankfurt; Rm2l
Tour First, Paris; Tf2a
Tour Montparnasse, Paris; Bf1k
Torre de Cristal, Madrid; Af2a
Torre Cepsa, Madrid; Bf3n
Torre Emperador, Madrid; Wf2a
Torre Glories, Barcelona; Lf2l
Turning Torso, Malmo; Wm0j
OKO Tower, Moscow; Bf2a
Evolution Tower, Moscow; Wf2l
UniCredit Tower, Milan; Rn2a
Varso Tower, Warsaw; Bm2a
Palace of Culture and Science, Warsaw; Sn0b
Moscow State University Main Building, Moscow; Sn0b
Istanbul Sapphire, Istanbul; Bf2l
Azrieli Sarona Tower, Tel Aviv; Wf2l
Azrieli Center Circular Tower, Tel Aviv; Rf1j
Northeast Asia Trade Tower, Incheon; Af2a
63 Building, Seoul; Tf2o
Parc1 Tower, Seoul; Bm2i
Tokyo Metropolitan Government Building, Tokyo; Ns0c
Mode Gakuen Cocoon Tower, Tokyo; Lf2j
Roppongi Hills Mori Tower, Tokyo; Rf2n
Toranomon Hills Mori Tower, Tokyo; Af2a
Tokyo Midtown Tower, Tokyo; Bf3c
Sunshine 60, Tokyo; Bf0c
NTT Docomo Yoyogi Building, Tokyo; Sn0c
Shinjuku Park Tower, Tokyo; Up0c
Umeda Sky Building, Osaka; Nf2a
Osaka Prefectural Government Sakishima Building, Osaka; Bm2a
Midland Square, Nagoya; Bf2a
Mode Gakuen Spiral Towers, Nagoya; Wf2a
JR Central Towers, Nagoya; Nf0c
Taipei Nan Shan Plaza, Taipei; Tf2a
Shin Kong Life Tower, Taipei; Sp0r
Grand Lisboa, Macau; Fn2o
HSBC Main Building, Hong Kong; Sf3n
Lippo Centre, Hong Kong; Nf2l
Hopewell Centre, Hong Kong; Rf1j
One Island East, Hong Kong; Bf2a
Langham Place, Hong Kong; Bd2a
Jardine House, Hong Kong; Bf0n
Bund Center, Shanghai; Bc0h
Pearl River Tower, Guangzhou; Bf3a
The Sail at Marina Bay, Singapore; Tf2a
Swissotel The Stamford, Singapore; Rf1j
World One, Mumbai; Yf2a
The Imperial, Mumbai; Nn0c
Flame Towers, Baku; Lf2l
SOCAR Tower, Baku; Wf2l
Carlton Centre, Johannesburg; Bf0c
Ponte City, Johannesburg; Rf0c
The Leonardo, Johannesburg; Bf2a
Britam Tower, Nairobi; Am2a
Torre Reforma, Mexico City; Af0c
Torre BBVA Mexico, Mexico City; Bf3a
Torre Mayor, Mexico City; Bf2g
Torre Latinoamericana, Mexico City; Sm1a
Torre KOI, Monterrey; Bf2a
Titanium La Portada, Santiago; Bm2l
Mirante do Vale, Sao Paulo; Bf1c
Edificio Italia, Sao Paulo; Of1c
Altino Arantes Building, Sao Paulo; Sm0j
Yachthouse Residence Club, Balneario Camboriu; Nf2a
Alvear Tower, Buenos Aires; Bf0b
Kavanagh Building, Buenos Aires; Sf0j
Torre Colpatria, Bogota; Bf0c
BD Bacata, Bogota; Nf2a
JW Marriott Panama, Panama City; Tf2j
F&F Tower, Panama City; Wf2g
Rialto Towers, Melbourne; Nf2l
120 Collins Street, Melbourne; Sm0c
101 Collins Street, Melbourne; Sm0r
Crown Sydney, Sydney; Wf2j
Chifley Tower, Sydney; Sm0c
Citigroup Centre, Sydney; Bm2l
Deutsche Bank Place, Sydney; Bt2a
Governor Phillip Tower, Sydney; Bc0c
MLC Centre, Sydney; Of0j
Australia Square Tower, Sydney; Rf1j
Central Park, Perth; Sm3n
108 St Georges Terrace, Perth; Af3j
Infinity Tower, Brisbane; Bf2l
1 William Street, Brisbane; Bf2d
Riparian Plaza, Brisbane; Bm2a
Soul, Gold Coast; Tf2a
Vero Centre, Auckland; Bd2a
TD Canada Trust Tower, Toronto; Sm2a
Commerce Court West, Toronto; Bf3n
Toronto-Dominion Bank Tower, Toronto; Bf3k
Aura, Toronto; Sf2a
St. Regis Toronto, Toronto; Sn2a
Royal Bank Plaza South Tower, Toronto; Af2o
L Tower, Toronto; Tf2f
1000 de La Gauchetiere, Montreal; Sp0c
1250 Rene-Levesque, Montreal; Bm2a
Tour de la Bourse, Montreal; Bf3k
Place Ville Marie, Montreal; Yf3n
The Bow, Calgary; Af3a
Brookfield Place, Calgary; Rf2a
Telus Sky, Calgary; Wf2a
Suncor Energy Centre, Calgary; Bf2g
Stantec Tower, Edmonton; Sf2a
Living Shangri-La, Vancouver; Af2a
Woolworth Building, New York; Sp0j
30 Rockefeller Plaza, New York; Sf0b
MetLife Building, New York; Of1c
Seagram Building, New York; Bf3m
Lever House, New York; Bf2g
Flatiron Building, New York; Af0b
Hearst Tower, New York; Af3n
8 Spruce Street, New York; Sf3n
3 World Trade Center, New York; Bt2a
4 World Trade Center, New York; Af2f
7 World Trade Center, New York; Bf2f
35 Hudson Yards, New York; Sf0c
15 Hudson Yards, New York; Uf2a
53W53, New York; Tn2k
220 Central Park South, New York; Sf0b
56 Leonard Street, New York; Sf2f
425 Park Avenue, New York; Sm2a
The Spiral, New York; Sf2d
270 Park Avenue, New York; Sf3m
One Worldwide Plaza, New York; Sp0i
383 Madison Avenue, New York; Od0c
CitySpire, New York; Od0c
Trump World Tower, New York; Bf2m
Metropolitan Life Insurance Company Tower, New York; Sp0j
New York Life Building, New York; Sp0b
Lipstick Building, New York; Rs1r
550 Madison Avenue, New York; Bp0r
28 Liberty Street, New York; Bf3n
The Brooklyn Tower, New York; On3k
Williamsburgh Savings Bank Tower, New York; Sd0b
One Court Square, New York; Sf2g
General Electric Building, New York; Sc0i
Chanin Building, New York; Sf0i
20 Exchange Place, New York; Sf0b
500 Fifth Avenue, New York; Sf0c
One Grand Central Place, New York; Sf0i
American Radiator Building, New York; Sc0k
One Wall Street, New York; Sf0c
Manhattan Municipal Building, New York; Sd0b
The San Remo, New York; Nd0b
Waldorf Astoria, New York; Sd0c
900 North Michigan, Chicago; Ss0b
Water Tower Place, Chicago; Bf0j
Chase Tower, Chicago; Tf0c
Park Tower, Chicago; Sp0b
Aqua, Chicago; Bf1j
St. Regis Chicago, Chicago; Uf2g
Marina City, Chicago; Nf1j
Lake Point Tower, Chicago; Yf2k
330 North Wabash, Chicago; Bf3k
Tribune Tower, Chicago; Sc0b
Wrigley Building, Chicago; Sn0j
Carbide and Carbon Building, Chicago; Sn0k
Chicago Board of Trade Building, Chicago; Sp0b
333 Wacker Drive, Chicago; Bf2g
77 West Wacker Drive, Chicago; Bp0c
150 North Riverside, Chicago; Tf2a
One Museum Park, Chicago; Sf2l
NEMA Chicago, Chicago; Uf2k
One Prudential Plaza, Chicago; Bm0b
Crain Communications Building, Chicago; Af1j
One Magnificent Mile, Chicago; Uf0r
35 East Wacker, Chicago; Sd0b
Palmolive Building, Chicago; Sm0b
Mather Tower, Chicago; On0j
Aon Center, Los Angeles; Bf3k
Two California Plaza, Los Angeles; Af2a
Gas Company Tower, Los Angeles; Sf2l
777 Tower, Los Angeles; Bf3j
Los Angeles City Hall, Los Angeles; Sp0j
181 Fremont, San Francisco; Tm3a
555 California Street, San Francisco; Bf1h
345 California Center, San Francisco; St0c
One Rincon Hill, San Francisco; Bd2a
101 California Street, San Francisco; Rf2a
140 New Montgomery, San Francisco; Sf0j
1201 Third Avenue, Seattle; Sp0r
Two Union Square, Seattle; Bf2c
Seattle Municipal Tower, Seattle; Bd2c
Smith Tower, Seattle; Sp0j
Rainier Square Tower, Seattle; Tf2a
TC Energy Center, Houston; Sp0r
Heritage Plaza, Houston; Bs2c
Pennzoil Place, Houston; Nf3k
One Shell Plaza, Houston; Bm0j
609 Main at Texas, Houston; Bf2a
Niels Esperson Building, Houston; Sd0b
Comerica Bank Tower, Dallas; Sd0c
Fountain Place, Dallas; Af2g
Trammell Crow Center, Dallas; Sp0c
Truist Plaza, Atlanta; Ss0c
One Atlantic Center, Atlanta; Sp0r
191 Peachtree Tower, Atlanta; Sd0r
Westin Peachtree Plaza, Atlanta; Rf2k
Georgia-Pacific Tower, Atlanta; Sf0r
Two Liberty Place, Philadelphia; Sc2d
BNY Mellon Center, Philadelphia; Sp0r
Three Logan Square, Philadelphia; Ss0r
Philadelphia City Hall, Philadelphia; Sd0j
PSFS Building, Philadelphia; Bf0k
200 Clarendon Street, Boston; Af2l
Prudential Tower, Boston; Bm3c
One Dalton, Boston; Rf2f
Custom House Tower, Boston; Sp0c
U.S. Steel Tower, Pittsburgh; Of3i
PPG Place, Pittsburgh; Sn2k
Fifth Avenue Place, Pittsburgh; Sp0r
Cathedral of Learning, Pittsburgh; Sf0b
Gulf Tower, Pittsburgh; Sp0b
Terminal Tower, Cleveland; Sn0b
200 Public Square, Cleveland; Bf0r
Erieview Tower, Cleveland; Bf3k
Renaissance Center, Detroit; Rf2k
Ally Detroit Center, Detroit; Ss0r
Penobscot Building, Detroit; Sm0b
Guardian Building, Detroit; Sf0i
Fisher Building, Detroit; Sp0b
IDS Center, Minneapolis; Af2l
Capella Tower, Minneapolis; Rd2a
Wells Fargo Center, Minneapolis; Ss0h
Foshay Tower, Minneapolis; Tm0b
Duke Energy Center, Charlotte; Af2a
One Wells Fargo Center, Charlotte; Bd0r
Southeast Financial Center, Miami; Sf0j
Miami Tower, Miami; Ss2a
One Thousand Museum, Miami; Bf3j
Republic Plaza, Denver; Bf0c
Wells Fargo Center, Denver; Bd0r
One America Plaza, San Diego; Op2a
Salesforce Tower, Indianapolis; St0h
Devon Energy Center, Oklahoma City; Rf2a
BOK Tower, Tulsa; Bf3n
One Kansas City Place, Kansas City; Ss0c
Kansas City Power and Light Building, Kansas City; Sn0b
Metropolitan Square, St. Louis; Sp0r
Carew Tower, Cincinnati; Sf0h
Great American Tower, Cincinnati; Sc2a
LeVeque Tower, Columbus; Sn0j
AT&T Building, Nashville; St0c
U.S. Bank Center, Milwaukee; Bf3j
U.S. Bancorp Tower, Portland; Af2r
Frost Bank Tower, Austin; Sc2a
The Independent, Austin; Uf2a
30 Hudson Street, Jersey City; Tf2a
Buffalo City Hall, Buffalo; Sd0h
Nebraska State Capitol, Lincoln; Sd0b
Royal Liver Building, Liverpool; Nd0c
Beetham Tower, Manchester; Bf2a
Tour Part-Dieu, Lyon; Rp0r
Torre Picasso, Madrid; Bf3j
Hotel Arts, Barcelona; Bf3j
Torre Sevilla, Seville; Rf3i
Bosco Verticale, Milan; Bf1q
Pirelli Tower, Milan; Bf1c
Generali Tower, Milan; Wf2a
DC Tower 1, Vienna; Bf2k
Post Tower, Bonn; Rf2a
De Rotterdam, Rotterdam; Uf2a
Prime Tower, Zurich; Af2g
Roche Tower, Basel; Sf1j
Warsaw Spire, Warsaw; Rn2a
Zlota 44, Warsaw; Tf2a
Hotel Ukraina, Moscow; Sn0b
Latvian Academy of Sciences, Riga; Sn0i
Avaz Twist Tower, Sarajevo; Wm2l
Boerentoren, Antwerp; Sf0b
Edificio Espana, Madrid; Sf0i
Palacio Barolo, Buenos Aires; Sd0c
Palacio Salvo, Montevideo; Sd0c
Marine Building, Vancouver; Sp0h
Commerce Court North, Toronto; Sf0b
Sun Life Building, Montreal; Sf0c
Park Hotel, Shanghai; Sf0i
Manchester Unity Building, Melbourne; Sn0j
"""

FORMS = {"S": 0, "T": 1, "R": 2, "O": 2, "W": 3, "U": 4, "Y": 5, "L": 6, "N": 7, "A": 8, "F": 9, "B": 10}
CROWNS = "fmtpcsdn"


def load(n_palette):
    """[(name, [form, crown, facade, colour, sides])] in file order; raises on a bad or repeated line."""
    out, seen = [], set()
    for line in TOWERS.strip().splitlines():
        name, code = (part.strip() for part in line.rsplit(";", 1))
        form, crown, facade, colour = code
        tint = ord(colour) - ord("a")
        if name in seen or form not in FORMS or crown not in CROWNS or facade not in "0123" or not 0 <= tint < n_palette:
            raise ValueError(f"bad or repeated tower line: {line}")
        seen.add(name)
        out.append((name, [FORMS[form], CROWNS.index(crown), int(facade), tint, 16 if form == "R" else 0]))
    return out
