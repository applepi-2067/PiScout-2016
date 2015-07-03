from piscout import *

scout = PiScout()
scout.loadsheet('sheet.png')

num1 = scout.rangefield('O5', 0, 9)
num2 = scout.rangefield('O6', 0, 9)
num3 = scout.rangefield('O7', 0, 9)
num4 = scout.rangefield('O8', 0, 9)

match1 = scout.rangefield('O10', 0, 1)
match2 = scout.rangefield('O11', 0, 9)
match3 = scout.rangefield('O12', 0, 9)

totes = scout.rangefield('J15', 1, 3)
zonecont = scout.rangefield('J16', 1, 4)
stepcont = scout.rangefield('J17', 1, 4)

stacked = scout.boolfield('W15')
inzone = scout.boolfield('W16')

#The following wall of code could probably be done iteratively, but I'm too lazy to do that at the moment
stacks = [None]*6

stacks[0] = {
	'capping': scout.boolfield('L20'),
	'height': scout.rangefield('G21', 1, 6),
	'capped': scout.boolfield('G22'),
	'noodled': scout.boolfield('L22')
}
stacks[1] = {
	'capping': scout.boolfield('Y20'),
	'height': scout.rangefield('T21', 1, 6),
	'capped': scout.boolfield('T22'),
	'noodled': scout.boolfield('Y22')
}
stacks[2] = {
	'capping': scout.boolfield('L24'),
	'height': scout.rangefield('G25', 1, 6),
	'capped': scout.boolfield('G26'),
	'noodled': scout.boolfield('L26')
}
stacks[3] = {
	'capping': scout.boolfield('Y24'),
	'height': scout.rangefield('T25', 1, 6),
	'capped': scout.boolfield('T26'),
	'noodled': scout.boolfield('Y26')
}
stacks[4] = {
	'capping': scout.boolfield('L28'),
	'height': scout.rangefield('G29', 1, 6),
	'capped': scout.boolfield('G30'),
	'noodled': scout.boolfield('L30')
}
stacks[5] = {
	'capping': scout.boolfield('Y28'),
	'height': scout.rangefield('T29', 1, 6),
	'capped': scout.boolfield('T30'),
	'noodled': scout.boolfield('Y30')
}

print("Team Number:")
print(1000*num1 + 100*num2 + 10*num3 + num4)

print("Match Number")
print(100*match1 + 10*match2 + match3)

print("Totes in auto zone: " + str(totes))
print("Containers in auto zone: " + str(zonecont))
print("Containers from step: " + str(stepcont))
print("Stacked set? " + str(stacked))
print("Moved into auto zone? " + str(inzone))

for s in stacks:
	if s['height'] == 0:
		continue
	if s['capping']:
		print('Capped a stack of ' + str(s['height']))
	else:
		print('Built a stack of ' + str(s['height']))
		print('Capped: ' + str(s['capped']))
	print('Noodled: ' + str(s['noodled']))