from pymongo import MongoClient
import re
import requests
from bs4 import BeautifulSoup
from config import *
import os, subprocess
import datetime, json
import urllib.parse
import pickle
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
#from common_methods import *
import help_data
import textdistance as td
from smu_components import *
from smu_customers import *
from smu_status import *
import difflib
import nltk
import threading 
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize, sent_tokenize 
import enchant
stop_words = set(stopwords.words('english'))
smu_customers = [x.lower() for x in smu_customers]
smu_customers_new = [p for x in smu_customers for p in x.split(' ')]
smu_components = [x.lower() for x in smu_components]
smu_status = [x.lower() for x in smu_status]
eng_dict = enchant.Dict("en_US")

def remove_stop_words(string):
    string = ' '.join([x for x in string.split(' ') if x not in stop_words])
    return string

def log(msg, value=""):
    print("\n*****************")
    print("\t"+ str(msg) + " = " + str(value))
    print("*****************\n")

# def get_help(question, type="web"):
#     question = question.lower()
#     question = question.replace("help", "")
#     question = question.replace(" ", "")
#     domain_tag=""
#     help_strings = help_data.get_formatted_help_strings()
#     domain_tag = difflib.get_close_matches(question, list(help_strings.keys()),1)
#     if len(domain_tag)==0:
#         output = "<blockquote><h2>CHATBOT HELP</h2><ul>" + ''.join(["<li>"+i.upper()+"</li>" for i in help_strings.keys()]) + "To know the data provided and accepted in a specific domain query - help &lt;domain name&gt;</blockquote>"
#     else:
#         output = help_strings[domain_tag[0]]
#     # mini = 1000000
#     # for key in help_strings.keys():
#     #     if td.levenshtein(key.replace(" ",""), question) < mini:
#     #         mini = td.levenshtein.distance(key.replace(" ",""), question)
#     #         domain_tag = key
#     #         output = help_strings[domain_tag]
#     content = {
#         "title": "HELP",
#         "results": output
#     }
#     return content

def get_help(question, type="web"):
    question = question.lower()
    question = question.replace("help", "")
    question = question.replace(" ", "")
    domain_tag=""
    help_strings = help_data.get_formatted_help_strings()
    log("HELP Strs", help_strings)
    if "ri" in question:
        domain_tag = "ri score"
        output = help_strings[domain_tag]
        log("domaintag", domain_tag)        
    else:
        if "bit" in question:
            domain_tag = "bit score"
            output = help_strings[domain_tag]
            log("domaintag", domain_tag)        
        else:
            domain_tag = difflib.get_close_matches(question, list(help_strings.keys()),1)
            if len(domain_tag)==0:
                output = "<blockquote><h2>CHATBOT HELP</h2><ul>" + ''.join(["<li>"+i.upper()+"</li>" for i in help_strings.keys()]) + "To know the data provided and accepted in a specific domain query - help &lt;domain name&gt;</blockquote>"
            else:
                output = help_strings[domain_tag[0]]
                log("dt", domain_tag[0])        
    if type=="web":
        output = output.replace("h3","h4")
        output = output.replace("h2","h3")
    content = {
        "title": "HELP",
        "results": output
    }
    return content

def extractPRI(question):
    platform = ""
    release = ""
    image = ""
    question = question.lower().strip()
    words = question.split(' ')
    plat = re.compile('^((asr)|(asr9k exr)|(asr9000)|(asr9000 exr)|(asr9000 cxr)|(asr9k cxr)|(access)|(bosshogg)|(crs)|(fretta)|(mystique)|(ncs)|(n540)|(rosco)|(rsp4)|(skywarp)|(tetley)|(tortin)|(xrv9k))')
    rel = re.compile('^((\d*\d+){3}|((\d*\d+).(\d*\d+).(\d*\d+)))$')
    img = re.compile('\d+i$')
    for word in words:
        if plat.match(word):
            platform = word
        if rel.match(word):
            release = ''.join(word.split('.'))
        if img.match(word):
            image = word
    platform.replace('-','')
    if platform.startswith('ncs'):
        if platform[3:] == '540':
            platform = "n540"
        elif platform[3:] == '6000' or platform[3:] == '6k':
            platform = "ncs6k"
        elif platform [3:] == '1002':
            platform = "ncs1002"
        #else:
        #    platform = ""
    elif platform.startswith("asr9000"):
        platform = platform.replace("9000", "9k")

    return platform, release, image


def format_CDETS_data(identifier, component, status, engineer, submitter, keyword, version, found, attribute, headline, severity, de_manager, dtpt_manager, est_fix_date):
    formatted_txt = ""
    try:
        formatted_txt += "<strong>Bug Id:</strong> " + identifier + "$$$"
        formatted_txt += "<strong>Headline:</strong> " + headline + "$$$"
        formatted_txt += "<strong>Component:</strong> " + component + "$$$"
        formatted_txt += "<strong>Severity:</strong> " + severity + "$$$"
        formatted_txt += "<strong>Status:</strong> " + status + "$$$"
        formatted_txt += "<strong>Engineer:</strong> " + engineer + "$$$"
        formatted_txt += "<strong>DE-Manager:</strong> " + de_manager + "$$$"
        formatted_txt += "<strong>DTPT-Manager:</strong> " + dtpt_manager + "$$$"
        formatted_txt += "<strong>Submitter:</strong> " + submitter + "$$$"
        formatted_txt += "<strong>Keyword:</strong> " + keyword + "$$$"
        formatted_txt += "<strong>Version:</strong> " + version + "$$$"
        formatted_txt += "<strong>Found:</strong> " + found + "$$$"
        formatted_txt += "<strong>Attribute:</strong> " + attribute + "$$$"
        formatted_txt += "<strong>Est-fix-date:</strong> " + datetime.datetime.strftime(datetime.datetime.strptime(est_fix_date,"%m/%d/%Y %H:%M:%S\n"),"%A, %b %e %Y") + "$$$"
        formatted_txt += "<strong>CDETS Link:</strong> " + "http://cdets.cisco.com/apps/dumpcr?content=summary&format=html&identifier=" + identifier
    except Exception as e:
        log("Formatting CDETS ERROR", str(e))
        formatted_txt += ""
    return formatted_txt.replace('\n','')


def get_valid_key(query):
    fields = ['Action','Activity-when-found','Affected-platforms ','ARF-Manager','Apply-to','Assigned Date','Assigner','Attachment-title','Attachment-created','Attribute','Attribute1','Attribute2','Attribute3','Automated-test','Automated-test-id','Back-out-bad-commit','Back-out-for','BadcodefixId','BadCodeFlag','Behavior-changed','Branch-name','Breakage','Browser','Bug-origin','Build-number','Build-platform','By-previous-commit','By-previous-commit-value','Care-Update','Category','Cause','CF-origin','Changeset-id','Change-db-id','Child-type','Cisco_pid ','Class','Closed-on','Code-reviewer','Comment','Commit-time','Committer-name','Component','Component-version','Customer-location','Customer-name','Customer-track-number','Customer-severity','Database','Data-classification','Data-classification-reason','Default_data_classification','Default_data_classification_reason','Data-classification-overwritten','DE-manager','DE-priority','DE Priority Desc','Detailed-activity','DTPT-manager','Dev-escape','Dev-escape-activity','Dev-escape-resolution-code','Disposition','Document','Documents-changed','Documentation-link','Documentation-resolution','Doc-manager','Duplicate-of','Duplicate-on','Engineer','Escape-from','Escape-manager','Escape Manager Id','Escape-of','Escape-type','Escl-manager','Est-fix-date','Evaluation','Failure-type','Failed-release','Fe-component','Feature','Files Fixed','Fix-entry-id','Fix-entry-type','Foreign-bug','Foreign-link','Foreign-bug-type','Forwarded-on','Forwarded-to','Forwarder','Found','Found-during','Frequency','Hardening','Hardware','Hardware_cisco_part_num','Hardware_manufacturing_part_num','Hardware-changed','Hardware-ios','Headline','Held','Held-on','Identifier','IFD-CFD-Conv-date','Impact','Impact-level','ImpactedProjects','ImpactedPlatforms','Info-awaiting','Info-req-on','Integrated-releases','Jira-id','Junked-on','Keyword','Known-affected-releases','Known-fixed-releases','mc_learning','MDF-series','Mean-time-to-assigned','Mean-time-to-resolved','Mean-time-to-verified','More-by','More-on','Multi-commit-flag','New-on','Note-created','Note-title','Original-activity-when-found','Original-found-during','OS-type','OS-version','Opened-on','Opener','Origin','Original-found','Original-version','Original-resolved-on','Other-mail','Parent-Class','Parent-Dev-Escape-Activity','Parent-found','Parent-found-during','Parent-Test-EDP-Phase','Parent-Product','Parent-Project','ParentState','Patch-req','Patch-versions','Platform','Postponed-on','Postponed-until','Potentially-affected-releases','Prevention','Previous-commit-id','Product','Product-owner','Project','PrimaryPV','Primary TagId','PSIRT','PSIRT-attribute','PSIRT-status','Reason','Regression','Regression-analytics','Regression-probability','Regression-submitter','Related-bugs','Relationship-type','Release-stage','Released-code','Released-code-id','Resolved-on','Resolver','Root-cause-analysis','S1S2-without-workaround','Scenario','Scenario-url','Sector','Serviceability-improvement','Severity','Single-select1','Single-select2','Single-select3','Single-select4','Single-select5','Single-select6','Single-select7','SIR','Software','Software-changed','Software-ios','Source-submitted-on','SR-type','Status','Submitted-on','Submitter','Submitter-org','Submitter-education','Supplier_ticket_number','Summary','Sync-to-customer','Sys-Last-Updated','Tags','TEA-mgr','Teacat-of','Technical-writer','Test-name','Test-escape','Test-escape-resolution-code','Test-EDP-activity','Test-EDP-comments','Test-EDP-phase','Test-complexity-required','Test-group-type','To-be-fixed','Triggers','Trouble-tickets','Troubleshooting-documentation','Trouble-tickets-direct','Tickets-count','Tickets-count-direct','Unreproducible','TPS_comp_id','TPS_comp_name','TPS_comp_type','TPS-distro','TPS_flag','TPS_release','TPS_supplier','TPS-upstream','TPS_version','TPS-fixed-version','TPS-fixed','Updated By Name','Upgrade-caveats','Upgrade-remarks','Urgency','Url','Verified-confidence','Verified-on','Verified-release','Verifier','Version','VF-patched','VF-unpatched','Vobgroup','Waiting-on','Webserver','Window-env','Window-ver','Working-release-id']
    key = None
    f = [x.lower().replace('-','').replace('_','').replace(' ','') for x in fields]
    try:
        idx = f.index(query.lower().replace('-','').replace('_','').replace(' ',''))
        key = fields[idx]
    except:
        idx = None
    return fields[idx] if idx else None
    

