#!/usr/bin/python

import requests
import socket
import json
import math
from sys import argv
from getpass import getpass

json_data = {
        "username":"",
        "password":""
}

short_lesson_name = {
        "Telekommunikation":"Tele",
        "Technologie und Planung":"TePe",
        "Gesellschaftliche Bildung":"GeBi",
        "Systeme und Netze":"SyNe",
        "Bewegung und Sport":"BuS",
        "Inklusion / Migration":"Inklusion",
        "Lehrausgang/Lehrausflug":"Ausflug",
}

short_teacher_name = {
}

host = 'digitalesregister.it'
default_subdomain = 'tfobz'

# -------------------------------------------------------- #

login_url = '/v2/api/auth/login'
dashboard_url = '/v2/api/student/dashboard/dashboard'
calendar_url = '/v2/api/calendar/student'
notifications_url = '/v2/api/notification/unread'
grades_url = '/v2/api/student/all_subjects'
absences_url = '/v2/api/student/dashboard/absences'

def printSpaced(msg, n):
    print(msg[:n], end='')
    l = len(msg)
    while l < n:
        print(' ', end='')
        l+=1

def printColCentered(msg, n, c):
    if n >= 0:
        print(f'\033[{c}m', end='')
        print(msg[:n].center(n, ' '), end='')
        print('\033[0m', end='')
    else:
        print(f'\033[{c}m', end='')
        print(msg, end='')
        print('\033[0m', end='')

def printCol(msg, n, c):
    if n >= 0:
        print(f'\033[{c}m', end='')
        printSpaced(msg, n)
        print('\033[0m', end='')
    else:
        print(f'\033[{c}m', end='')
        print(msg, end='')
        print('\033[0m', end='')


def dashboard(cookies, future=True, n=7):
    res = requests.post('https://' + host +  dashboard_url, cookies=cookies, json={"viewFuture":future})

    i = 0
    for day in json.loads(res.content.decode()):
        if i >= n:
            break
        # print(i, day['date'], ':')
        for item in day['items']:
            if future:
                printCol('+' + str(i) + ' ', int(math.log10(n)+1)+2, '0;39')
                if 'deadlineFormatted' in item:
                    printSpaced(item['deadlineFormatted'].split(',')[0], 3)
                else:
                    printSpaced("", 3)
            else:
                printCol('-' + str(i+1) + ' ', int(math.log10(n)+1)+2, '0;39')
                print(day['date'], end='')
            print(' ', end='')
            if 'label' in item:
                if item['label'] in short_lesson_name:
                    printSpaced(short_lesson_name[item['label']], 4)
                else:
                    printSpaced(item['label'], 4)
                print(end=': ')
                printCol(item['title'], 12, '1;39')
                print(item['subtitle'])
            else:
                printSpaced('', 4)
                print(end='  ')
                printCol(item['title'], 12, '1;39')
                print(item['subtitle'])
                # print(item['label'], end='')
        i+=1

def past(cookies, n=7):
    dashboard(cookies, future=False, n=n)

def printHour(day, i, cellen, normal_col, centered=False):
    exam_col = '1;31'
    test_col = '1;33'
    pruef_col = '1;36'
    homework_col = '1;32'
    col = normal_col

    if day['1']['1'][str(i)]['isLesson']:
        if len(day['1']['1'][str(i)]['lesson']['homeworkExams']) > 0:
            if day['1']['1'][str(i)]['lesson']['homeworkExams'][0]['typeId'] == 3:
                col = exam_col
            elif day['1']['1'][str(i)]['lesson']['homeworkExams'][0]['typeId'] == 2:
                col = test_col
            elif day['1']['1'][str(i)]['lesson']['homeworkExams'][0]['typeId'] == 1:
                col = pruef_col
            else:
                col = homework_col
        else:
            col = normal_col

        if day['1']['1'][str(i)]['lesson']['subject']['name'] in short_lesson_name:
            if centered:
                printColCentered(short_lesson_name[day['1']['1'][str(i)]['lesson']['subject']['name']], cellen, col)
            else:
                printCol(short_lesson_name[day['1']['1'][str(i)]['lesson']['subject']['name']], cellen, col)
        else:
            if centered:
                printColCentered(day['1']['1'][str(i)]['lesson']['subject']['name'], cellen, col)
            else:
                printCol(day['1']['1'][str(i)]['lesson']['subject']['name'], cellen, col)
    else:
        printSpaced('', cellen)

