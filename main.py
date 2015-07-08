from piscout import *

scout = PiScout()
scout.loadsheet('double_new.jpg')

for s in (0,23):
	scout.shiftDown(s) #on the second iteration, it shifts down to see the second match
	num1 = scout.rangefield('O-6', 0, 9)
	num2 = scout.rangefield('O-7', 0, 9)
	num3 = scout.rangefield('O-8', 0, 9)
	num4 = scout.rangefield('O-9', 0, 9)

	match1 = scout.rangefield('O-11', 0, 1)
	match2 = scout.rangefield('O-12', 0, 9)
	match3 = scout.rangefield('O-13', 0, 9)

	totes = scout.rangefield('AG-8', 1, 3)
	zonecont = scout.rangefield('AG-9', 1, 4)
	stepcont = scout.rangefield('AG-10', 1, 4)

	stacked = scout.boolfield('AG-11')
	inzone = scout.boolfield('AG-12')

	#The following wall of code could probably be done iteratively, but I'm too lazy to do that at the moment
	stacks = [None]*6

	stacks[0] = {
		'capping': scout.boolfield('L-15'),
		'height': scout.rangefield('G-16', 1, 6),
		'capped': scout.boolfield('G-17'),
		'noodled': scout.boolfield('L-17')
	}
	stacks[1] = {
		'capping': scout.boolfield('X-15'),
		'height': scout.rangefield('S-16', 1, 6),
		'capped': scout.boolfield('S-17'),
		'noodled': scout.boolfield('X-17')
	}
	stacks[2] = {
		'capping': scout.boolfield('AJ-15'),
		'height': scout.rangefield('AE-16', 1, 6),
		'capped': scout.boolfield('AE-17'),
		'noodled': scout.boolfield('AJ-17')
	}
	stacks[3] = {
		'capping': scout.boolfield('L-19'),
		'height': scout.rangefield('G-20', 1, 6),
		'capped': scout.boolfield('G-21'),
		'noodled': scout.boolfield('L-21')
	}
	stacks[4] = {
		'capping': scout.boolfield('X-19'),
		'height': scout.rangefield('S-20', 1, 6),
		'capped': scout.boolfield('S-21'),
		'noodled': scout.boolfield('X-21')
	}
	stacks[5] = {
		'capping': scout.boolfield('AJ-19'),
		'height': scout.rangefield('AE-20', 1, 6),
		'capped': scout.boolfield('AE-21'),
		'noodled': scout.boolfield('AJ-21')
	}

	telecont = scout.rangefield('K-23', 1, 4)
	coop = scout.rangefield('T-23', 1, 4)
	coopstack = scout.boolfield('AI-23')
	toteloc = scout.rangefield('L-26', 1, 18)

	scout.set("team", 1000*num1 + 100*num2 + 10*num3 + num4)
	scout.set("match", 100*match1 + 10*match2 + match3)
	scout.set("auto totes", totes)
	scout.set("RC in zone", zonecont)
	scout.set("RC from step", stepcont)
	scout.set("stacked set", stacked)
	scout.set("moved to zone", inzone)
	scout.set("stacks", [stack for stack in stacks if stack['height']])
	scout.set("coop", coop)
	scout.set("teleop step RC", telecont)
	scout.set("coop stack?", coopstack)
	scout.set("tote location", toteloc)

	scout.submit()