def format_enclosures(data, limit=None):
    notes = [x.strip() for x in data.split('---Start of Note Titled:')[1:]]
    output = "<br>" + \
        "<ul>"
    for note in notes:
        title = note.split('(Created')[0].strip()
        data = note.split('---\n')[1].split('\n---End of Note')[0].strip()
        if limit:
            data = data[:limit] + " ....."
        output += "<li><strong>" + title + " : </strong><i>" + data + "</i></li>"
    output += "</ul>"
    log("ENCLOSURES",output)
    return str(output)


def get_row_indices(subs, tests):   
    test_list = [re.sub(r'\W+', '', test.lower()) for test in tests]
    res = [test_list.index(i) for i in test_list if re.sub(r'\W+', '', subs.lower()) in i] 
    return res


def format_ri_schedule(schedule):
    results = ""
    for key,data in schedule.items():
        results += "<strong>" + key + "</strong><br>"
        results += "<ul>"
        for item in data:
            results += "<li><strong>" + item["date"] + " :</strong> " + item["value"] + "</li>"
        results += "</ul><br>"
    content = {
        "title" : "Schedule from the past 1 week to the next 3 weeks",
        "results": [results] 
    }
    return content


def extract_date_str(question):
    pat = re.compile('\s\d?\d/\d{2}/\d{2}')
    res = re.findall(pat, question)
    if len(res) == 0:
        matchdate = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%y")
    else:
        matchdate = res[0].strip()
    matchstr = question.split("~")[1]
    return matchdate, matchstr
    
"""
Return type to be kept as following for all the functions

content = {
    "title": title - can be left blank as ""
    "results": results - This has to be a list even if one item is there make it as a list item
}

"""

def get_directory_info(cec_id):
    """
        building the directory data
    """

    query = "/usr/cisco/bin/rchain -nh" + " " + cec_id 
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    directory = {}
    
    if not console_output :
        return False

    if console_output :
        emp = []
        for emp_1 in console_output.split('\n') : 
            emp.append(emp_1)
        directory["reportees"] = []
        directory["id"] = re.split("[\s]\s+",emp[len(emp)-2])[0]
        directory["name"] = re.split("[\s]\s+",emp[len(emp)-2])[1]
        directory["photo"] = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg"%(directory["id"])
        if len(emp) > 2 :
            directory["manager"] = re.split("[\s]\s+",emp[len(emp)-3])[1]
            directory["manager-Id"] = re.split("[\s]\s+",emp[len(emp)-3])[0]
            directory["manager-photo"] = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg"%(directory["manager-Id"])
    
    query = "/usr/cisco/bin/rchain -th" + " " + cec_id
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    title = []
    if console_output :
        director = []
        for dirc in console_output.split('\n') : 
            director.append(dirc)
        directory["title"] = re.split("[\s]\s+",director[len(director)-2])[1]
        directory["DIRECTOR"] = []
        for i in range(1,len(director)-2):  
            if re.search("DIRECTOR",re.split("[\s]\s+",director[i])[1]):
                directory["DIRECTOR"].append(re.split("[\s]\s+",emp[i])[1] + "(" + re.split("[\s]\s+",emp[i])[0] + ")")
    
    query = "/usr/cisco/bin/rchain -ph" + " " + cec_id
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    phone = []
    if console_output :
        for emp1 in console_output.split('\n') : 
            phone.append(emp1)
        directory["phone-number"] = re.split("[\s]\s+",phone[len(phone)-2])[1]
    
    query = "/usr/cisco/bin/rchain -nrh" + " " + cec_id
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    reportees = []
    reports = []
    if console_output:
        directory["reportees"] = []
        
        for rep in console_output.split('\n'): 
            reports.append(rep)
        
        if len(reports) > 2 :
            for rep in reports: 
                reportees.append(re.split("[\s]\s+",rep))
            del reportees[len(reportees)-1]
            person = reportees.pop(0)
        for employee in reportees: 
            directory["reportees"].append(employee[1]+"("+employee[0]+")")
        directory["number-of-reportees"] = int(len(reportees))
    
    query = "/usr/cisco/bin/rchain -elh" + " " + cec_id
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")

    if console_output:
        loc_empId = []
        for rec in console_output.split('\n'): loc_empId.append(rec)

        directory['emp-number'] = re.split("[\s]\s+",loc_empId[len(loc_empId)-2])[2]
        directory["location"] = re.split("[\s]\s+",loc_empId[len(loc_empId)-2])[1]
    
    "/usr/cisco/bin/rchain -dh ikyalnoo"
    query = "/usr/cisco/bin/rchain -dh" + " " + cec_id
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    if console_output:
        department = []
        for rec in console_output.split('\n'): department.append(rec)
        directory["department"] = re.split("[\s]\s+",department[len(department)-2])[1]
    
    return directory

        


def get_directory_data(question,user,type="web"):
    ced_id = ""
    result = ""
    question = ''.join(question.lower().split("dir "))
    qwords = question.split(" ")
    content = {}
    for word in qwords:
        if word not in words.words():
            cec_id = word
    directory = get_directory_info(cec_id) 

    if not directory:
        return {
            "title" : "ERROR",
            "results" : "<strong> Could not find the requested details , please check help directory </strong>"
        }

    if re.search("location|loc|building",question):
        try:
            dir_photo = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg"%(directory["id"])
            result = result + "<img src='" + dir_photo + "' style='width:150px; height: auto;'><br><br>"
            result += "<p> Location of <strong>%s(%s)</strong> is  <strong>%s </strong></p>" % (directory["name"],directory["id"],directory["location"])
        except KeyError:
            result +=  "<strong> Sorry location couldn't find,please check help directory </strong>"
    elif re.search("director",question):
        try:
            dir_photo = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg"%(directory["id"])
            result = result + "<img src='" + dir_photo + "' style='width:150px; height: auto;'><br><br>"
            result = result + "<p> Director[s] of <strong>%s(%s)</strong>: </p>" % (directory["name"],directory["id"])
            
            for director in directory["DIRECTOR"]:
                result = result + "<br>" + "<strong> %s </strong>"%(director)
        except KeyError:
            result = result + "<p> Sorry director couldn't find,please check help directory</p>"
    elif re.search("manager|boss|whom i report to",question):
        try:
            #print(directory["name"],directory["id"],directory["manager"],directory["manager-Id"])
        
            result = result +"<img src='" + directory["photo"] + "' style='width:150px; height: auto;'><br><br>" + "<p>Manager of <strong>%s(%s)</strong> is <br><br><strong>%s(%s)</strong> </p>"%(directory["name"],directory["id"],directory["manager"],directory["manager-Id"])
            result = result + "<img src='" + directory["manager-photo"] + "' style='width:100px; height: auto;'><br><br>"
        except KeyError:
            result = result + "<strong> Sorry couldn't find Manager details,please check help directory </strong>"
    elif re.search("reportees|team",question):
        try:
            if len(directory["reportees"]) > 0:
                result = result + "<img src='" + directory["photo"] + "' style='width:150px; height: auto;'><br><br>" + "<p> Below are reportees of: <strong>%s(%s)</strong> </p>"%(directory["name"],directory["id"])
                result = result + "<p> Total number of reportees are: <strong>%s</strong> </p>"%(int(directory["number-of-reportees"])) 
                for mate in directory["reportees"]:
                    result = result + "<br>" + "<strong> %s </strong>"%(mate)
            else:
                result = result + "<p> No reportees found for <strong>%s(%s)</strong></p>"%(directory["name"],directory["id"])
        except KeyError:
            result = result + "<strong> sorry requested details coudn't be found,please check help directory </strong>"
    else:
        result = result + "<img src='" + directory["photo"] + "' style='width:150px; height: auto;'><br><br>"
        result = result + "<p>Name: <strong>%s</strong><br>CEC ID: <strong>%s</strong><br>Designation: <strong>%s</strong><br>Employee ID: <strong>%d</strong><br>Phone: <strong>%s</strong><br>Location: <strong>%s</strong><br>Department: <strong>%s</strong>"%(directory["name"],directory["id"],directory["title"],int(directory["emp-number"]),directory["phone-number"],directory["location"],directory["department"])
        result = result + "<br>Manager: <strong>%s(%s)</strong><br></br>"%(directory["manager"],directory["manager-Id"])
        result = result + "<img src='" + directory["manager-photo"] + "' style='width:100px; height: auto;'><br><br>"
    content["title"] = "Directory Details"
    content["results"] = result+"<br>"+"<br>"
    log(result)
    return content
    
    

def get_ri_schedule(question, type="web"):
    matchdate, matchstr = extract_date_str(question)
    access_token = '5rxm6e1os8lp87thcy3uawhen4'

    try:
        url = "https://api.smartsheet.com/2.0/sheets/4915172235077508"
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get(url=url, headers=headers)
        root = response.json()
        columns = root["columns"]
        tests = [row["cells"][0] for row in root["rows"]]
        tests = [(test["value"] if "value" in test else "") for test in tests]
        row_indices = get_row_indices(matchstr,tests)
        schedule = {}
        for row_index in row_indices:
            dates = []
            for column in columns[:2:-1]:
                date = column["title"].split('/')
                date = (date[0][1:] if date[0].startswith('0') else date[0]) + '/' + date[1] + '/' + (date[2] if len(date[2]) == 2 else date[2][-2:])
                date = datetime.datetime.strptime(date, "%m/%d/%y")
                startdate = (matchdate[0][1:] if matchdate[0].startswith('0') else matchdate[0]) + '/' + matchdate[1] + '/' + (matchdate[2] if len(matchdate[2]) == 2 else matchdate[2][-2:])
                startdate = datetime.datetime.strptime(matchdate, "%m/%d/%y") - datetime.timedelta(days=7)
                enddate = (matchdate[0][1:] if matchdate[0].startswith('0') else matchdate[0]) + '/' + matchdate[1] + '/' + (matchdate[2] if len(matchdate[2]) == 2 else matchdate[2][-2:])
                enddate = datetime.datetime.strptime(matchdate, "%m/%d/%y") + datetime.timedelta(days=21) 

                if date >= startdate:
                    if date <= enddate:
                        dates.append({
                            "date": datetime.datetime.strftime(date, "%b %e %Y"),
                            "index": columns.index(column),
                            "value": root["rows"][row_index]["cells"][columns.index(column)]["displayValue"] if "displayValue" in root["rows"][row_index]["cells"][columns.index(column)] else ""
                        })
                else:
                    break
            schedule[tests[row_index]] = dates
        return format_ri_schedule(schedule)
    except Exception as e:
        return {"title" : "Sorry, there was a problem fetching the schedule", "results": [e]}