def calendar_extended(cookies, hours=11, cellen=16, spacer=' '):
    if spacer == '\0':
        spacer = ' | '
    res = requests.post('https://' + host +  calendar_url, cookies=cookies)
    data = json.loads(res.content.decode())
    lesson_col = '1;39'
    teacher_col = '0;39'
    for i in range(1, hours):
        print(end=spacer)
        for day in data:
            if str(i) in data[day]['1']['1']:
                printHour(data[day], i, cellen, "1;39", centered=False)
                # if data[day]['1']['1'][str(i)]['isLesson']:
                #     if data[day]['1']['1'][str(i)]['lesson']['subject']['name'] in short_lesson_name:
                #         printCol(short_lesson_name[data[day]['1']['1'][str(i)]['lesson']['subject']['name']], cellen, lesson_col)
                #     else:
                #         printCol(data[day]['1']['1'][str(i)]['lesson']['subject']['name'], cellen, lesson_col)
                # else:
                #     printSpaced('', cellen)
            else:
                t = i
                while t >= 0:
                    if str(t) in data[day]['1']['1']:
                        if data[day]['1']['1'][str(t)]['lesson']['subject']['name'] in short_lesson_name:
                            printCol(short_lesson_name[data[day]['1']['1'][str(t)]['lesson']['subject']['name']], cellen, lesson_col)
                        else:
                            printCol(data[day]['1']['1'][str(t)]['lesson']['subject']['name'], cellen, lesson_col)
                        break
                    t-=1
            print(end=spacer)
        print()

        print(end=spacer)
        for day in data:
            if str(i) in data[day]['1']['1']:
                if data[day]['1']['1'][str(i)]['isLesson']:
                    teachers = ''
                    for teacher in data[day]['1']['1'][str(i)]['lesson']['teachers']:
                        if teacher['lastName'] in short_teacher_name:
                            teachers += ', ' + short_teacher_name[teacher['lastName']]
                        else:
                            teachers += ', ' + teacher['lastName']
                    printCol(teachers[2:], cellen, teacher_col)
                else:
                    printSpaced('', cellen)
            else:
                t = i
                while t >= 0:
                    if str(t) in data[day]['1']['1']:
                        teachers = ''
                        for teacher in data[day]['1']['1'][str(t)]['lesson']['teachers']:
                            teachers += ', ' + teacher['lastName']
                        printCol(teachers[2:], cellen, teacher_col)
                        break
                    t-=1
            print(end=spacer)
        print()

def calendar(cookies, hours=11, cellen=8, spacer='|'):
    if spacer == '\0':
        spacer = ' '
    res = requests.post('https://' + host +  calendar_url, cookies=cookies)
    data = json.loads(res.content.decode())
    col = '0;39'

    for i in range(1, hours):
        print(end=spacer)
        for day in data:
            if str(i) in data[day]['1']['1']:
                printHour(data[day], i, cellen, col, centered=True)
            else:
                t = i
                while t >= 0:
                    if str(t) in data[day]['1']['1']:
                        printHour(data[day], t, cellen, col, centered=True)
                        break
                    t-=1
            print(end=spacer)
        print()

    # print("Calendar".upper())

def notifications(cookies):
    res = requests.post('https://' + host +  notifications_url, cookies=cookies)
    data = json.loads(res.content.decode())

    for notification in data:
        if 'subTitle' in notification:
            print(notification['title'], notification['subTitle'])
        else:
            print(notification['title'])

