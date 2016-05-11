from piscout import *

# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
def main(scout):
	for s in (0,16,32):
		scout.shiftDown(s)

		# The numberings of the fields are important; you reference them by number in server.py
		num1 = scout.rangefield('N-4', 0, 9)
		num2 = scout.rangefield('N-5', 0, 9)
		num3 = scout.rangefield('N-6', 0, 9)
		num4 = scout.rangefield('N-7', 0, 9)
		scout.set("Team", 1000*num1 + 100*num2 + 10*num3 + num4) #0

		match1 = scout.rangefield('N-9', 0, 1)
		match2 = scout.rangefield('N-10', 0, 9)
		match3 = scout.rangefield('N-11', 0, 9)
		scout.set("Match", 100*match1 + 10*match2 + match3) #1

		scout.set("Fouls", scout.countfield('G-11', 'I-11')) #2
		scout.set("Tech fouls", scout.countfield('G-12', 'I-12')) #3

		scout.set("Spy box", scout.boolfield('AB-5')) #4
		scout.set("Reach", scout.boolfield('AB-6')) #5

		scout.set("Preloaded", scout.boolfield('AH-4')) #6
		scout.set("Auto: High goal", scout.countfield('AH-5', 'AI-5')) #7
		scout.set("Auto: Low goal", scout.countfield('AH-6', 'AI-6')) #8
		scout.set("Auto: Miss", scout.countfield('AH-7', 'AI-7')) #9

		scout.set("Auto: Portcullis", scout.boolfield('AD-8')) #10
		scout.set("Auto: Cheval de frise", scout.boolfield('AI-8')) #11
		scout.set("Auto: Moat", scout.boolfield('AD-9')) #12
		scout.set("Auto: Ramparts", scout.boolfield('AI-9')) #13
		scout.set("Auto: Drawbridge", scout.boolfield('AD-10')) #14
		scout.set("Auto: Sally port", scout.boolfield('AI-10')) #15
		scout.set("Auto: Rock wall", scout.boolfield('AD-11')) #16
		scout.set("Auto: Rough terrain", scout.boolfield('AI-11')) #17
		scout.set("Auto: Low bar", scout.boolfield('AD-12')) #18

		a = scout.countfield('N-14', 'R-14')
		scout.set("Portcullis", a * scout.boolfield('H-14')) #19
		scout.set("Cheval de frise", a * scout.boolfield('L-14')) #20

		b = scout.countfield('N-15', 'R-15')
		scout.set("Moat", b * scout.boolfield('H-15')) #21
		scout.set("Ramparts", b * scout.boolfield('L-15')) #22

		c = scout.countfield('N-16', 'R-16')
		scout.set("Drawbridge", c * scout.boolfield('H-16')) #23
		scout.set("Sally port", c * scout.boolfield('L-16')) #24

		d = scout.countfield('N-17', 'R-17')
		scout.set("Rock wall", d * scout.boolfield('H-17')) #25
		scout.set("Rough terrain", d * scout.boolfield('L-17')) #26

		scout.set("Low bar", scout.countfield('N-18', 'R-18')) #27

		scout.set("High goal", scout.countfield('W-14', 'AE-14')) #28
		scout.set("High miss", scout.countfield('W-15', 'AE-15')) #29
		scout.set("Low goal", scout.countfield('W-17', 'AE-17')) #30

		scout.set("Challenging", scout.boolfield('AJ-13')) #31
		scout.set("Scale", scout.boolfield('AJ-14')) #32
		scout.set("Failed scale", scout.boolfield('AJ-15')) #33
		scout.set("Defense", scout.boolfield('AJ-16')) #34
		scout.set("Feeder", scout.boolfield('AJ-17')) #35

		scout.submit()

# This line creates a new PiScout and starts the program
# It takes the main function as an argument and runs it when it finds a new sheet
PiScout(main)