def view_cdets(cdet):
    query = "dumpcr " + cdet
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    error = process.stderr.read().decode("UTF8")
    query = "findcr -w Attribute Identifier='" + cdet + "'"
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    attribute = process.stdout.read().decode("UTF8")
    output = ""
    if len(error) == 0:
        try:
            headline = console_output.split('Headline : ')[1].split('PrimaryPV : ')[0].strip().replace('\n','')
            headline = headline[0].upper() + headline[1:]
        except:
            headline = ""
        try:
            component = console_output.split('Component:')[1].split('Severity:')[0].strip().replace('\n','')
        except:
            component = ""
        try:
            project = console_output.split('Project  :')[1].split('Status  :')[0].strip().replace('\n','')
        except:
            project = ""
        try:
            severity = console_output.split('Severity:')[1].split('Headline :')[0].strip().replace('\n','')
        except:
            severity = ""
        try:
            status = console_output.split('Status  :')[1].split('Product  :')[0].strip().replace('\n','')
        except:
            status = ""
        try:
            engineer = console_output.split('Engineer :')[1].split('Manager  :')[0].strip().replace('\n','')
        except:
            engineer = ""
        try:
            de_manager = console_output.split('Manager  :')[1].split('Est Time/Attribute :')[0].strip().replace('\n','')
        except:
            de_manager = ""
        try:
            submitter = console_output.split('Submitter:')[1].split('Submitted: ')[0].strip().replace('\n','')
        except:
            submitter = ""
        try:
            keyword = console_output.split('Keyword :')[1].split('Files Impacted :')[0].strip().replace('\n','')
        except:
            keyword = ""
        try:
            version = console_output.split('Version :')[1].split('Build-number :')[0].strip().replace('\n','')
        except:
            version = ""
        # try:
        #     attribute = console_output.split('Attribute :')[1].split('Est. completion date: ')[0].strip().replace('\n','')
        # except:
        #     attribute = ""
        try:
            est_fix_date = console_output.split('Est. completion date:')[1].split('Documents Changed:')[0].strip().replace('\n','')
            est_fix_date = datetime.datetime.strftime(datetime.datetime.strptime(est_fix_date,"%m/%d/%Y %H:%M:%S"),"%A, %b %e %Y")
        except:
            est_fix_date = ""
        try:
            notes = format_enclosures(console_output.split('********************* Listing of Notes')[1].split('***********************')[1].split('********************* List of Fix Entries (')[0].strip(), 200)
        except:
            notes = "Nill"
        try:
            description = console_output.split('Summary:')[1].split('Point of Contact' if 'Point of Contact' in console_output else '*******')[0].strip().replace('\n','')
        except:
            description = ""
        try:
            point_of_contact = console_output.split('Point of Contact:')[1].split('****')[0].strip().replace('\n','')
        except:
            point_of_contact = ""
        output += "<strong>Bug Id:</strong> " + cdet + "<br>"
        output += "<strong>Headline:</strong> " + headline + "<br>"
        output += "<strong>Component:</strong> " + component + "<br>"
        output += "<strong>Project:</strong> " + project + "<br>"
        output += "<strong>Severity:</strong> " + severity + "<br>"
        output += "<strong>Status:</strong> " + status + "<br>"
        output += "<strong>Engineer:</strong> " + engineer + "<br>"
        output += "<strong>DE-Manager:</strong> " + de_manager + "<br>"
        output += "<strong>Submitter:</strong> " + submitter + "<br>"
        output += "<strong>Keyword:</strong> " + keyword + "<br>"
        output += "<strong>Version:</strong> " + version + "<br>"
        output += "<strong>Attribute:</strong> " + attribute + "<br>"
        output += "<strong>Est-fix-date:</strong> " + est_fix_date + "<br>"
        output += "<strong>Description/Summary:</strong> " + description + "<br>"
        output += "<strong>Point of Contact:</strong>" + point_of_contact + "<br>"
        output += "<strong>Enclosures:</strong>" + notes + "<br>"
        output += "<strong>CDETS Link:</strong>" + "http://cdets.cisco.com/apps/dumpcr?content=summary&format=html&identifier=" + cdet + "<br>"
    else:
        output = "<strong>" + error + "</strong>"

    log("CDET Information", output)
    # output += "<br><br>I can also update the fields for you, Here are a few examples:<br>" + \
    # "<ul style='font-size : 0.8em';>" + \
    # "<li>APENDING Attribute </li>" + \
    # "<li><strong>add attribute ~</strong><i>attribute data</i><strong>~</strong> to bug <strong>CSC<i>xx12345</i></li></strong><br>" + \
    # "<li>ADDING ENCLOSURES</li>" + \
    # "<li><strong>update enclosure ~</strong><i>Title</i><strong>~</strong> : <strong>~</strong><i>Content of the enclosure</i><strong>~</strong> to bug <strong>CSC<i>xx12345</i></strong></li><br>" + \
    # "<li>UPDATING SINGLE FIELD</li>" + \
    # "<li><strong>update de manager </strong><i>de manager userid</i> to bug <strong>CSC<i>xx12345</i></li></strong>" + \
    # "<li><strong>update severity </strong><i>severity value (0-7)</i> to bug <strong>CSC<i>xx12345</i></li></strong>" + \
    # "<li><strong>update est-fix-date ~</strong><i>est-fix-date (DD/MM/YYYY)</i><strong>~</strong> to bug <strong>CSC<i>xx12345</i></li></strong><br>" + \
    # "<li>UPDATING MULTIPLE FIELDS : <i>Add the field name and the respective values seperated by spaces</i></li>" + \
    # "<li><strong>update status </strong><i>status code</i> <strong>est-fix-date </strong><i>est-fix-date (DD/MM/YYYY)</i> <strong>attribute ~</strong><i>attribute data</i><strong>~</strong> to bug <strong>CSC<i>xx12345</i></li></strong><br>" + \
    # "<li><strong>VIEWING HISTORY: </strong></li>" + \
    # "<li>show me the <strong>history</strong> of <strong>CSC<i>xx12345</i></li></strong><br>" + \
    # "<li><strong>NOTE: </strong></li>" + \
    # "<li><i>Enclose the <strong>multi-word</strong> values in '<strong>~</strong>' (tild) symbols as shown above</i></li>" + \
    # "</ul>"
    
    return output


def add_attribute_cdets(cdet, question):
    log("Adding Attribute")
    attribute = None
    output = ""
    if "~" in question:
        attribute = question.split("~")[1]
        log("Attribute",attribute)
        query = "fixcr -S -i " + cdet + " Attribute ', " + attribute + "'"
        process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        console_output = process.stdout.read().decode("UTF8")
        error = process.stderr.read().decode("UTF8")
        output = "<strong>" + (console_output if len(error) == 0 else error) + "</strong>"
        log("OUTPUT",output)
    else:
        output = "<i>I'm still learning... Can you please enter the data in the following syntax</i><br><strong>add attribute </strong>~<i>attribute data</i>~ to bug <strong>CSC<i>xx12345</i></strong><br>"
        return output
    output += "<br><br>" + view_cdets(cdet)
    return output

    
def update_cdets(cdet, question):
    log("Updating CDETS")
    output = ""
    keys = []
    values = []
    words = question.split(' ')[1:]
    index = 0
    try:
        while True:
            key = get_valid_key(words[index])
            if key:
                keys.append(key)
            else:
                index = index + 2
                continue
            index = index + 1
            value = words[index]
            if words[index].startswith("~"):
                value = words[index]
                if not value.endswith('~'):
                    for i in range(index + 1, len(words)):
                        if words[i].endswith("~"):
                            value = value + " " + words[i]
                            break
                        value = value + " " + words[i]
                index = i + 1
                value = value.replace('~',"'")
                print(value)
            else:
                index = index + 1
            values.append(value)
            
            
    except Exception as e:
        pass

    log("Keys", keys)
    log("Values", values)
    params = ""
    for k,v in zip(keys,values):
        if k == 'Status':
            v = v.upper()
        elif k == 'Est-fix-date':
            v = "'" + datetime.datetime.strftime(datetime.datetime.strptime(v, "%d/%m/%Y"), "%m/%d/%Y 00:00:00") + "'"
        params = params + " " + k + " " + v
        
    query = "fixcr -i " + cdet + params
    log("EFD QUERY", query)
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    error = process.stderr.read().decode("UTF8")
    output = "<strong>" + (console_output if len(error) == 0 else error) + "</strong>"
    log("OUTPUT",output)
    output += "<br><br>" + view_cdets(cdet)
    return output


def update_enclosure_cdets(cdet, question):
    output = ""
    if "update" in question.lower() or "add" in question.lower() or "append" in question.lower() or "prepend" in question.lower():
        if question.count('~') == 4:
            title = question.split('~')[1].replace("'",'')
            data = question.split('~')[3].replace("'",'')
            if title.lower() == "scrubnote":
                if "prepend" in question.lower():
                    option = "-p"
                    data = data + ", "
                else:
                    option = "-s"
                    data = ", " + data
            elif "append" in question.lower():
                option = "-s"
                data = ", " + data
            elif "prepend" in question.lower():
                option = "-p"
                data = data + ", "
            else:
                option = "-o"
            with open("/auto/tftp-blr-users2/shpraman/ganesha/ganesha/tempnote.txt", 'w+') as filetowrite:
                try:
                    filetowrite.write(data)
                except Exception as e:
                    log("FILE WRITE ERROR", str(e))
            query = "addnote " + option + " " + cdet + " '" + title[0].upper() + title[1:] + "' /auto/tftp-blr-users2/shpraman/ganesha/ganesha/tempnote.txt"
            log(query) 
            process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            console_output = urllib.parse.unquote(process.stdout.read().decode("UTF8"))
            error = process.stderr.read().decode("UTF8")
            output = "<strong>" + (console_output if len(error) == 0 else error) + "</strong><br>"
            output += "<br>" + view_cdets(cdet)
        else:
            output = "<i>I'm still learning... Can you please enter the data in the following syntax</i><br><strong>update enclosure ~<i>Title</i>~ : ~<i>Content of the enclosure</i>~ to bug CSC<i>xx12345</i><br>"
    
    elif "show" in question.lower() or "view" in question.lower():
        query = "dumpcr " + cdet
        log(query) 
        process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        console_output = urllib.parse.unquote(process.stdout.read().decode("UTF8"))
        error = process.stderr.read().decode("UTF8")
        output += error
        try:
            notes = format_enclosures(console_output.split('********************* Listing of Notes')[1].split('***********************')[1].split('********************* List of Fix Entries (')[0].strip())
        except:
            notes = "Nill"
        output += notes

    elif "delete" in question.lower() or "del" in question.lower():
        if question.count('~') == 2:
            title = question.split('~')[1].replace("'",'')
            query = "addnote -D " + cdet + " '" + title + "'"
            log(query) 
            process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            console_output = urllib.parse.unquote(process.stdout.read().decode("UTF8"))
            error = process.stderr.read().decode("UTF8")
            output = "<strong>" + (console_output if len(error) == 0 else error) + "</strong><br>"
            output += "<br>" + view_cdets(cdet)
            
    return output