def fetch(cookies):
    space = 22
    # import datetime
    # dt = datetime.datetime.now()
    # td = datetime.timedelta(days=7)
    # print(dt)
    # print(dt+td)
    # res = requests.post('https://' + host +  calendar_url, cookies=cookies)
    #
    # printCol("DAYS:\n", -1, '1;39')
    # print()

    res = requests.post('https://' + host +  grades_url, cookies=cookies)
    data = json.loads(res.content.decode())
    grades_total = 0
    grades_sum = 0
    subjects_width_grades = 0
    for subject in data['subjects']:
        grades_total += len(subject['grades'])
        if len(subject['grades']) > 0:
            grades_sum += subject['averageSemester']
            subjects_width_grades += 1

    printCol("GRADES:\n", -1, '1;39')
    printSpaced("total:", space)
    print(grades_total)
    printSpaced("average:", space)
    print(grades_sum / subjects_width_grades)
    printSpaced("sum:", space)
    print(grades_sum)

    res = requests.post('https://' + host +  absences_url, cookies=cookies)
    data = json.loads(res.content)

    printCol("\nABSENCES:\n", -1, '1;39')
    printSpaced("total:", space)
    print(data['statistics']['counter'])
    printSpaced("percentage:", space)
    print(data['statistics']['percentage'])
    printSpaced("for school:", space)
    print(data['statistics']['counterForSchool'])
    printSpaced("not justified:", space)
    print(data['statistics']['notJustified'])

def subjects(cookies):
    res = requests.post('https://' + host +  grades_url, cookies=cookies)
    data = json.loads(res.content.decode())

    printCol("Subject name:", 18, '0;39')
    printCol(" avg:", 6, '0;39')
    printCol(" obs:", 6, '0;39')
    printCol(" abs:", 6, '0;39')
    print()

    for subject in data['subjects']:
        if subject['subject']['name'] in short_lesson_name:
            printCol(short_lesson_name[subject['subject']['name']], 16, '1;39')
        else:
            printCol(subject['subject']['name'], 16, '1;39')
        print(':  ', end='')
        if subject['averageSemester'] == None:
            print("None", end='')
        elif subject['averageSemester'] >= 5.5:
            printCol(str(subject['averageSemester']), 4, '1;32')
        else:
            printCol(str(subject['averageSemester']), 4, '1;31')
        print(end='  ')
        printCol(str(subject['countObservations']), 4, '0;39')
        print(end='  ')
        print(str(subject['absences']))
        if subject['averageSemester'] == None:
            continue

        # print(end='    ')
        # l = 4
        # for grade in subject['grades']:
        #     print(end='(')
        #     if not 'grade' in grade:
        #         print("None", end='')
        #     elif float(grade['grade']) >= 5.5:
        #         printCol(grade['grade'], -1, '1;32')
        #     else:
        #         printCol(grade['grade'], -1, '1;31')
        #     print(end=', ')
        #     printCol(str(grade['weight']), -1, '1;39')
        #     l += len(grade['grade']) + len(str(grade['weight'])) + 5
        #     print(end=') ')
        # print()
        # if l < 36:
        #     l = 36
        # for i in range(l-1):
        #     printCol('-', -1, '1;39')
        # print()

def absences(cookies):
    import datetime

    res = requests.post('https://' + host +  absences_url, cookies=cookies)
    data = json.loads(res.content.decode())
    
    # res = requests.post('https://' + host +  calendar_url, cookies=cookies)
    # calendar = json.loads(res.content.decode())

    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Sammstag", "Sonntag"]
    missing_minutes = [0]*7
    total_minutes = [50*6, 50*9, 50*6, 50*9, 50*6, 0, 0]

    for day in data['absences']:
        weekday = datetime.date.fromisoformat(day['date']).weekday()
        # print(weekdays[weekday], end=' ')
        for hour in day['group']:
            # print(hour['minutes'], end=' ')
            missing_minutes[weekday] += hour['minutes']
        # print()
    
    printCol("ABSENCES:\n" , -1, "1;39")
    printCol("Weekday"     , 16, "0")
    printCol("min"         , 8, "0")
    printCol("days"       , -1, "0")
    print()
    for i in range(7):
        if total_minutes[i] > 0:
            printCol(weekdays[i], 16, "0")
            printCol(str(missing_minutes[i]), 8, "0")
            printCol(str(int(missing_minutes[i]/total_minutes[i]*100)/100), 8, "0")
            # printCol(str(int(missing_minutes[i]/50*100)/100), 8, "0")
            print()

