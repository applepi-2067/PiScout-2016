from piscout import *

scout = PiScout()
scout.loadsheet('195.jpg')

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

telecont = scout.rangefield('J32', 1, 4)
coop = scout.rangefield('V32', 1, 4)
coopstack = scout.boolfield('V33')
toteloc = scout.rangefield('F36', 1, 18)

scout.disp("Team Number: " + str(1000*num1 + 100*num2 + 10*num3 + num4))
scout.disp("Match Number: " + str(100*match1 + 10*match2 + match3))

scout.disp("Totes in auto zone: " + str(totes))
scout.disp("Containers in auto zone: " + str(zonecont))
scout.disp("Containers from step: " + str(stepcont))
scout.disp("Stacked set? " + str(stacked))
scout.disp("Moved into auto zone? " + str(inzone))

for s in stacks:
	if s['height'] == 0:
		continue
	if s['capping']:
		scout.disp('Capped a stack of ' + str(s['height']))
	else:
		scout.disp('Built a stack of ' + str(s['height']))
		scout.disp('Capped: ' + str(s['capped']))
	scout.disp('Noodled: ' + str(s['noodled']))

scout.disp('Teleop containers from step: ' + str(telecont))
scout.disp('Coop totes placed: ' + str(coop))
scout.disp('Got coop stack? ' + str(coopstack))

if toteloc == 1:
	scout.disp('Gets all totes from HP')
elif toteloc == 18:
	scout.disp('Gets all totes from landfill')
elif 2 <= toteloc <= 7:
	scout.disp('Gets most totes from HP')
elif 17 >= toteloc >= 12:
	scout.disp('Gets most totes from landfill')
elif toteloc == 0:
	scout.disp("Doesn't pick up gray totes")
else:
	scout.disp("Gets totes equally from landfill/HP")

scout.finish()