def fetch_history_cdets(cdet):
    query = "dumpcr " + cdet
    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    error = process.stderr.read().decode("UTF8")
    output = ""
    history = []
    if len(error) == 0:
        console_output = console_output.split('*********************************************** History *****************************************************')[1]
        logs = console_output.split('\n')[3:-1]
        for log in logs:
            row = log.split(' ')
            log_date = datetime.datetime.strftime(datetime.datetime.strptime(row[0].split(' ')[0].strip(), "%m/%d/%Y"), "%b %d, %Y")
            log_user = row[0].split(' ')[1].strip()
            log_field = row[1].strip()
            log_from = row[2].strip()
            log_to = row[3].strip()
            log_type = row[4].strip()
            add = ""
            if log_type == "New":
                if log_field.endswith('-Flg'):
                    add = "<strong><i>" + log_date + "</i></strong> - <strong>" + log_user + "</strong><i> cleared </i><strong>" + log_field + "</strong> which was <strong>\"" + log_from + "\"</strong><br>"
                else:
                    add = "<strong><i>" + log_date + "</i></strong> - <strong>" + log_user + "</strong><i> added </i><strong>" + log_field + "</strong> as <strong>\"" + log_to + "\"</strong><br>"
            elif log_type == "Mod":
                add = "<strong><i>" + log_date + "</i></strong> - <strong>" + log_user + "</strong><i> changed </i><strong>" + log_field + "</strong> from <strong>\"" + log_from + "\"</strong> to <strong>\"" + log_to + "\"</strong><br>"
            elif log_type == "Del":
                add = "<strong><i>" + log_date + "</i></strong> - <strong>" + log_user + "</strong><i> deleted </i><strong>" + log_field + "</strong> which was <strong>\"" + log_from + "\"</strong><br>"
            if (len(output) + len(add)) > 7200:
                output += "<i>........ <br>Click this link if you want to see earlier activity : http://cdets.cisco.com/apps/dumpcr?content=summary&format=html&identifier=" + cdet + "</i>"
                break
            else:
                output += add
    else:
        output = "<strong>" + error + "</strong><br>"
    return output


def get_cdets(question, user, type="web"):

    log("QUESTION", question)
    cdets_re = re.compile('csc[a-z]{2}[0-9]{5}')
    cdets = re.findall('csc[a-z]{2}[0-9]{5}',question.lower())
    cdets = [(i[:3].upper() + i[3:]) for i in cdets]
    results = []
    case_sensitive_question = question[:]
    for cdet in cdets:
        if "add attribute" in question.lower() or "add attr" in question.lower():
            output = add_attribute_cdets(cdet, case_sensitive_question)
        elif "enclosure" in question.lower() or "note" in question.lower() or " enc " in question.lower() or " encl " in question.lower():
            output = update_enclosure_cdets(cdet, case_sensitive_question)
        elif "history" in question.lower():
            output = fetch_history_cdets(cdet)
        elif "update" in question.lower() or "replace" in question.lower():
            output = update_cdets(cdet, case_sensitive_question)
        else:
            output = view_cdets(cdet)
        results.append(output[:7000])

    log("CDETS", results)
    content = {
        "title": "CDETS data",
        "results": (results[0] if type=="web" else results)
    }
    return content

def get_ri_score(question, user, type="web"):
    platform, release, image = extractPRI(question)
    log('platform : ', platform)
    log('release : ', release)
    log('image : ', image)
    log("QUESTION",question)
    client  = MongoClient('cafy-dev-lnx', 27017)
    db = client['regression_score']
    ridb = db['ri_score_copy']
    items = []
    #print("\t\t\t",platform, release, image)
    query = {
        "platform": {"$regex": "^.*" + platform + ".*$"},
        "version": {"$regex": "^" + release + ".*$"},
        "sub_version" : {"$regex": "^" + image + ".*$"}
    }
    for a in ridb.find(query):
        items.append(a)
    log("items", items)
    latest = True if "latest" in question.lower() else False
    results = []
    if platform == "" and release == "" and image == "" and type=="webex":
        l = ["access ri", "asr9k exr", "fretta", "n540", "ncs560", "ncs6k", "rosco", "rsp4"]
        for item in items[::-1]:
            pltfrm = str(item['platform'])
            rel = str(item['version'])
            img = str(item['sub_version'])
            cdets = []
            #print("\t\t", pltfrm)
            if pltfrm in l:
                l.remove(pltfrm)
                for test_area in item['test_area']:
                    if test_area['cdets'] != '':
                        cdets.append(" -> " + test_area['score'] + " | " + test_area['test_area'] + " | CDETS filed are: " + ', '.join(str(test_area['cdets']).split(';')))

                resultDict = {
                    "result" : "RI Score for the  <strong>"+ pltfrm +" </strong>,  <strong>" + '.'.join(list(rel)) + " </strong> lineup,  <strong>"+ img +"</strong> image :  <strong>" + str(item['score'])+"</strong>",
                    "cdets" : cdets
                }
                results.append(resultDict)
    else:
        ver, plat = [], []
        for item in items[::-1]:
            pltfrm = str(item['platform'])
            rel = str(item['version'])
            img = str(item['sub_version'])
            if platform == "" and release != "":
                if pltfrm in plat:
                    continue
                plat.append(pltfrm)
            if release == "" and platform!="":
                if rel in ver:
                    continue
                ver.append(rel)
            elif platform != "" and release != "" and latest:
                if pltfrm in plat:
                    continue
                plat.append(pltfrm)
            cdets = []
            for test_area in item['test_area']:
                if test_area['cdets'] != '':
                    cdets.append(" -> " + test_area['score'] + " | " + test_area['test_area'] + " | CDETS filed are: " + ', '.join(str(test_area['cdets']).split(';')))

            resultDict = {
                "result" : "RI Score for the <strong>"+ pltfrm +"</strong>, <strong>" + '.'.join(list(rel)) + "</strong> lineup, <strong>"+ img +"</strong> image : <strong>" + str(item['score']) + "</strong>",
                "cdets" : cdets
            }
            results.append(resultDict)

    if len(results) == 0:
        results.append({"result":"Sorry I couldn't find the data you are looking for"})
    content = {
        "title": "",
        "results": results
    }
    #log("content", content)
    return content

"""
        Method to scrape BIT to get results specific to the query.
"""
def scrapeBIT(platform, version, subversion, type):
    r, result, heading = "", "", 'platform wise score'
    if version=="":
        r = requests.get(config['BIT_URL'])
    else:
        r = requests.post(config['BIT_URL'], data={'version':version, 'sub-version': "-1" if subversion=="" else subversion, 'search':1})
    soup = BeautifulSoup(r.content.lower(), 'html5lib')
    if platform != "":
        platform = platform.replace('asr9000', 'asr9k').replace('asr5000', 'asr5k').replace('asr6000', 'asr6k').replace('ncs1000', 'ncs1k').replace('ncs5000', 'ncs5k').replace('x leaf', 'x-leaf')
        print(platform)
        divs = soup.find_all('b', text=re.compile(platform))
        webex_count, heading_list = 0, []
        for i in divs:
            label = i.text
            i = i.parent.parent
            if type=='webex':
                webex_count = webex_count + 1
                if webex_count<6:
                    div = i.find(text=re.compile('score')).parent
                    result = result + '\n'
                    print("Label is :", label)
                    result = result + '\n' + "<h1>" + label.strip().replace("\n", "").replace("    ", "") + "</h1>"
                    result = result + '\n<h3>' + str(div.find(text=re.compile('score'))).strip().replace("\n", "").replace("    ", "") + "</h3>"
                    count = 0
                    for i in div.find_all('tr'):
                        data = "<ul>"#[j.find('a').text.strip() if j.find('a') else j.text.strip() for j in i.find_all(['td', 'th'])]
                        for c, j in enumerate(i.find_all(['td', 'th'])):
                            # t = ""
                            # if j.find('a'):
                            #     t =  j.find('a').text.strip() if j.find('a').text.strip() else ""
                            # else:
                            #     t =  j.text.strip() if j.text.strip() else ""
                            # if t == "":
                            #     t =  "Nill"
                            # t = t + "&nbsp;"*(35-len(t)) + "|"
                            # data = data + t 
                            if count == 0:
                                heading_list.append(j.text.strip())
                            else:
                                t = ""
                                if j.find('a'):
                                    t =  j.find('a').text.strip() if j.find('a').text.strip() else ""
                                else:
                                    t =  j.text.strip() if j.text.strip() else ""
                                if t == "":
                                    t =  "Nill"
                                data = data + "\n" + "<li><h4>" + heading_list[c] + ": " +  t + "</h4></li>"
                        count = count + 1
                        result = result + '\n' +  data + '</ul>\n' + "="*30
                    result = result + "\n\n"+ "-"*3 + "\n\n"
            else:
                result = result + label + '<br>' + str(i.find(text=re.compile('score')).parent)
        if result == "":
            result = "<h4>Could not find data you requested for, kindly verify once.</h4>"
    else:
        main_div = soup.find(text=re.compile(heading)).parent.parent
        if type == 'webex':
            result = result + "<h2>" + heading + "</h2>"
            for i in main_div.find_all('tr'):
                #result=result+'\n'+ '-'*3
                data = ["**"+j.text.strip()+"**" for j in i.find_all(['th', 'td'])]
                data = '|'.join(data)
                result = result + "\n<br>" + data 
            result = result + '\n\n' 
        else:
            table = main_div.find("table")
            table = str(table)
            result = heading + '\n' + table
    #print(len(result))
    return result


"""
        Method for getting BI scores as per the user query.
"""
def get_BIT_Score(question, user, type="web"):
    platform, version, subversion, title, results = "", "", "", "", ""
    question = question.lower().strip()
    words = question.split(' ')
    plat = re.compile('^((asr)|(asr9k exr)|(asr9000)|(asr9k)|(asr9000 exr)|(asr9000 cxr)|(asr9k cxr)|(ncs)|(ncs540)|(ncs 540)|(ncs 560)|(ncs560)|(ncs6k)|(ncs6k pbit)|(ncs5k)|(ncs5500)|(crs cbt)|(xrv9k))|(pixr)|(spitfire)|(x-leaf)|(x leaf)|(rsp4)|(rsp)')
    #ver = re.compile("^(([0-9]|[0-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[0-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    ver = re.compile("^(([0-9]|[0-9][0-9]|[0-9][0-9][0-9])\.([0-9]|[0-9][0-9]|[0-9][0-9][0-9])\.([0-9]|[0-9][0-9]|[0-9][0-9][0-9]))")
    subver = re.compile("^([0-9]|[0-9][0-9])i")
    for word in words:
        if plat.match(word):
            platform = word
        if ver.match(word):
            version = word
            version = ".".join(["0"+x if len(x)==1 else x for x in version.split(".")])
        if subver.match(word):
            subversion = word[:-1]
            if len(subversion)==1:
                subversion = "0" + subversion
        elif word.isnumeric():
            vers = word
            for i in vers:
                version = version + "0" + i + "."
            version = version[:-1]
    if platform == "rsp4" or "rsp" in platform:
        platform = "ncs560"
    log("Platform ", platform)
    log("Version ", version)
    log("Subversion ", subversion)
    results = scrapeBIT(platform, version, subversion, type)
    content = {'title': title, 'results': results}
    #log('content', content)
    return content

