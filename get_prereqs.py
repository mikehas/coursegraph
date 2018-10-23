#!/usr/bin/python3

import csv
import re
from pprint import pprint
import json
import sys

courses = {}

limit =  -1# -1 for no limit
filter = "CPE,CSC" # comma separated list of

name_links = []
graph = {"nodes":[], "links": [] }
name_idx = {}
idx = 0
groups_idx = 0
groups = {}
all_prereqs = {}

depts = []

def getGroupNum(prefix):
    global groups_idx, groups

    your_g = 0

    if prefix not in groups:
        groups_idx = groups_idx + 1
        groups[prefix] = groups_idx
        your_g = groups_idx
    else:
        your_g = groups[prefix]

    return your_g

def addNode(name, prefix):
    global idx
    graph['nodes'].append({'id':name, 'group': getGroupNum(prefix)})
    idx = idx + 1

def writeFile(data, filename):
    f = open(filename, "+w")
    f.write(json.dumps(data,sort_keys=True, indent=4))

def cleanCourseId(str):
    return str.replace(u'\xa0', u' ')

def cleanDict(row):
    for key, val in row.items():
        row[key] = val.replace(u'\xa0', u' ')

def addDept(name):
    global depts
    if name not in depts:
        depts.append(name)

f = open('courses.csv', 'r')
with f:
    itr = 0
    reader = csv.DictReader(f)

    for row in reader:
        if filter != "" and row['courseprefix'] not in [ x.strip() for x in filter.split(',')]:
            continue

        addDept(row['courseprefix'])
        itr = itr + 1
        if limit != -1 and itr > limit:
          break
        course = {}
        # row['course_id'] = cleanCourseId(row['course_id'])
        cleanDict(row)
        print(row['course_id'])
        courses.update({row['course_id']: row})

for c in courses.values():
    if c:
        prereqs = []

        if 'prequisites' in c:
           prereqs = re.findall(r'[A-Z]+\s[A-Z]?[0-9]+[A-Z]?', c['prequisites'])

        addNode(c['course_id'], c['courseprefix'])

        for prereq in prereqs:
            name_links.append({'source':prereq, 'target': c['course_id'], 'value': 1})
            if prereq not in all_prereqs:
                all_prereqs[prereq] = 'generated'

for p in all_prereqs:
    if p not in courses:
        print(p)
        addNode(p, p.split()[0])

graph['links'] = name_links

pprint(graph)
pprint(depts)

writeFile(graph, "output.json")