def gradecalc(cookies, data=None):
    if data == None:
        res = requests.post('https://' + host + grades_url, cookies=cookies)
        data = json.loads(res.content.decode())

    print("GRADECALC:")
    printCol("0", 4, "0")
    printCol("Don't imort", -1, "1;39")
    print()
    for i in range(len(data["subjects"])):
        printCol(str(i+1), 4, "0")
        if data["subjects"][i]['averageSemester'] == None:
            printCol("None", 4, '1;39')
        elif data["subjects"][i]['averageSemester'] >= 5.5:
            printCol(str(data["subjects"][i]['averageSemester']), 4, '1;32')
        else:
            printCol(str(data["subjects"][i]['averageSemester']), 4, '1;31')
        printCol(" " + str(len(data["subjects"][i]['grades'])), 4, '0;39')
        if data["subjects"][i]["subject"]["name"] in short_lesson_name:
            printCol(" " + short_lesson_name[data["subjects"][i]["subject"]["name"]], -1, "1;39")
        else:
            printCol(" " + data["subjects"][i]["subject"]["name"], -1, "1;39")
        print()
    
    c = input("Choose which grades to import (q to quit): ")
    grades = []
    sname = "None"
    if c == 'q':
        for i in range(len(data["subjects"])+3):
            print(end="\r\033[K\033[A")
        return
    try:
        int(c)
    except: 
        for i in range(len(data["subjects"])+3):
            print(end="\r\033[K\033[A")
        printCol("Invalid option\n", -1, '1;31')
        gradecalc(cookies, data)
        return
    if int(c) < 0 or int(c) > len(data["subjects"]):
        for i in range(len(data["subjects"])+3):
            print(end="\r\033[K\033[A")
        printCol("Invalid subject\n", -1, '1;31')
        gradecalc(cookies, data)
        return
    elif (int(c) != 0):
        sname = data["subjects"][int(c)-1]["subject"]["name"]
        for grade in data["subjects"][int(c)-1]['grades']:
            if 'grade' in grade:
                grades.append([grade['grade'], grade['weight']])

    c = ""
    l = len(data["subjects"])+2
    while c != "q" and c != "Q":
        for i in range(l):
            print(end="\r\033[K\033[A")
        print(end="\033[K")
        print("Enter h for help.")
        printCol(sname + "\n", -1, '1;39')
        l = 3

        if c == "h":
            print("a <grade> <weight>  to add a grade (weight in %)")
            print("d <index>           to remove a grade")
            print("p                   to previous menu")
            print("q                   to quit")
            print("enter               to print list of grades again")
            l += 5
        elif c.startswith('p'):
            for i in range(l):
                print(end="\r\033[K\033[A")
            gradecalc(cookies, data)
            return
        elif c.startswith('d'):
            if len(c.split(' ')) == 2:
                try:
                    grades.pop(int(c.split(' ')[1]))
                except IndexError:
                    print("Invalid index: " + int(c.split(' ')[1]))
                    l += 1
                # except:
                #     for i in range(l):
                #         print(end="\r\033[K\033[A")
                #     print(end="\033[K")
                #     printCol("Invalid option for delete", -1, "1;31")
                c = ""
            else:
                print("Invalid index")
        elif c.startswith('a'):
            if len(c.split(' ')) == 3:
                try: 
                    int(c.split(' ')[1])
                    grades.append([c.split(' ')[1], int(c.split(' ')[2])])
                except:
                    printCol("Invalid option for add", -1, "1;31")
                c = ""
            else:
                print("Invalid syntax for Add")
        if c == "":
            t = 0
            g = 0
            for i in range(len(grades)):
                printCol(str(i), 4, "0")
                t += float(grades[i][0]) * grades[i][1]
                g += grades[i][1]
                if float(grades[i][0]) >= 5.5:
                    printCol(grades[i][0], 4, '1;32')
                else:
                    printCol(grades[i][0], 4, '1;31')
                print("", grades[i][1])
            if g != 0:
                print(end="Average: ")
                if t/g >= 5.5:
                    printCol(str(int(t/g*100)/100)+"\n", -1, '1;32')
                else:
                    printCol(str(int(t/g*100)/100)+"\n", -1, '1;31')
            else:
                print("Average: None")
            l += len(grades) + 1

        c = input("> ")

    for i in range(l+1):
        print(end="\r\033[K\033[A")