"""
    Get SMU Token
"""
def get_token():
    res = requests.post(config['SMU_AUTH_API'], params={'client_id': config['SMU_CLIENT'], 'client_secret': config['SMU_CLIENT_SEC'], 'grant_type': config['SMU_GRANT_TYPE']})
    #print(res.content)
    return json.loads(res.content)

def get_smu_details(token, smuid):
    try:
        res = requests.post(config['SMU_DETAIL_API'], params={'smu_id':smuid}, headers={'Authorization': 'Bearer '+token})
        res = json.loads(res.content)['smu_basic_details']
        data = ""
        for i in res:
            data = data + '<h4>'+ i + ' : ' + (res[i] if res[i] else ' Nil ') + '</h4>'
        return [data]
    except:
       return False


def get_smu_search(token, ddtsid='',  plat='',  version='', customer='', component='', status='', smutype='', not_posted=False):
    try:
        res = requests.post(config['SMU_SEARCH_API'], params={'ddts':ddtsid, 'customer':customer, 'platform':plat, 'component':component, 'release': version}, headers={'Authorization': 'Bearer '+token})
        res = json.loads(res.content)['smu_list'][::-1]
        typecheck = len(smutype)>0#print(res)
        data, count = "", 0
        for i in res:
            # if not_posted and i['posted_date'].lower()=='na':
            #     for j in i:
            #         data = data + '<h4>'+ j +' : '  + (i[j] if i[j] else ' Nil ') + '</h4>'
            #     data = data + '<br>' + '---'*30 + '<br>'
            if  count>5:
                break
            if status!='':

                if i['status'].lower()==status and (i['smu_type'].lower()==smutype if typecheck else True):
                    count +=1
                    for j in i:
                        data = data + '<h4>'+ j +' : '  + (i[j] if i[j] else ' Nil ') + '</h4>'
                    data = data + '<br>' + '---'*30 + '<br>'
            
            else:
                if (i['smu_type'].lower()==smutype if typecheck else True):
                    count +=1
                    for j in i:
                        data = data + '<h4>'+ j +' : '  + (i[j] if i[j] else ' Nil ') + '</h4>'
                    data = data + '<br>' + '---'*30 + '<br>'
        return  [data] if len(data)>0  else ['No data found! try "help smu" to know more or check the question asked again.']

    except:
        return False


def get_raw_smu(token, status, smutype):
    data, count, total_try = "", 0, 150
    def parallel_calls(smu_ids, typecheck):

        nonlocal count, data
        for i in smu_ids:
            if count > 5:
                break
            res = requests.post(config['SMU_DETAIL_API'], params={'smu_id':i}, headers={'Authorization': 'Bearer '+token})
            res = json.loads(res.content)['smu_basic_details']

            if res['status'].lower() == status and (res['smu_type'].lower()==smutype if typecheck else True):

                count +=1
                for j in res:
                    data = data + '<h4>'+ j +' : '  + (res[j] if res[j] else ' Nil ') + '</h4>'
                data = data + '<br>' + '---'*30 + '<br>'
    res = requests.get(config['SMU_ALL_ID'], headers={'Authorization': 'Bearer '+token})
    smu_ids = json.loads(res.content)['all_smu_list'][::-1]

    typecheck = len(smutype)>0
    if status!='':
        l = [None]*5
        for i in range(5):
            l[i] = threading.Thread(target=parallel_calls, args=(smu_ids[i*50:(i+1)*50], typecheck))

            l[i].start()
        for i in l:
            i.join()
    else:
        for i in smu_ids:
            if count>5 or total_try==0:
                break
            total_try -=1
            res = requests.post(config['SMU_DETAIL_API'], params={'smu_id':i}, headers={'Authorization': 'Bearer '+token})
            res = json.loads(res.content)['smu_basic_details']
            # if status!='':
            #     if res['status'].lower() == status:
            #         count +=1
            #         for j in res:
            #             data = data + '<h4>'+ j +' : '  + (res[j] if res[j] else ' Nil ') + '</h4>'
            #         data = data + '<br>' + '---'*30 + '<br>'
            #else:

            if typecheck:
                if res['smu_type'].lower() == smutype:
                    count +=1
                    for j in res:
                        data = data + '<h4>'+ j +' : '  + (res[j] if res[j] else ' Nil ') + '</h4>'
                    data = data + '<br>' + '---'*30 + '<br>'
            else:
                count +=1
                for j in res:
                    data = data + '<h4>'+ j +' : '  + (res[j] if res[j] else ' Nil ') + '</h4>'
                data = data + '<br>' + '---'*30 + '<br>'

    return [data] if len(data)>0  else ['No data found! try "help smu" to know more or check the question asked again.']



"""
    Method to get SMU Data

    Data search with SMU ID
    Data search with DDTS ID
    Data search with multiple inputs: DDTS ,Platform,Release
    Data search with Customer name
    Data search with exceptional approval of SMUs
    Data search with Service Pack data inputs where they wanted to  know whether some particular DDTS is part of that Service Pack
    Data search with components wanting to know about platform/release
"""

def get_smu_data(question, user, type="web"):

    global smu_components, smu_customers_new, smu_status
    status_acronyms = {'ut':'unittestpass', 'dt':'devtestpass'}
    question = question.lower().replace('smu', '')
    not_posted = True if 'not posted' in question else False
    token = get_token()['access_token']

    smuid, ddtsid, platform, customer, component, version, status, smutype, result = '', '', '', '', '', '', '', '', None

    smu_id = re.compile('^aa.....')
    ddts_id = re.compile('^csc.......')
    plat = re.compile('^((asr)|(asr9k exr)|(asr9000)|(asr9000 exr)|(asr9000 cxr)|(asr9k cxr)|(ncs)|(ncs540)|(ncs 540)|(ncs 560)|(ncs6k pbit)|(ncs5k)|(ncs5500)|(crs cbt)|(xrv9k))|(pixr)|(spitfire)|(x-leaf)|(x leaf)')
    ver = re.compile("^(([0-9]){1,2}(\.){0,1}([0-9]){1,3}(\.){0,1}([0-9]){1,3})")
    qwords = remove_stop_words(question).replace('smu', '').replace('smus', '').replace('data', '').replace('details', '').replace('search', '').replace('list', '').replace('release', '').replace('version', '').replace('customer', '').replace('show', '').replace('let me know', '').replace('know', '').replace('display', '').replace('status', '').replace('platform', '').replace('pass', '').split(' ')
    qwords = [x for x in qwords if x!='']

    smu_type = ['recommended', 'optional', 'psirt']

    print(qwords)
    for word in qwords:
        if smu_id.match(word):
            smuid = word
            question.replace(word, '')
        elif ddts_id.match(word):
            ddtsid = word
            question.replace(word, '')
        elif plat.match(word):
            platform = word
            question.replace(word, '')
        elif ver.match(word):
            version = word if '.' in (word) else '.'.join(list(word))
            version = version[:-1] if version[-1]=='.' else version
            version = version[1:] if version[0]=='.' else version
        elif len(difflib.get_close_matches(word, smu_type))>0:
            smutype = difflib.get_close_matches(word, smu_type)[0]
        elif len(difflib.get_close_matches(word, smu_status))>0:
            status = difflib.get_close_matches(word, smu_status)[0]
        elif word not in words.words() and len(difflib.get_close_matches(word, smu_components))>0:
            component = difflib.get_close_matches(word, smu_components)[0]
        elif word not in words.words() and len(difflib.get_close_matches(word, smu_customers_new))>0:
            customer = difflib.get_close_matches(word, smu_customers_new)[0] #if len(difflib.get_close_matches(word, smu_customers_new))>0 else difflib.get_close_matches(word, smu_customers)[0]

    
    print('ddts', ddtsid, '| customer:', customer, '| platform:',platform, '| component:', component, '| version:', version, '| status:', status, '| smu_type:', smutype)

    if status!='':
        status = status_acronyms[status] if status in status_acronyms else status


    if smuid!='':
        result = get_smu_details(token, smuid)
        #print(result)
    elif ddtsid!='' or customer!='' or platform!='' or component!='' or version!='':

        #print('ddts', ddtsid, '| customer:', customer, '| platform:',platform, '| component:', component, '| version:', version, '| status:', status, '| smu_type:', smutype)
        result = get_smu_search(token, ddtsid,  platform, version, customer, component, status, smutype, not_posted)
    else:
        result = get_raw_smu(token, status, smutype)

    #print(result)
    if result:
        return {'title':'', 'results':  result if type=="webex"  else result[0]}
    else:
        return {'title': '', 'results': ['No SMU data found !!'] if type=="webex" else 'No SMU data found !!'}

"""
Rally API
Fetches the Rally result based on the feature ID given by user in question.
"""

