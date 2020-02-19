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

        


def get_directory_data(question,type="web"):
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
    
    