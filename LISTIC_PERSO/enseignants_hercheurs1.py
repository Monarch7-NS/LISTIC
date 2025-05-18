
import requests
from bs4 import BeautifulSoup as bs

def make_soup(url):
    html = requests.get(url).content
    soup = bs(html,"html.parser")
    return soup

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/ilham-alloui/")
data1 ={}
data1["name"] = soup.find_all("h1")[0].text
data1["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data1["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data1["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data1["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data1["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/ilham-alloui/"
data1

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/khadija-arfaoui")
data2 ={}
data2["name"] = soup.find_all("h1")[0].text
data2["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data2["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data2["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data2["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data2["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/khadija-arfaoui"
data2

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/abdourrahmane-atto/")
data3 ={}
data3["name"] = soup.find_all("h1")[0].text
data3["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data3["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data3["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data3["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data3["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/abdourrahmane-atto/"
data3

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/alexandre-benoit/")
data4 = {}
data4["name"] = soup.find_all("h1")[0].text
data4["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data4["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()[:-12]
data4["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data4["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data4["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/alexandre-benoit/"
data4

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/eric-benoit-fr/")
data5 = {}
data5["name"] = soup.find_all("h1")[0].text
data5["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data5["phone"] = [soup.find_all("p")[2].text.split(":")[1].strip()[:-1], soup.find_all("p")[3].text.split(":")[1].strip()]
data5["office"] = soup.find_all("p")[4].text.split(":")[1].strip()
data5["address"] = soup.find_all("p")[5].text.split(":")[1].strip()
data5["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/eric-benoit-fr/"
data5

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/lamia-amel-berrah/")
data6 = {}
data6["name"] = soup.find_all("h1")[0].text
data6["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data6["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data6["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data6["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data6["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/lamia-amel-berrah/"
data6

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/mickael-bettinelli/")
data7 = {}
data7["name"] = soup.find_all("h1")[0].text
data7["email"] = soup.find_all("p")[0].text.split(":")[1].strip().replace("at","@").replace(" dot ",".")
data7["website"] = soup.find_all("h3")[2].a.get("href")
data7["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/mickael-bettinelli/"
data7

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/argheesh-bhanot/")
data8 = {}
data8["name"] = soup.find_all("h1")[0].text
data8["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data8["office"] = soup.find_all("p")[1].text.split(":")[1].strip()
data8["address"] = soup.find_all("p")[2].text.split(":")[1].strip().replace("\xa0"," ")
data8["Theme"] = soup.find_all("p")[3].text.split(":")[1].strip()
data8["website"] = soup.find_all("p")[4].text.split("b :")[1].strip()
data8["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/argheesh-bhanot/"
data8

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/julien-boissiere/")
data9 = {}
data9["name"] = soup.find_all("h1")[0].text
data9["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data9["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data9["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data9["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data9["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/julien-boissiere/"
data9

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/reda-boukezzoula/")
data10 = {}
data10["name"] = soup.find_all("h1")[0].text
data10["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data10["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data10["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data10["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data10["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/reda-boukezzoula/"
data10

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/sorana-cimpan/")
data11 = {}
data11["name"] = soup.find_all("h1")[0].text
data11["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data11["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data11["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data11["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data11["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/sorana-cimpan/"
data11

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/didier-coquin/")
data12 = {}
data12["name"] = soup.find_all("h1")[0].text
data12["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data12["phone"] = [soup.find_all("p")[2].text.split(":")[1].strip(),soup.find_all("p")[2].text.split(":")[2].strip()]
data12["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data12["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data12["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/didier-coquin/"
data12

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/vincent-couturier/")
data13 = {}
data13["name"] = soup.find_all("h1")[0].text
data13["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data13["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data13["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data13["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data13["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/vincent-couturier/"
data13

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/luc-damas/")
data14 = {}
data14["name"] = soup.find_all("h1")[0].text
data14["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data14["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data14["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data14["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data14["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/luc-damas/"
data14

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/yves-dumond/")
data15 = {}
data15["name"] = soup.find_all("h1")[0].text
data15["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data15["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data15["office"] = soup.find_all("p")[2].text.split(":")[1].strip().replace("\xa0"," ")
data15["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data15["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/yves-dumond/"
data15

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/guillaume-ginolhac/")
data16 = {}
data16["name"] = soup.find_all("h1")[0].text
data16["email"] = soup.find("div",id="c10273").find_all("ul")[4].find_all("li")[0].text.split(":")[1].strip()
data16["phone"] = soup.find("div",id="c10273").find_all("ul")[4].find_all("li")[1].text.split(":")[1].strip()
data16["office"] = soup.find("div",id="c10273").find_all("ul")[4].find_all("li")[2].text.split(":")[1].strip()
data16["address"] = soup.find("div",id="c10273").find_all("ul")[4].find_all("li")[3].text.split(":")[1].strip()
data16["fax"] = soup.find("div",id="c10273").find_all("ul")[4].find_all("li")[1].text.split(":")[2].strip()
data16

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/marc-philippe-huget/")
data17 = {}
data17["name"] = soup.find_all("h1")[0].text
data17["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data17["phone"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[1].text.split(":")[2].strip()]
data17["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data17["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data17["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/marc-philippe-huget/"
data17

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/antoine-lavault/")
data18 = {}
data18["name"] = soup.find_all("h1")[0].text
data18["email"] = soup.find_all("p")[0].text.split(":")[1].strip().replace("at","@").replace(" dot ",".")
data18["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data18["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data18["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data18["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/antoine-lavault/"
data18

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/christophe-lin-kwong-chon/")
data19 = {}
data19["name"] = soup.find_all("h1")[0].text

data19["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data19["address"] = [soup.find_all("p")[1].text.split(":")[1].strip(),soup.find_all("p")[2].text.split(":")[1].strip()]
data19["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/christophe-lin-kwong-chon/"
data19

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/faiza-loukil/")
data20 = {}
data20["name"] = soup.find_all("h1")[0].text
data20["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data20["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data20["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data20["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data20["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/faiza-loukil/"
data20

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/nicolas-meger-2/")
data21 = {}
data21["name"] = soup.find_all("h1")[0].text
data21["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data21["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data21["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data21["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data21["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/nicolas-meger-2/"
data21

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/yassine-mhiri/")
data22 = {}
data22["name"] = soup.find_all("h1")[0].text
data22["email"] = soup.find_all("p")[-5].text.split(":")[1].strip()
data22["github"] = soup.find_all("p")[-4].text.split(":")[1].strip()
data22["address"] = soup.find_all("p")[-3].text.split(":")[1].strip()
data22["url_listic"] = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/yassine-mhiri/"
data22

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/ammar-mian-fr/")
data23 = {}

data23["name"] = soup.find_all("h1")[0].text
data23["email"] = soup.find_all("p")[2].text.split(":")[1].strip()
data23["phone"] = soup.find_all("p")[3].text.split(":")[1].strip()
data23["office"] = soup.find_all("p")[4].text.split(":")[1].strip()
data23["address"] = soup.find_all("p")[5].text.split(":")[1].strip()
data23["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/ammar-mian-fr/"
data23

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/sebastien-monnet-fr/")
data24 = {}
data24["name"] = soup.find_all("h1")[0].text
data24["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data24["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data24["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data24["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data24["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/sebastien-monnet-fr/"
data24

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/stephane-perrin-fr/")
data25 = {}
data25["name"] = soup.find_all("h1")[0].text
data25["email"] = soup.find_all("p")[1].decode_contents().split('<br/>')[0].split(":")[1].strip()
data25["phone"] = soup.find_all("p")[1].decode_contents().split('<br/>')[1].split(":")[1].strip()
data25["fax"] = soup.find_all("p")[1].decode_contents().split('<br/>')[1].split(":")[2].strip()
data25["office"] = soup.find_all("p")[1].decode_contents().split('<br/>')[2].split(":")[1].strip()
data25["address"] = soup.find_all("p")[1].decode_contents().split('<br/>')[3].split(":")[1].strip()
data25["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/stephane-perrin-fr/"
data25

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/stephan-plassart/")
data26 = {}
data26["name"] = soup.find_all("h1")[0].text
data26["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data26["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data26["HAL"] = soup.find_all("p")[2].a.get("href")
data26["web"] = soup.find_all("p")[3].a.get("href")
data26["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/stephan-plassart/"
data26

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/frederic-pourraz/")
data27 = {}
data27["name"] = soup.find_all("h1")[0].text
data27["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data27["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data27["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data27["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data27["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/frederic-pourraz/"
data27

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/jean-yves-ramel/")
data28 = {}
data28["name"] = soup.find_all("h1")[0].text
data28["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data28["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data28["web"] = soup.find_all("p")[2].find_all("a")[0].get("href")
data28["HAL"] = soup.find_all("p")[2].find_all("a")[2].get("href")
data28["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data28["address"] = soup.find_all("p")[4].text.split(":")[1].strip().replace("\n"," ")
data28["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/jean-yves-ramel/"
data28

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/kave-salamatian/")
data29 = {}
data29["name"] = soup.find_all("h1")[0].text
data29["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data29["web"] = soup.find_all("p")[1].a.get("href")
data29["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data29["fax"] = soup.find_all("p")[2].text.split(":")[2].strip()
data29["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data29["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data29["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/kave-salamatian/"
data29

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/david-telisson/")
data30 = {}
data30["name"] = soup.find_all("h1")[0].text
data30["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data30["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data30["address"] = soup.find_all("p")[2].text.split(":")[1].strip()
data30["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/david-telisson/"
data30

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/emmanuel-trouve-fr/")
data31 = {}
data31["name"] = soup.find_all("h1")[0].text
data31["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data31["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data31["fax"] = soup.find_all("p")[2].text.split(":")[2].strip()
data31["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data31["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data31["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/emmanuel-trouve-fr/"
data31

soup = make_soup("https://www.univ-smb.fr/listic/pages-fr/lionel-valet-fr/")
data32 = {}
data32["name"] = soup.find_all("h1")[0].text
data32["email"] = soup.find_all("p")[1].text.split(":")[1].strip()
data32["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data32["fax"] = soup.find_all("p")[2].text.split(":")[2].strip()
data32["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data32["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data32["url_listic"] = "https://www.univ-smb.fr/listic/pages-fr/lionel-valet-fr/"
data32

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/herve-verjus/")
data33 = {}
data33["name"] = soup.find_all("h1")[0].text
data33["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data33["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data33["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data33["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data33["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/herve-verjus/"
data33

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/flavien-vernier/")
data34 = {}
data34["name"] = soup.find_all("h1")[0].text


html_content = '''
<p class="bodytext">E-mail: <span style="font-weight: bold">flavien -POINT- vernier -AROBAS- univ-smb -POINT- fr<br/>
 Telephone:</span> <span style="font-weight: bold">+33(0) 4 50 09 65 90</span> - fax: <span style="font-weight: bold">+33(0) 4 50 09 65 59<br/>
 Office:</span> <span style="font-weight: bold">A227<br/>
 Address:</span> <span style="font-weight: bold">LISTIC - Polytech Annecy-Chambéry, BP 80439, </span><span style="font-weight: bold">Annecy le Vieux, </span><span style="font-weight: bold">74944 </span><span style="font-weight: bold"> </span><span style="font-weight: bold">Annecy </span><span style="font-weight: bold">Cedex, France</span></p>
'''

# Parser le contenu HTML
soup = bs(html_content, 'html.parser')

# Trouver la balise avec la classe "bodytext"
bodytext = soup.find('p', class_='bodytext')

# Dictionnaire pour stocker les données extraites
data = {}

if bodytext:
    # Transformer le contenu de la balise en texte brut
    raw_content = bodytext.decode_contents()

    # Extraction des données
    data34['email'] = raw_content.split('E-mail:')[1].split('<br/>')[0].strip()
    data34['Telephone'] = raw_content.split('Telephone:</span>')[1].split('</span>')[0].strip()
    data34['Fax'] = raw_content.split('fax:')[1].split('<br/>')[0].strip()
    data34['Office'] = raw_content.split('Office:</span>')[1].split('<br/>')[0].strip()
    data34['Address'] = raw_content.split('Address:</span>')[1].split('</span>')[0].strip()
    data34['url_listic'] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/flavien-vernier/"



data34

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/yajing-yan-fr/")
data35 = {}
data35["name"] = soup.find_all("h1")[0].text
data35["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data35["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data35["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data35["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data35["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/yajing-yan-fr/"
data35

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/philippe-bolon/")
data36 = {}

data36["name"] = soup.find_all("h1")[0].text
data36["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data36["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data36["fax"] = soup.find_all("p")[1].text.split(":")[2].strip()
data36["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data36["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data36["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/philippe-bolon/"
data36

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/collaborateurs-benevoles/richard-dapoigny/")
data37 = {}
data37["name"] = soup.find_all("h1")[0].text
data37["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data37["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data37["address"] = soup.find_all("p")[2].text.split(":")[1].strip()
data37["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/collaborateurs-benevoles/richard-dapoigny/"
data37

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/laurent-foulloy/")
data38 = {}
data38["name"] = soup.find_all("h1")[0].text
data38["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data38["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data38["fax"] = soup.find_all("p")[1].text.split(":")[2].strip()
data38["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data38["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data38["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/laurent-foulloy/"
data38

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/gilles-mauris/")
data39 = {}
data39["name"] = soup.find_all("h1")[0].text
data39["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data39["phone"] = soup.find_all("p")[1].text.split(":")[1].strip()
data39["fax"] = soup.find_all("p")[1].text.split(":")[2].strip()
data39["office"] = soup.find_all("p")[2].text.split(":")[1].strip()
data39["address"] = soup.find_all("p")[3].text.split(":")[1].strip()
data39["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/gilles-mauris/"
data39

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/christophe-roche/")
data40 = {}
data40["name"] = soup.find_all("h1")[0].text
data40["email"] = soup.find_all("p")[0].text.split(":")[1].strip()
data40["web"] = soup.find_all("p")[1].a.get("href")
data40["phone"] = soup.find_all("p")[2].text.split(":")[1].strip()
data40["fax"] = soup.find_all("p")[2].text.split(":")[2].strip()
data40["office"] = soup.find_all("p")[3].text.split(":")[1].strip()
data40["address"] = soup.find_all("p")[4].text.split(":")[1].strip()
data40["url_listic"] = "https://www.univ-smb.fr/listic/en/presentation_listic/membres/enseignants-chercheurs/christophe-roche/"
data40

import json

# Créer un dictionnaire contenant les données structurées
all_data = {
    "enseignants_chercheurs": [
        data1, data2, data3, data4, data5, data6, data7, data8, data9, data10,
        data11, data12, data13, data14, data15, data16, data17, data18, data19, data20,
        data21, data22, data23, data24, data25, data26, data27, data28, data29, data30,
        data31, data32, data33, data34, data35
    ],
    "émérite": [
        data36, data37, data38, data39, data40
    ]
}

# Enregistrer les données dans un fichier JSON
with open("data/Enseignants.json", "w", encoding="utf-8") as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)