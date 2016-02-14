from piscout import *

# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
def main(scout):
	for s in (0,16,32):
		scout.shiftDown(s)

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

		scout.set("Portcullis", scout.countfield('H-14', 'K-14')) #19
		scout.set("Cheval de frise", scout.countfield('P-14', 'S-14')) #20
		scout.set("Moat", scout.countfield('H-15', 'K-15')) #21
		scout.set("Ramparts", scout.countfield('P-15', 'S-15')) #22
		scout.set("Drawbridge", scout.countfield('H-16', 'K-16')) #23
		scout.set("Sally port", scout.countfield('P-16', 'S-16')) #24 
		scout.set("Rock wall", scout.countfield('H-17', 'K-17')) #25
		scout.set("Rough terrain", scout.countfield('P-17', 'S-17')) #26	
		scout.set("Low bar", scout.countfield('H-18', 'K-18')) #27

		scout.set("High goal", scout.countfield('X-14', 'AE-14')) #28
		scout.set("High miss", scout.countfield('X-15', 'AE-15')) #29
		scout.set("Low goal", scout.countfield('X-17', 'AE-17')) #30

		scout.set("Challenging", scout.boolfield('AJ-13')) #31
		scout.set("Scale", scout.boolfield('AJ-14')) #32
		scout.set("Failed scale", scout.boolfield('AJ-15')) #33
		scout.set("Defense", scout.boolfield('AJ-16')) #34
		scout.set("Feeder", scout.boolfield('AJ-17')) #35
	
		scout.submit()

# This line creates a new PiScout and starts the program
# It takes the main function as an argument and runs it when it finds a new sheet
PiScout(main)