def get_rally_result_fid(feature_id):
    RALLY_API_DOMAIN = config['Rally_API_domain']
    path = '/portfolioitem/feature?query=(FormattedID%20%3D%20'+feature_id+')'
    to_fetch = "&fetch=Name,FormattedID,AHAIDString,TIMSReportID,DevGONOGO,DTEEndDateActual,DTEEndDateCommit,DTEEndDateTarget,DTHOActual,DTHOCommit,DTHOTarget,DTHOStatus,PlannedRelease,PlatformsPlanned,PlatformsRequested,POCDevManagersDEDT,POCAutomationTestManager,POCDevelopmentManager,POCProductManager,POCProgramManager,POCTestManager,RequirementRefPRDEDCS,TCAutomated,TCAutomation,TCAutomationComplete,TCAutomationRequired,TCAutomationSource,TestGONOGO,AutomationAPalignment,AutomationCompleteDateActual,AutomationCompleteDateCommit,AutomationCompleteDateTarget,Automationcompletiondate,Automationproductiondate,AutomationStartDate,TestPlanStatus"
    
    try:
        res = requests.request('GET', f'{RALLY_API_DOMAIN}{path}{to_fetch}', headers={'zsessionid': config['Rally_APIKey']})
        #log("Connect","True")
        json_load = json.loads(res.content)
        res_list = json_load['QueryResult']['Results']
    except:
        return "Problem in establishing connection."

    #print(res_dict)
    if len(res_list) == 0:
        return ""

    res_dict = res_list[0]
    result = ""

    #prog_manager,dev_manager,test_manager,dtho_status,dtho_commit,dtho_target,dtho_actual,fid,plan_release,tims_id,aha_id,clarity_id = "","","","","","","","","","","",""
    
    #print(type(res_dict["Feature"]["c_BCCCDocStatus"]))
    
    result += "<h3>" + str(res_dict.get("Name","N.A.")) + "</h3>"

    result += "Feature ID = " + str(res_dict.get("FormattedID","N.A.")) + "<br>"
    result += "Planned Release = " + str(res_dict.get("c_PlannedRelease","N.A.")) + "<br>"
    result += "TIMS Report ID = " + str(res_dict.get("c_TIMSReportID","N.A.")) + "<br>"
    result += "Aha ID = " + str(res_dict.get("c_AhaIDString","N.A.")) + "<br><br>"

    result += "Program Manager = " + str(res_dict.get("c_POCProgramManager","N.A.")) + "<br>"
    result += "Product Manager = " + str(res_dict.get("c_POCProductManager","N.A.")) + "<br>"
    result += "Development Manager = " + str(res_dict.get("c_POCDevelopmentManager","N.A.")) + "<br>"
    result += "Development Managers DEDT = " + str(res_dict.get("c_POCDevManagersDEDT","N.A.")) + "<br>"
    result += "Test Manager = " + str(res_dict.get("c_POCTestManager","N.A.")) + "<br>"
    result += "Automation Test Manager = " + str(res_dict.get("c_POCAutomationTestManager","N.A.")) + "<br><br>"
    
    flag = 0
    for i in range(res_dict['c_PlatformsPlanned']['Count']):
        if flag==0:
            result += "Platforms Planned = "
            flag = 1
        result += str(res_dict['c_PlatformsPlanned']['_tagsNameArray'][i].get('Name','N.A.'))
        if(i+1 == res_dict['c_PlatformsPlanned']['Count']):
            result += "<br>"
            flag = 0
        else:
            result += ', '

    for i in range(res_dict['c_PlatformsRequested']['Count']):
        if flag==0:
            result += "Platforms Requested = "
            flag = 1
        result += str(res_dict['c_PlatformsRequested']['_tagsNameArray'][i].get('Name','N.A.'))
        if(i+1 == res_dict['c_PlatformsRequested']['Count']):
            result += "<br><br>"
        else:
            result += ', '

    result += "Test Plan Status = " + str(res_dict.get("c_TestPlanStatus","N.A.")) + "<br>"
    result += "Requirement PRDEDCS = " + str(res_dict.get("c_RequirementRefPRDEDCS","N.A.")) + "<br>"
    result += "Development Go/NoGo = " + str(res_dict.get("c_DevGONOGO","N.A.")) + "<br>"
    result += "Test Go/NoGo = " + str(res_dict.get("c_TestGONOGO","N.A.")) + "<br><br>"

    result += "DTHO Status = " + str(res_dict.get("c_DTHOStatus","N.A.")) + "<br>"
    result += "DTHO Actual = " + (str(res_dict.get("c_DTHOActual")).split("T")[0] if "c_DTHOActual" in res_dict  else "N.A.") + "<br>"
    result += "DTHO Commit = " + (str(res_dict.get("c_DTHOCommit")).split("T")[0] if "c_DTHOCommit" in res_dict  else "N.A.") + "<br>"
    result += "DTHO Target = " + (str(res_dict.get("c_DTHOTarget")).split("T")[0] if "c_DTHOTarget" in res_dict  else "N.A.") + "<br><br>"
    
    result += "DTE End Date Actual = " + (str(res_dict.get("c_DTEEndDateActual")).split("T")[0] if "c_DTEEndDateActual" in res_dict  else "N.A.") + "<br>"
    result += "DTE End Date Commit = " + (str(res_dict.get("c_DTEEndDateCommit")).split("T")[0] if "c_DTEEndDateCommit" in res_dict  else "N.A.") + "<br>"
    result += "DTE End Date Target = " + (str(res_dict.get("c_DTEEndDateTarget")).split("T")[0] if "c_DTEEndDateTarget" in res_dict  else "N.A.") + "<br><br>"

    result += "Automation AP Alignment = " + str(res_dict.get("c_AutomationAPalignment","N.A.")) + "<br>"
    result += "Automation Complete Date Actual = " + (str(res_dict.get("c_AutomationCompleteDateActual")).split("T")[0] if "c_AutomationCompleteDateActual" in res_dict  else "N.A.") + "<br>"
    result += "Automation Complete Date Commit = " + (str(res_dict.get("c_AutomationCompleteDateCommit")).split("T")[0] if "c_AutomationCompleteDateCommit" in res_dict  else "N.A.") + "<br>"
    result += "Automation Complete Date Target = " + (str(res_dict.get("c_AutomationCompleteDateTarget")).split("T")[0] if "c_AutomationCompleteDateTarget" in res_dict  else "N.A.") + "<br>"
    result += "Automation Start Date = " + (str(res_dict.get("c_AutomationStartDate")).split("T")[0] if "c_AutomationStartDate" in res_dict  else "N.A.") + "<br>"
    result += "Automation Completion Date = " + (str(res_dict.get("c_Automationcompletiondate")).split("T")[0] if "c_Automationcompletiondate" in res_dict  else "N.A.") + "<br>"
    result += "Automation Production Date = " + (str(res_dict.get("c_Automationproductiondate")).split("T")[0] if "c_Automationproductiondate" in res_dict  else "N.A.") + "<br><br>"

    result += "TC Automated = " + str(res_dict.get("c_TCAutomated","N.A.")) + "<br>"
    result += "TC Automation Complete = " + str(res_dict.get("c_TCAutomationComplete","N.A.")) + "<br>"
    result += "TC Automated Required = " + str(res_dict.get("c_TCAutomationRequired","N.A."))

    return result


def get_rally_data_fid(fid, type):
    log('Feature ID', fid)
    result = ""
    if fid=="":
        results = "Wrong Feature ID."
        return {'title':'', 'results':([results] if type == "webex" else results)}

    result = get_rally_result_fid(fid)
    #print(result)

    if result == "":
        results = "Couldn't find any data for this Feature ID."
        return {'title':'', 'results':([results] if type == "webex" else results)}

    
    result = "<blockquote>" + result + "</blockquote>"

    content = {'title':'',
                'results':([result] if type=="webex" else result)}

    return content

def search_rally_fid(query_str, type):
    RALLY_API_DOMAIN = config['Rally_API_domain']
    path = '/portfolioitem/feature?query=' + query_str
    to_fetch = "&fetch=Name,FormattedID&pagesize=2000"
    #print('Connecting')
    try:
        res = requests.request('GET', f'{RALLY_API_DOMAIN}{path}{to_fetch}', headers={'zsessionid': config['Rally_APIKey']})
        #log("Connect","True")
        json_load = json.loads(res.content)
        res_list = json_load['QueryResult']['Results']
        #print('Hi')
    except:
        return "Problem in establishing connection."

    if len(res_list) == 0:
        return "No Rally ID found."


    result = ""
    
    for dic in (res_list[:30] if type=='webex' else res_list):
        #print(len(res_list))
        #print(result)
        result += "<pre>" + dic['FormattedID'] +"\t"+ ''.join([i if ord(i) < 128 else ' ' for i in dic["Name"]]) + "<br></pre>"
        
    if type == "webex":
            if len(res_list)>30:
                result += "Showing 30 out of " + str(len(res_list)) + " results.<br>For more results go to http://ganesha.cisco.com:3000<br>"

    #print(result)
    return result


def get_rally_data(question, user, type="web"):
    try:
        print(user)
        question = question.lower().replace(', ',' ').replace(',',' ')
        feature_id_pat = re.compile('^f\d')
        words = question.split(' ')
        for word in words:
            if word == "and" or word == '':
                words.remove(word)
            
        for idx in range(len(words)):
            if words[idx] in ["me" ,"my", "mine", "myself"]:
                #print(words[idx],idx)
                if words[idx]=="me" and idx<2:
                    pass
                else:
                    words[idx] = user
                

        fid = ""
        for word in words:
            if feature_id_pat.match(word):
                fid = word
                return get_rally_data_fid(fid, type)

        POC_list = ["c_POCDevScopingL0", "c_POCDevScopingLead", "c_POCDocDevSME", "c_POCDocLead", "c_POCExecutives", "c_POCScrumMaster",
            "c_POCTechnicalLeader", "c_POCTestScopingL0", "c_POCTestScopingLead", "c_POCLineManagement", "c_POCDevManagersDEDT",
            "c_POCOtherPOCsegScrummasteretc", "c_POCProductOwnerPOCPO", "c_POCArchitect", "c_POCAutomationTestManager", "c_POCDevelopmentManager",
            "c_POCDevelopmentManagerText", "c_POCDOCMANAGER", "c_POCPDDirector", "c_POCPIDirector", "c_POCProductManager", "c_POCProgramManager",
            "c_POCTechnicalWriter", "c_POCTestManager", "c_POCTestManagerText", "c_POCUXLead"]

        re_pat = {
            "POCDevelopmentManager" : re.compile("^dev"),
            "POCProductManager" : re.compile("^prod"),
            "POCProgramManager" : re.compile("^prog"),
            "POCTestManager" : re.compile("^test"),
            "RequestedRelease" : re.compile("^(([0-9]){1,2}(.){0,1}([0-9]){1,3}(.){0,1}([0-9]){1,3})")
        }
        count = 0
        query_str = ""
        #print(re_pat)
        #print(words)
        flag = False
        while count < len(words):
            #print(count)
            for i in re_pat:
                if(re_pat[i].match(words[count])):
                    #print(words[count])
                    if i!="RequestedRelease":
                        count += 2
                        flag = True
                        #print(words[count], not eng_dict.check(words[count]))
                        #print("Before loop:", count, len(words),not eng_dict.check(words[count]))
                        while count<len(words) and not eng_dict.check(words[count]):
                            #print("In loop:", count)
                            if query_str == "":
                                query_str += f'({i} contains {words[count]})'
                            else:
                                query_str = f'({query_str} AND ({i} contains {words[count]}))'
                            count += 1
                        if count<len(words):
                            count -= 1
                    else:
                        #count = count - 2
                        words[count] = words[count] if '.' in (words[count]) else '.'.join(list(words[count]))
                        if query_str == "":
                                query_str += f'({i} contains {words[count]})'
                        else:
                            query_str = f'({query_str} AND ({i} contains {words[count]}))'
                    break
            count += 1
            
        #print(flag)
        #print(query_str)
        if not flag:
            user_query_str = ""
            for word in words:
                #print(word)
                if not eng_dict.check(word):
                    for item in POC_list:
                        if user_query_str == "":
                            user_query_str = f'({item} contains {word})'
                        else:
                            user_query_str = f'({user_query_str} OR ({item} contains {word}))'
                    if query_str == "":
                        query_str = user_query_str
                    else:
                        query_str = f'({query_str} AND {user_query_str})'
                    user_query_str = ""

        #log("query_str",query_str)
        result = search_rally_fid(query_str, type)

        result = "<blockquote>" + result + "</blockquote>"

        content = {'title':'',
                    'results':([result] if type=="webex" else result)}

        return content   
    except:
        return {'title':'', 'results':(["Some error Occured!"] if type=="webex" else "Some error Occured!")}



