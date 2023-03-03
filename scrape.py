
import os
import requests
import json
from lxml import etree, html
from html.parser import HTMLParser

DEBUG = False

def ensure_jan_1():
    if not os.path.exists("ohrid/content/jan_1.html"):
        r = requests.get("https://web.archive.org/web/20170502150951/http://westserbdio.org/en/prologue/363-january-1")
        with open("ohrid/content/jan_1.html", "w") as f:
            f.write(r.text)

def parse_calendar(start, end):
    calendar = []
    for line in data[start:end].split("\n"):
        if '<div align="center"' in line and '<a href=' in line:
            link = "https://web.archive.org" + line[line.find('<a href="')+9:line.find("title=")-2]
            date = line[line.find('<a href="')+68:line.find("title=")-2]
            calendar.append({
                "date": date,
                "link": link,
            })
    return calendar

def get_content(date, link):
    global DEBUG

    if not "-" in date:
        return

    raw = "ohrid/content/raw/"+date+".html"
    if not os.path.exists(raw):
        r = requests.get(link)
        with open(raw, "w") as f:
            f.write(r.text)
    
    with open(raw) as f:
        data = f.read()

    start_options = [
        '<div style="text-align: left;',
        '<p style="text-align: left;',
        '<span style="color: #800000;',
        '<span class="article-text" style="color: #800000;',
    ]

    start = len(data)
    for o in start_options:
        s = data.find(o)
        start = s if 0 < s and s < start else start
    
    data = data[start:]
    data = data[:data.find('bt-social-share bt-social-share-below')]
    data = data.split("\n")
    data = data[:-1] if ">&nbsp;</p>" in data[-1] else data
    data = "".join(data)
    data = data.replace('\u00a0', " ")

    # Pretty
    data = etree.tostring(html.fromstring(data), encoding='unicode', pretty_print=True)

    if DEBUG:
        print(data)

    p = Parser()
    p.feed(data)
    p.write("ohrid/content/json/"+date+".json")

    DEBUG = False
    
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = "saints"

        self.s_state = ""
        self.s_data = []

        self.hm_state = ""
        self.hm_data = {"title": [""], "data": []}

        self.r_state = ""
        self.r_data = []

        self.c_state = ""
        self.c_data = {"title": "", "data": []}

        self.h_state = ""
        self.h_data = {"quote": "", "data": []}

    def handle_starttag(self, tag, attrs):
        if self.state == "saints":
            self.saint_state_machine(tag=tag, attrs=attrs)
        elif self.state == "hymn_of_praise":
            self.hymn_of_praise_state_machine(tag=tag, attrs=attrs)
        elif self.state == "reflection":
            self.reflection_state_machine(tag=tag, attrs=attrs)
        elif self.state == "contemplation":
            self.contemplation_state_machine(tag=tag, attrs=attrs)
        elif self.state == "homily":
            self.homily_state_machine(tag=tag, attrs=attrs)
        
    def handle_endtag(self, tag):
        if self.state == "hymn_of_praise":
            self.hymn_of_praise_state_machine(tag=tag)

    def handle_data(self, data):
        if "HYMN OF PRAISE" in data:
            self.state = "hymn_of_praise"
        elif "RELFECTION" in data or "REFLECTION" in data:
            self.state = "reflection" if self.state == "hymn_of_praise" else "homily" 
        elif "CONTEMPLATION" in data:
            self.state = "contemplation"
        elif "HOMILY" in data:
            self.state = "homily"

        if self.state == "saints":
            self.saint_state_machine(data=data)
        elif self.state == "hymn_of_praise":
            self.hymn_of_praise_state_machine(data=data)
        elif self.state == "reflection":
            self.reflection_state_machine(data=data)
        elif self.state == "contemplation":
            self.contemplation_state_machine(data=data)
        elif self.state == "homily":
            self.homily_state_machine(data=data)
        
    
    def saint_state_machine(self, data=None, tag=None, attrs=None):
        if DEBUG:
            print(data, tag, attrs)

        if tag in ("p", "br") and self.s_state: 
            self.s_state = "data"
            self.s_data[-1]["data"].append("")

        if attrs and (('style', 'color: #800000;') in attrs or ('style', 'color: #993300;') in attrs):
            self.s_state = "title"
        
        if data and len(data.strip()) > 0:
            if self.s_state == "title":
                if not len(self.s_data) or len(self.s_data[-1]["data"]):
                    self.s_data.append({"title": data[3:], "data" : []})
                else:
                    self.s_data[-1]["title"] += data
            else:
                if len(self.s_data[-1]["data"]) == 0:
                    self.s_data[-1]["data"] = [data,]
                else:
                    self.s_data[-1]["data"][-1] += data

    
    def hymn_of_praise_state_machine(self, data=None, tag=None, attrs=None):
        if DEBUG:
            print(data, tag, attrs)

        if tag == "strong":
            if attrs != None:
                self.hm_state = "title"
            else:
                self.hm_state = "content"
        elif tag in ("p", "div", "br"):
            self.hm_state = "content"
            if not len(self.hm_data["data"]) or len(self.hm_data["data"][-1]):
                self.hm_data["data"].append("")  
        
        if data and len(data.strip()) > 0:
            if self.hm_state == "title":
                self.hm_data["title"][-1] += data
            elif self.hm_state == "content":
                self.hm_data["data"][-1] += data
    
    def reflection_state_machine(self, data=None, tag=None, attrs=None):   
        if DEBUG:
            print(data, tag, attrs)

        if tag in ("p", "div", "br", "span"):
            self.r_state = "content"
            self.r_data.append("")
        
        if data and len(data.strip()) > 0:
            if self.r_state == "content":
                self.r_data[-1] += data
    
    def contemplation_state_machine(self, data=None, tag=None, attrs=None):
        if DEBUG:
            print(data, tag, attrs)

        if tag in ("p", "div"):
            if not self.c_state:
                self.c_state = "title"
            elif self.c_state in ("title", "content") and len(self.c_data["title"]):
                self.c_state = "content"
                self.c_data["data"].append("")
    
        if data and len(data.strip()) > 0:
            if self.c_state == "title":
                self.c_data["title"] += data
            elif self.c_state == "content":
                self.c_data["data"][-1] += data
    
    def homily_state_machine(self, data=None, tag=None, attrs=None):
        if DEBUG:
            print(data, tag, attrs)

        if tag == "strong" and not self.h_state:
            self.h_state = "title"
        elif tag in ("p", "div", "br"):
            if self.h_state == "quote" and self.h_data["quote"]:
                self.h_state = "content"
            # intentional fallthrough
            if self.h_state == "content":
                self.h_data["data"].append("")
        
        if data and len(data.strip()) > 0:
            if self.h_state == "title":
                self.h_data["title"] = data
                self.h_state = "quote"
            elif self.h_state == "quote":
                self.h_data["quote"] += data
            elif self.h_state == "content":
                self.h_data["data"][-1] += data
    
    def write(self, filename):
        data = {
            "saints": [{
                "title": s["title"], 
                "data": [x for x in s["data"] if x]
            } for s in self.s_data],
            "hymn_of_praise": {
                "title": [x.strip() for x in self.hm_data["title"] if x],
                "data": [x.strip() for x in self.hm_data["data"] if x],
            },
            "reflection": [x for x in self.r_data if x],
            "contemplation": {
                "title": self.c_data["title"].strip(),
                "data": [x.strip() for x in self.c_data["data"] if x],
            },
            "homily": {
                "title": self.h_data["title"],
                "quote": self.h_data["quote"],
                "data": [x for x in self.h_data["data"] if x],
            },
        }
        missing = ""
        for s in data["saints"]:
            if len(s["title"]) == 0:
                missing = "saint"
        if len(data["hymn_of_praise"]["data"]) == 0:
            missing = "hymn"
        if len(data["reflection"]) == 0:
            missing = "reflection"
        if len(data["contemplation"]["title"]) == 0 or len(data["contemplation"]["data"]) == 0:
            missing = "contemplation"
        if len(data["homily"]["title"]) == 0 or len(data["homily"]["quote"]) == 0 or len(data["homily"]["data"]) == 0:
            missing = "homily"
        
        if missing:
            print(filename, missing)

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    ensure_jan_1()

    with open("ohrid/content/jan_1.html") as f:
        data = f.read()

    jan = data.find('<div align="center" class="style4">JANUARY</div>')
    feb = data.find('<div align="center" class="style4">FEBRUARY</div>')
    mar = data.find('<div align="center" class="style4">MARCH</div>')
    apr = data.find('<div align="center" class="style4">APRIL</div>')
    may = data.find('<div align="center" class="style4">MAY</div>')
    jun = data.find('<div align="center" class="style4">JUNE</div>')
    jul = data.find('<div align="center" class="style4">JULY</div>')
    aug = data.find('<div align="center" class="style4">AUGUST</div>')
    sep = data.find('<div align="center" class="style4">SEPTEMBER</div>')
    oct = data.find('<div align="center" class="style4">OCTOBER</div>')
    nov = data.find('<div align="center" class="style4">NOVEMBER</div>')
    dec = data.find('<div align="center" class="style4">DECEMBER</div>')
    end = data.find('title="December 31">31</a></div>') + len('title="December 31">31</a></div>')

    months = [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec, end]
    for i in range(12):
        print(i)
        for date in parse_calendar(months[i], months[i+1]):
            try:
                get_content(**date)
            except:
                DEBUG = True
                print(date)
                get_content(**date)
                raise "stop"

    # DEBUG = True
    # get_content(**parse_calendar(may, jun)[28])

    files = [x for x in os.listdir("./ohrid/content/json") if ".json" in x]
    with open("./ohrid/content/database.ts", "w") as f:
        f.write('import Content from "./db_types"\n\n')
        f.write("let database: Content = {\n")
        for filename in files:
            f.write('  "%s": require("./json/%s"),\n' % (filename, filename))
        f.write("}\n\nexport default database;\n")

