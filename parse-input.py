#!/usr/bin/python

from people.models import Person

people = dict()
with open('input.txt', 'r') as inp:
  for line in inp:
    if ' : ' not in line:
      continue

    parts = line.split(' : ')

    skill_name = parts[0].strip(' *:')

    for measurement in parts[1].split(','):
      person_name, levels = (s.strip(' ]').lower() for s in measurement.split('['))
      if person_name not in people:
        people[person_name] = {}

      levels = {k[0].strip(): k[1].strip(' ]\n') for k in [l.split(':') for l in levels.split('/')]}
      for key in ('k', 'i'):
        levels[key] = int(levels[key]) - 1
        if levels[key] == 0:
          levels[key] = 1

      people[person_name][skill_name] = levels

print(people)