'''
PIMS COMMANDS
Delta LOCs between builds
LOCs for lineup/project
LOCs by Org/Func/DE Mgr/Comp
'''
def pims_execute(question, user, type="web"):
    log("QUESTION", question)
    keys = ["src_bld","targ_bld","proj_name","efr_id"]
    argdict = {}
    for i in keys:
        argdict[i]=""
    question = question.replace("Ganesha","")
    question = question.lower().strip()
    words = question.split(' ')
    
    rel = re.compile('^((\d*\d+){3}|((\d*\d+).(\d*\d+).(\d*\d+)))$')
    img = re.compile('\d+\D$')
    efr = re.compile('EFR-00000[0-9]{6} | EFR-[0-9]{6} | [0-9]{6}')
    imgs=[]
    rels=[]
    efrs=[]
    for word in words:
        if rel.match(word):
            rels.append(word)
        if img.match(word):
            imgs.append(word)
        if rel.match(word):
            efrs.append(word)    
    log("rels",rels)
    vers=[]
    version=""
    for i in rels:
        release = i
        if len(release)==3:
            version = '.'.join(release) 
        elif len(release)==4:
            version = release[0]+"."+release[1]+"."+release[2]+release[3]
        vers.append(version)    
    pims_new_prod_bld_list()    
    with open("prodbldlist.pkl","rb") as f:
        prodlist = pickle.load(f)

    if (version):
        version=vers[0]
        patt = version.replace(".","_")
        
        print("LEN",len(prodlist))
        for prod in prodlist:
            if patt in prod and imgs[0].upper() in prod:
                argdict['src_bld'] = prod 
        
        version = vers[1] if len(vers)==2 else vers[0]        
        patt = version.replace(".","_")        
        for prod in prodlist:
            if patt in prod and imgs[1].upper() in prod:
                argdict['targ_bld'] = prod       

    argdict["efr_id"] = "" if len(efrs)==0 else efrs[0]              
    # log("VERSION",version)
    log("Source build",argdict['src_bld'])
    log("Target build",argdict['targ_bld'])

    results=[]
    if "delta" in question:
        results = pims_get_delta_loc(argdict["src_bld"],argdict["targ_bld"],type)
    else:
        pims_new_proj_list()
        with open("projlist.pkl","rb") as f:
            projlist = pickle.load(f)
        cquestion=question[:]    
        question = question.replace("project","")
        question = question.replace("lineup","")
        question = question.replace("proj","")
        question = question.replace("pims","")
        question = question.replace("gsr","")
        stop_words = set(stopwords.words('english')) 
        words = word_tokenize(question) 
        question = [w for w in words if not w in stop_words]
        log("mod question", question)

        for i in question:
            for p in projlist:
                if i in p:
                    print(i,p)
                    argdict["proj_name"] = p
                    log("proj name",argdict["proj_name"])            
        if "lineup" in cquestion :
            results = pims_get_loc_for_lineup(argdict["proj_name"],argdict["efr_id"])
        else:
            results = pims_get_loc_by_cat(argdict["proj_name"],argdict["efr_id"],type)

    log("PIMS", results)
    content = {
        "title": "PIMS report data",
        "results": [results] if type=="webex" else results
    }
    return content
    
"""
PIMS HANDLERS
"""
def getdloc(val):
    return val[1]

