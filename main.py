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
		scout.set("team", 1000*num1 + 100*num2 + 10*num3 + num4)

		match1 = scout.rangefield('N-9', 0, 1)
		match2 = scout.rangefield('N-10', 0, 9)
		match3 = scout.rangefield('N-11', 0, 9)
		scout.set("match", 100*match1 + 10*match2 + match3)

		scout.set("foul", scout.countfield('G-11', 'I-11'))
		scout.set("techfoul", scout.countfield('G-12', 'I-12'))

		scout.set("spy", scout.boolfield('AB-5'))
		scout.set("reach", scout.boolfield('AB-6'))

		scout.set("preload", scout.boolfield('AH-4'))
		scout.set("a_high", scout.countfield('AH-5', 'AI-5'))
		scout.set("a_low", scout.countfield('AH-6', 'AI-6'))
		scout.set("a_miss", scout.countfield('AH-7', 'AI-7'))

		scout.set("a_port", scout.boolfield('AD-8'))
		scout.set("a_chev", scout.boolfield('AI-8'))
		scout.set("a_moat", scout.boolfield('AD-9'))
		scout.set("a_ramp", scout.boolfield('AI-9'))
		scout.set("a_draw", scout.boolfield('AD-10'))
		scout.set("a_sall", scout.boolfield('AI-10'))
		scout.set("a_rock", scout.boolfield('AD-11'))
		scout.set("a_roug", scout.boolfield('AI-11'))		
		scout.set("a_lowb", scout.boolfield('AD-12'))	

		scout.set("port", scout.countfield('H-14', 'K-14'))
		scout.set("chev", scout.countfield('P-14', 'S-14'))
		scout.set("moat", scout.countfield('H-15', 'K-15'))
		scout.set("ramp", scout.countfield('P-15', 'S-15'))
		scout.set("draw", scout.countfield('H-16', 'K-16'))
		scout.set("sall", scout.countfield('P-16', 'S-16'))
		scout.set("rock", scout.countfield('H-17', 'K-17'))
		scout.set("roug", scout.countfield('P-17', 'S-17'))	
		scout.set("lowb", scout.countfield('H-18', 'K-18'))

		scout.set("high", scout.countfield('X-14', 'AE-14'))
		scout.set("miss", scout.countfield('X-15', 'AE-15'))
		scout.set("low", scout.countfield('X-17', 'AE-17'))

		scout.set("challenge", scout.boolfield('AJ-13'))
		scout.set("scale", scout.boolfield('AJ-14'))
		scout.set("failscale", scout.boolfield('AJ-15'))
		scout.set("defense", scout.boolfield('AJ-16'))
		scout.set("feeder", scout.boolfield('AJ-17'))
	
		scout.submit()

# This line creates a new PiScout and starts the program
# It takes the main function as an argument and runs it when it finds a new sheet
PiScout(main)
