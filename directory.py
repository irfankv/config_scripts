import subprocess
import re

# query = "/usr/cisco/bin/rchain -nth tashanka"
# process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# console_output = process.stdout.read().decode("UTF8")

# emp = []

# for emp1 in console_output.split('\n') :
#     (emp.append(emp1))

# directory = {}

# directory['id']= re.split(r"[\s]\s+",emp[4])[0]
# directory['name']= re.split(r"[\s]\s+",emp[4])[1]

# print(directory)

query = "/usr/cisco/bin/rchain -nh tashanka"
process = subprocess.Popen(
    query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
console_output = process.stdout.read().decode("UTF8")
directory = {}
if console_output:
    emp = []
    for emp1 in console_output.split("\n"):
        emp.append(emp1)
    directory["reportees"] = []
    directory["id"] = re.split("[\s]\s+", emp[len(emp) - 2])[0]
    directory["name"] = re.split("[\s]\s+", emp[len(emp) - 2])[1]
    directory["photo"] = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg" % (
        directory["id"]
    )
    # directory["title"] = re.split("[\s]\s+",emp[len(emp)-2])[2]
    directory["manager"] = re.split("[\s]\s+", emp[len(emp) - 3])[1]
    directory["manager-Id"] = re.split("[\s]\s+", emp[len(emp) - 3])[0]
    directory["manager-photo"] = "http://wwwin.cisco.com/dir/photo/zoom/%s.jpg" % (
        directory["manager-Id"]
    )
    # for i in range(1,len(emp)):
    #     title = re.split("[\s]\s+",emp[len(emp)-i])[2]
    #     if re.search("DIRECTOR",title):
    #         directory["DIRECTOR"] = re.split("[\s]\s+",emp[len(emp)-i])[1]
    #         directory["DIRECTOR-id"] = re.split("[\s]\s+",emp[len(emp)-i])[0]

query = "/usr/cisco/bin/rchain -th tashanka"
process = subprocess.Popen(
    query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
console_output = process.stdout.read().decode("UTF8")

title = []

if console_output:
    director = []
    for dirc in console_output.split("\n"):
        director.append(dirc)
    directory["title"] = re.split("[\s]\s+", director[len(director) - 2])[1]
    directory["DIRECTOR"] = []
    for i in range(1, len(director) - 2):
        # if re.search("DIRECTOR",re.split("[\s]\s+",director[len(director)-i])[1]):
        #     directory["DIRECTOR"].append(re.split("[\s]\s+",emp[len(emp)-i])[1] + "(" + re.split("[\s]\s+",emp[len(emp)-i])[0] + ")")

        if re.search("DIRECTOR", re.split("[\s]\s+", director[i])[1]):
            directory["DIRECTOR"].append(
                re.split("[\s]\s+", emp[i])[1]
                + "("
                + re.split("[\s]\s+", emp[i])[0]
                + ")"
            )
            # directory["DIRECTOR-id"] = re.split("[\s]\s+",emp[len(emp)-i])[0]

query = "/usr/cisco/bin/rchain -ph tashanka"
process = subprocess.Popen(
    query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
console_output = process.stdout.read().decode("UTF8")
phone = []
if console_output:
    for emp1 in console_output.split("\n"):
        phone.append(emp1)
    directory["phone-number"] = re.split("[\s]\s+", phone[len(phone) - 2])[1]

query = "/usr/cisco/bin/rchain -nrh tashanka"
process = subprocess.Popen(
    query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
console_output = process.stdout.read().decode("UTF8")
reportees = []
reports = []
if console_output:

    for rep in console_output.split("\n"):
        reports.append(rep)

    if len(reports) > 2:
        for rep in reports:
            reportees.append(re.split("[\s]\s+", rep))
        del reportees[len(reportees) - 1]
        person = reportees.pop(0)
    # print("reportees of %s are %s" %(person[1],reportees))
    directory["reportees"] = reportees
    directory["number-of-reportees"] = int(len(reportees))

query = "/usr/cisco/bin/rchain -elh tashanka"
process = subprocess.Popen(
    query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
console_output = process.stdout.read().decode("UTF8")

if console_output:
    loc_empId = []
    for rec in console_output.split("\n"):
        loc_empId.append(rec)

    directory["emp-number"] = re.split("[\s]\s+", loc_empId[len(loc_empId) - 2])[2]
    directory["location"] = re.split("[\s]\s+", loc_empId[len(loc_empId) - 2])[1]

# if re.search("([a-z]+|[A-Z]+)(\d+)",re.split("[\s]\s+",rep[len(rep)-2])[1]).group(1) :
#     loc = re.search("([a-z]+|[A-Z]+)(\d+)",re.split("[\s]\s+",rep[len(rep)-2])[1]).group(1)
#     if loc == "BGL":
#         directory['location'] = "Banglore Building" + re.search("([a-z]+|[A-Z]+)(\d+)",re.split("[\s]\s+",rep[len(rep)-2])[1]).group(2)
#     elif loc == "SJC":


# repo = []

# for rep in console_output.split('\n'):
#     repo.append(repo)
# for ia in repo:
#     print(ia)
#     #print(re.split("[\s]\s+",ia)[0])
#     #directory["reportees"].append({'id': re.split("[\s]\s+",ia)[0], "name":re.split("[\s]\s+",ia)[1]})
print(directory)