def pims_get_delta_loc(source, target,type):
    # type="webex"
    query = "pims gsr -r summary_loc -src_prod_bld " + source + " -targ_prod_bld " + target +" -format json"
    log("query",query)
    process = subprocess.Popen("export LC_ALL='en_US.UTF-8'\n"+query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    console_output = process.stdout.read().decode("UTF8")
    error = process.stderr.read().decode("UTF8")
    # log("ERROR!",error)
    if len(error)==0:
        cons_op = json.loads(console_output)
        totals = cons_op[-1]
        cons_op=cons_op[2:-1]
        sorted_consop = []
        for i in cons_op:
            sorted_consop.append((i,int(i["delta_loc"])))

        sorted_consop.sort(key = getdloc,reverse=True)
        cons_op=[]
        for each in sorted_consop:
            cons_op.append(each[0])

        console_output="<i>##NOTE: <br>NC - NO Comment lines <br>LOC - Lines Of Code <br></i>"
        console_output+= ("<h4>Source Build : " + source + "</h4>")
        console_output+= ("<h4>Target Build : " + target + "</h4>")
       
        if type!="web":
            console_output+= ("Showing 15 out of " + str(len(cons_op)-3))
            console_output+= "<table style='font-size: 85%'>"
            console_output+= "<tr>"
            for i in cons_op[0].keys():
                console_output+= ("<th>"+i+"</th>")
            console_output+= "</tr>"
            for i in range(15):
                console_output+= "<tr>"
                # log("DEB1",cons_op[i])
                for r in cons_op[i].keys():
                    console_output+= ("<td>" + cons_op[i][r] if cons_op[i][r]!=None else "NA" + "</td>")
                console_output+= "</tr>"

            console_output+= ("<tr><th>TOTAL(for all components):</th>" + ''.join(["<th></th>"]*(len(cons_op[0].keys())-1))+"</tr>")
            
            console_output+= "<tr>"
            totals["comp"]=str(len(cons_op))
            for i in totals.keys():
                if i != "de_mgr":
                    console_output+= ("<th>"+totals[i]+"</th>")
                else:
                    console_output+= ("<th></th>")    
            console_output+= "</tr>"       
            console_output+= "</table>"  
        else:
            console_output+= "<hr>"
            console_output+= ("Showing 5 out of " + str(len(cons_op)-3))
            for i in range(5):
                console_output+= "<ul>"
                console_output+= ("<li><strong>Component</strong> : " + cons_op[i]["comp"] + "</li>")
                console_output+= ("<li><strong>DE Manager</strong> : " + cons_op[i]["de_mgr"] + "</li>")
                console_output+= "</ul>"
                console_output+= "<pre>\tSource\t|\tTarget\t|\tDelta<i>[Target-Source]\t</i></pre>"
                console_output+= ("<pre>LOC: \t" + cons_op[i]["r1_loc"] + "\t|\t" + cons_op[i]["r2_loc"] + "\t|\t" + cons_op[i]["delta_loc"] + "</pre>") 
                console_output+= ("<pre>NC: \t" + cons_op[i]["r1_nc"] + "\t|\t" + cons_op[i]["r2_nc"] + "\t|\t" + cons_op[i]["delta_nc"] + "</pre>") 
                console_output+= "<hr>"
            console_output+= "<hr>"    
            console_output+= "<h5>TOTAL(for all components):</h5>"
            console_output+= "<ul>"
            totals["comp"]=str(len(cons_op))
            labels = ["Target LOC","Delta NC","DE Manager","Components","Target NC","Source NC","Delta LOC","Source LOC"]
            for i in range(len(totals.keys())):
                if i != 2:
                    console_output+= ("<li>" + labels[i]+ ": " + totals[list(totals.keys())[i]]+"</li>")  
            console_output+= "</ul>"      
        log("console op", console_output)
        return console_output
    else:
        return error

def pims_get_loc_for_lineup(proj_name,efr_id):
    query = "pims gsr -r loc_for_proj "
    error=""
    if proj_name!="" or efr_id!="":   
        if proj_name:
            query+= ("-proj " + proj_name)
        else:
            query+= ("-efr_id EFR-00000"+efr_id[-6:])    
        query += " -format json"  
        # print("lu loc")  
        log("query",query)
        process = subprocess.Popen("export LC_ALL='en_US.UTF-8'\n"+query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        console_output = process.stdout.read().decode("UTF8")
        # log("consop",console_output)
        error = process.stderr.read().decode("UTF8")
        if len(error)==0:
            cons_op = json.loads(console_output)
            # log("len of consop", str(len(cons_op))+' '.join(cons_op[0].keys()))
            console_output=""
            fields = ["Project","efr_id","No of Components","NC-LOC","Comments","Total KLOC's"]
            labels = ["col_"+str(i) for i in range(1,8)]
            console_output+= "<ul>"
            for i in range(len(fields)):
                console_output+= ("<li>" + fields[i] +": "+ cons_op[0][labels[i]] + "</li>")
            console_output+= "</ul><hr>"

            console_output+= "<h4>Components:</h4>"
            cons_op = cons_op[5:]
            if len(cons_op)<15:
                console_output+= ("Showing all components")
                console_output+= "<ul>"
                for i in range(len(cons_op)):
                    console_output+= ("<li>" + cons_op[i]["col_1"] + "</li>")  
                console_output+= "</ul>"
            else:   
                console_output+= "<ul>"       
                console_output+= ("Showing 15 out of " + str(len(cons_op)))
                for i in range(15):
                    console_output+= ("<li>" + cons_op[i]["col_1"] + "</li>")
                console_output+= "</ul>"
    else:
        error = "Sorry couldn't find the data you were looking for. Try again."
    if error:
        return error
    else:
        return console_output    

def pims_get_loc_by_cat(proj_name,efr_id,type): 
    query = "pims gsr -r loc_for_categories "
    error=""
    if proj_name!="" or efr_id!="":   
        if proj_name:
            query+= ("-proj " + proj_name)
        else:
            query+= ("-efr_id EFR-00000"+efr_id[-6:])    
        query += " -format json"  
        # print("lu loc")  
        log("query",query)
        process = subprocess.Popen("export LC_ALL='en_US.UTF-8'\n"+query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        console_output = process.stdout.read().decode("UTF8")
        error = process.stderr.read().decode("UTF8")
        if len(error)==0:
            json_cons_op = json.loads(console_output)
            # log("len of consop", str(len(cons_op))+' '.join(cons_op[0].keys()))
            console_output="<h4>"+json_cons_op[0]["col_1"]+"</h4>"
            console_output+= ("Project: "+json_cons_op[1]["col_1"]+"<br>")
            console_output+= ("EFR_ID: "+json_cons_op[1]["col_2"]+"<br><h5>Components:</h5>")
            fields = ["col_"+str(i) for i in range(1,10)]
            #Components
            i=6
            j=0
            old_consop = console_output
            console_output= "<ul>"
            while(json_cons_op[i]["col_1"]!="Total LOC by Category :"):
                if(j<=10 and json_cons_op[i]["col_1"]!=""):
                    console_output+= ("<li>" + json_cons_op[i]["col_1"] + "</li>")
                    j+=1
                i+=1
            console_output= (old_consop + "Showing " + str(j) + " out of " + str(i-6) + " results" + console_output)        
            console_output+= "</ul><h5><i> Grand Total = NC+Comments+Blanks </i></h5><br>"
            console_output+= "<h5><strong>Total LOC by Platforms :</strong></h5>"
            # Total LOC by Categories :
            labels=["Category","","Total Components","Total NC Lines","Total Comments","Total Blanks","Grand Total"]
            cat_loc=[]
            i+=3
            j=1
            while(json_cons_op[i]["col_1"]!="Total LOC by Functionality:"):
                if(json_cons_op[i]["col_7"]!=""):
                    cat_loc.append((json_cons_op[i],int(json_cons_op[i]["col_7"])))
                i+=1  
            # print("-------WORKING---------")                

            cat_loc.sort(key = getdloc,reverse=True)
            cons_op=[]
            for each in cat_loc:
                cons_op.append(each[0])
            if type=="web":
                console_output+= ("Showing 11 out of " + str(len(cat_loc)-1) + " Platforms")    
                console_output+= "<table style='font-size: 85%'>"
                console_output+= "<tr>"
                for l in labels:
                    if l!="":
                        console_output+= ("<th>"+l+"</th>")
                console_output+= "</tr>"

                while(j<=11):
                    console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        if r!="col_2":
                            console_output+= ("<td>" + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</td>")
                    console_output+= "</tr>"
                    # print (cons_op[i][r])
                    j+=1

                console_output+= ("<tr><th>TOTAL:</th>" + ''.join(["<th></th>"]*(len(labels)-2))+"</tr>")
                console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    if r!="col_2":
                        console_output+= ("<td>" + cons_op[0][r] if cons_op[0][r]!=None else "NA" + "</td>")
                console_output+= "</tr>"       
                console_output+= "</table><br>"
            else:
                console_output+= ("Showing 4 out of " + str(len(cat_loc)-1) + " Platforms")    
                console_output+= "<hr>"
                while(j<4):
                    console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        if r!="col_2":
                            console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</li>")
                    console_output+= "</ul><hr>"
                    # print (cons_op[i][r])
                    j+=1

                console_output+= ("<h5>TOTAL:</h5>")
                console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    if r!="col_2" and r!="col_1":
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[0][r] if cons_op[0][r]!="" else "NA" + "</li>")
                console_output+= "</ul>"       
                console_output+= "<br>"
            console_output+= "<h5><strong>Total LOC by Features :</strong></h5>"
        
            # Total LOC by functionality   
            labels=["Function","Category","Total Components","Total NC Lines","Total Comments","Total Blanks","Grand Total"]
            functional_loc=[]
            i+=3
            j=1
            while(json_cons_op[i]["col_1"]!="Total LOC by DE Mgr :"):
                if(json_cons_op[i]["col_7"]!=""):
                    functional_loc.append((json_cons_op[i],int(json_cons_op[i]["col_7"])))
                i+=1  

            functional_loc.sort(key = getdloc,reverse=True)
            cons_op=[]
            for each in functional_loc:
                cons_op.append(each[0])
            if type=="web":
                console_output+= ("Showing 11 out of " + str(len(functional_loc)-1) + " Features")    
                console_output+= "<table style='font-size: 85%'>"
                console_output+= "<tr>"
                for l in labels:
                    console_output+= ("<th>"+l+"</th>")
                console_output+= "</tr>"
                while(j<=11):
                    console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        console_output+= ("<td>" + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</td>")
                    console_output+= "</tr>"
                    j+=1

                console_output+= ("<tr><th>TOTAL:</th>" + ''.join(["<th></th>"]*(len(labels)-1))+"</tr>")
                console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    console_output+= ("<td>" + cons_op[0][r] if cons_op[0][r]!=None else "NA" + "</td>")
                console_output+= "</tr>"       
                console_output+= "</table><br>"
            else:
                console_output+= ("Showing 4 out of " + str(len(functional_loc)-1) + " Features")    
                console_output+= "<hr>"
                while(j<=4):
                    console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</li>")
                    console_output+= "</ul>"
                    j+=1

                console_output+= ("<h5>TOTAL:</h5>")
                console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    if r!="col_1" and r!="col_2":
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[0][r] if cons_op[0][r]!=None else "NA" + "</li>")
                console_output+= "</ul>"       
                console_output+= "<br>"

            console_output+= "<h5><strong>Total LOC by DE Mgr :</strong></h5>"

            # Total LOC by DE Mgr :
            labels=["DE Manager","Category","Total Components","Total NC Lines","Total Comments","Total Blanks","Grand Total"]
            demgr_loc=[]
            i+=3
            j=1
            while(json_cons_op[i]["col_1"]!="Total LOC by list of components :"):
                if(json_cons_op[i]["col_7"]!=""):
                    demgr_loc.append((json_cons_op[i],int(json_cons_op[i]["col_7"])))
                i+=1  

            demgr_loc.sort(key = getdloc,reverse=True)
            cons_op=[]
            for each in demgr_loc:
                cons_op.append(each[0])

            if type=="web":
                console_output+= ("Showing 11 out of " + str(len(demgr_loc)-1) + " DE Managers")    
                console_output+= "<table style='font-size: 85%'>"
                console_output+= "<tr>"
                for l in labels:
                    console_output+= ("<th>"+l+"</th>")
                console_output+= "</tr>"
                while(j<=11):
                    console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        console_output+= ("<td>" + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</td>")
                    console_output+= "</tr>"
                    j+=1

                console_output+= ("<tr><th>TOTAL:</th>" + ''.join(["<th></th>"]*(len(labels)-1))+"</tr>")
                console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    console_output+= ("<td>" + cons_op[0][r] if cons_op[0][r]!=None else "NA" + "</td>")
                console_output+= "</tr>"       
                console_output+= "</table><br>"
            else:
                console_output+= ("Showing 4 out of " + str(len(demgr_loc)-1) + " DE Managers")    
                console_output+= "<hr>"
                while(j<4):
                    console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[j][r] if cons_op[j][r]!=None else "NA" + "</li>")
                    console_output+= "</ul>"
                    j+=1

                console_output+= ("<h5>TOTAL:</h5>")
                console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    if r!="col_1" and r!="col_2":
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + cons_op[0][r] if cons_op[0][r]!=None else "NA" + "</li>")
                console_output+= "</ul>"       
                console_output+= "<br>"   
            console_output+= "<h5><strong>Total LOC by list of Components :</strong></h5>"

            # Total LOC by list of components:
            labels=["Component Name","Category","Function","DE Manager","Locale","Total NC Lines","Total Comments","Total Blanks","Grand Total"]
            # comp_loc=[]
            i+=3
            j=0
            # while(cons_op[i]["col_1"]!="Total LOC by :"):
            #     if(cons_op[i]["col_7"]!=""):
            #         comp_loc.append((cons_op[i],int(cons_op[i]["col_7"])))
            #     i+=1  

            # comp_loc.sort(key = getdloc,reverse=True)
            # cons_op=[]
            # for each in comp_loc:
            #     cons_op.append(each[0])
            if type=="web": 
                console_output += "<table style='font-size: 85%'>"
                console_output+= "<tr>"
                for l in labels:
                    if l!="Locale":
                        console_output+= ("<th>"+l+"</th>")
                console_output+= "</tr>"
                while(j<=10):
                    console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        if r!="col_5":
                            console_output+= ("<td>" + json_cons_op[i][r] if json_cons_op[i][r]!=None else "NA" + "</td>")
                    console_output+= "</tr>"
                    j+=1
                    i+=1

                console_output+= ("<tr><th>TOTAL:</th>" + ''.join(["<th></th>"]*(len(labels)-1))+"</tr>")
                console_output+= "<tr>"
                    # log("DEB1",cons_op[i])
                for r in fields[:len(labels)]:
                    if r!="col_5":
                        console_output+= ("<td>" + json_cons_op[-1][r] if json_cons_op[-1][r]!=None else "NA" + "</td>")
                console_output+= "</tr>"       
                console_output+= "</table><br>"
            else:
                console_output+= "<hr>"
                while(j<=4):
                    console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                    for r in fields[:len(labels)]:
                        if r!="col_5":
                            console_output+= ("<li>" + labels[fields.index(r)] + ": " + json_cons_op[i][r] if json_cons_op[i][r]!=None else "NA" + "</li>")
                    console_output+= "</ul>"
                    j+=1
                    i+=1
                    console_output+= "<hr>"

                console_output+= ("<h5>TOTAL:</h5>")
                console_output+= "<ul>"
                    # log("DEB1",cons_op[i])
                ignore = ["col_"+str(i) for i in [1,2,3,4,5]]    
                for r in fields[:len(labels)]:
                    if r not in ignore:
                        console_output+= ("<li>" + labels[fields.index(r)] + ": " + json_cons_op[-1][r] if json_cons_op[-1][r]!=None else "NA" + "</li>")
                console_output+= "</ul>"       
                console_output+= "<br>"
    else:
        error = "Sorry couldn't find the data you were looking for. Try again."
    if error:
        return error
    else:
        return console_output    

# PIMS DATA
def pims_new_prod_bld_list():
    try:
        with open("prodbldlist.pkl","rb") as file:
            f = file.read()
    except:            
        query = "pims gsr -r lineup_labels -lineup_label '*PROD_BUILD*' -start_time_month_dd,_yyyy 01/01/2019 -format json"
        log("query",query)
        process = subprocess.Popen("export LC_ALL='en_US.UTF-8'\n"+query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell =True)
        console_op = process.stdout.read().decode("UTF-8")
        error = process.stderr.read().decode("UTF-8")

        if(len(error)==0):
            cons_op = json.loads(console_op)
            prodbldlist=[]
            for i in cons_op:
                prodbldlist.append(i["label"][11:])
            # print(prodbldlist, len(prodbldlist), len(cons_op))
            with open("prodbldlist.pkl","wb") as file:
                pickle.dump(prodbldlist,file)
        else:
            log("ERROR at pims_new_prod_bld_list",error)

def pims_new_proj_list():
    try:
        file = open("projlist.pkl","rb")
    except:    
        query = "pims gsr -r active_lineups_details_cli -format json"
        log("query",query)
        process = subprocess.Popen("export LC_ALL='en_US.UTF-8'\n"+query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell =True)
        console_op = process.stdout.read().decode("UTF-8")
        error = process.stderr.read().decode("UTF-8")

        if(len(error)==0):
            cons_op = json.loads(console_op)
            projlist=[]
            for i in cons_op:
                projlist.append(i["Lineup"])
            # print(prodbldlist, len(prodbldlist), len(cons_op))
            with open("projlist.pkl","wb") as file:
                pickle.dump(projlist,file)
        else:
            log("ERROR at pims_new_proj_list",error)

if __name__=="__main__":
    #scrapeBIT("ncs", "", "", 'webex')

    #print(get_smu_data('how many optional SMUs', 'webex')['results'])
    print(get_rally_data('Rally feature of dpatwa in 731 release', 'dpatwa', 'webex'))