commands = [
    {
        'name':'dashboard',
        'short':'-d',
        'input':'int',
        'description':'Print dashboard n days in future',
        'function':dashboard
    },
    {
        'name':'past',
        'short':'-p',
        'input':'int',
        'description':'Print dashboard n days in past',
        'function':past
    },
    {
        'name':'calendar',
        'short':'-c',
        'description':'Print calendar of current week',
        'function':calendar
    },
    {
        'name':'calendar-extended',
        'short':'-ce',
        'description':'Print calendar of current week but nicer',
        'function':calendar_extended
    },
    {
        'name':'notifications',
        'short':'-n',
        'description':'Print out unread notifications',
        'function':notifications
    },
    {
        'name':'fetch',
        'short':'-f',
        'description':'Get general information',
        'function':fetch
    },
    {
        'name':'cell-width',
        'short':'--cell-width',
        'input':'int',
        'description':'Change the width of cells in calendar',
    },
    {
        'name':'credentials',
        'short':'--credentials',
        'input':'bool',
        'description':'Ask for credentials',
    },
    {
        'name':'subdomain',
        'short':'--subdomain',
        'input':'string',
        'description':'Change the school',
    },
    {
        'name':'spacer',
        'short':'--spacer',
        'input':'string',
        'description':'Change the spacer character for calendar',
    },
    {
        'name':'hours',
        'short':'--hours',
        'input':'int',
        'description':'Change how many hours are displayed in the calendar',
    },
    {
        'name':'subjects',
        'short':'-s',
        'description':'Get general information about all subjects.',
        'function':subjects,
    },
    {
        'name':'absences',
        'short':'-a',
        'description':'Get information about how much you where absent from each day.',
        'function':absences,
    },
    {
        'name':'gradecalc',
        'short':'-gc',
        'description':'Calculate grades.',
        'function':gradecalc,
    },
]

variables = {
    'cell-width':-1,
    'credentials':False,
    'subdomain':default_subdomain,
    'spacer':'\0',
    'hours':11,
}

def help():
    space = 20
    printCol('HELP: ' + argv[0] + '\n', -1, '1;39')
    printSpaced('  -h', space)
    print('Print this message')
    print()

    printCol("COMMANDS:\n", -1, '1;39')
    for cmd in commands:
        if 'function' in cmd:
            if 'input' in cmd:
                printSpaced('  ' + cmd['short'] + ' n', space)
                print(cmd['description'], end='')
                print(' (' + cmd['input'] + ')')
            else:
                printSpaced('  ' + cmd['short'], space)
                print(cmd['description'])

    print()
    printCol("SETTINGS:\n", -1, '1;39')
    for cmd in commands:
        if not 'function' in cmd:
            if 'input' in cmd and cmd['input'] != 'bool':
                printSpaced('  ' + cmd['short'] + ' n', space)
                print(cmd['description'], end='')
                print(' (' + cmd['input'] + ')')
            else:
                printSpaced('  ' + cmd['short'], space)
                print(cmd['description'])

def unknown_argument(arg, subcommand):
    print(f'Argument "{arg}" not allowed for "{subcommand}"!')

if __name__ == '__main__':
    # host = variables['subdomain'] + host
    # res = requests.post('https://' + host +  login_url, json=json_data)
    # cookies = res.cookies
    # requests.get('https://tfobz.digitalesregister.it/v2/?semesterWechsel=1')
    # res = requests.post('https://' + host + grades_url, cookies=cookies, json={'studentId':6263})
    # data = json.loads(res.content.decode())
    # for subject in data['subjects']:
    #     printSpaced(subject['subject']['name'], 24)
    #     print('  ' + str(subject['averageSemester']))
    # exit()

    if len(argv) <= 1:
        help()
        exit(-1)

    i = 1
    arg = -1
    found_func = False
    cell_width = -1
    func = []
    while i < len(argv):
        actual_cmd = False
        for cmd in commands:
            if argv[i] == cmd['short']:
                actual_cmd = True
                if 'function' in cmd:
                    func = cmd
                    if found_func:
                        print("ONLY ONE CMD ALLOWED")
                        exit()
                    found_func = True

                    # print(cmd['name'].upper())
                    if 'input' in cmd and len(argv) > i+1 and not argv[i+1].startswith('-'):
                        i+=1
                        # print('ARG:', argv[i])
                        try:
                            if int(argv[i]) <= 0:
                                raise
                            arg = int(argv[i])
                        except:
                            unknown_argument(argv[i], cmd['short'])
                            exit(0)
                else:
                    # print(cmd['name'].upper())
                    if cmd['input'] == 'bool':
                        variables[cmd['name']] = True
                    elif cmd['input'] == 'int' and len(argv) > i+1:
                        i+=1
                        # print('ARG:', argv[i])
                        try:
                            if int(argv[i]) <= 0:
                                raise
                            variables[cmd['name']] = int(argv[i])
                        except:
                            unknown_argument(argv[i], cmd['short'])
                            exit(0)
                    elif cmd['input'] == 'string' and len(argv) > i+1:
                        i+=1
                        variables[cmd['name']] = argv[i]
                    else:
                        print('Argumetn required for "' + cmd['short'] + '"!')
                        exit(0)
        if not actual_cmd:
            help()
            exit(0)
        i+=1

    if not found_func:
        print("Nothing to do...")
        exit()

    if variables['subdomain'] == "":
        variables['subdomain'] = input("Subdomain: ")
    # else:
    #     print(variables['subdomain'])

    if json_data['password'] == "" and json_data['username'] != "":
        print("Username:", json_data['username'])
        json_data['password'] = getpass()
    elif json_data['username'] == "" or variables['credentials']:
        json_data['username'] = input("Username: ")
        json_data['password'] = getpass()
        print()

    try:
        host = variables['subdomain'] + '.' + host
        res = requests.post('https://' + host +  login_url, json=json_data)
    except:
        print("No internet connection")
        exit(1)

    if not res.ok:
        print("Server unreachable.")
        exit(-1)


    try:
        data = json.loads(res.content)
    except:
        print("Ungueltiges subdomain")
        exit()

    if not 'loggedIn' in data:
        print("Not logged in because: " + data['error'])
        exit(0)

    cookies = res.cookies

    if func['name'] == 'dashboard' or func['name'] == 'past':
        if arg > 0:
            func['function'](cookies, n=arg)
        else:
            func['function'](cookies)
    elif func['name'].startswith('calendar'):
        if variables['cell-width'] > 0:
            func['function'](cookies, cellen=variables['cell-width'], spacer=variables['spacer'], hours=variables['hours'])
        else:
            func['function'](cookies, spacer=variables['spacer'], hours=variables['hours'])
    else:
        func['function'](cookies)

    # dashboard(cookies, future=True, n=16)
    # calendar(cookies)
    # calendar_extendet(cookies)
