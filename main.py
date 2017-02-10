from piscout import *

# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
def main(scout):
    for s in (0,16,32):
        scout.shiftDown(s)

        # The numberings of the fields are important; you reference them by number in server.py
        num1 = scout.rangefield('J-5', 0, 9)
        num2 = scout.rangefield('J-6', 0, 9)
        num3 = scout.rangefield('J-7', 0, 9)
        num4 = scout.rangefield('J-8', 0, 9)
        scout.set("Team", 1000*num1 + 100*num2 + 10*num3 + num4) #0

        match1 = scout.rangefield('AB-5', 0, 1)
        match2 = scout.rangefield('AB-6', 0, 9)
        match3 = scout.rangefield('AB-7', 0, 9)
        scout.set("Match", 100*match1 + 10*match2 + match3) #1

        scout.set("Fouls", scout.rangefield('L-16', 1, 4)) #2
        scout.set("Tech fouls", scout.rangefield('L-17', 1, 4)) #3
        
        scout.set("Auto: Gears", scout.rangefield('F-11', 1, 3)) #4
        scout.set("Auto: Baseline", scout.boolfield('O-11')) #5
        
        highGoal = scout.boolfield('V-13')
        lowGoal = scout.boolfield('V-14')
        balls1 = scout.rangefield('F-12', 0, 9)
        balls2 = scout.rangefield('F-13', 0, 9)
        scout.set("Auto: Low Balls", lowGoal * (balls1*10 + balls2)) #6
        scout.set("Auto: High Balls", highGoal * (balls1*10 + balls2)) #7
        
        scout.set("Gears Floor Intake", scout.boolfield('V-11')) #8
        scout.set("Feeder Bot", scout.boolfield('V-16')) #9
        scout.set("Defence Bot", scout.boolfield('V-17')) #10
        scout.set("Defended", scout.boolfield('AB-17')) #11
        scout.set("Teleop: Gears", scout.rangefield('AB-10', 1, 9)) #12
        scout.set("Teleop: Gear Drops", scout.rangefield('AB-11', 1, 9)) #13
        balls1 = scout.rangefield('AA-13', 1, 10)
        balls2 = scout.rangefield('AA-14', 11, 20)
        balls3 = scout.rangefield('AA-15', 21, 30)
        scout.set("Teleop: Low Balls", lowGoal * 10 * (balls1 + balls2 + balls3)) #14
        scout.set("Teleop: High Balls", highGoal * 10 * (balls1 + balls2 + balls3)) #15
        
        scout.set("Hang", scout.boolfield('G-16')) #16
        scout.set("Failed Hang", scout.boolfield('G-17')) #17

        scout.submit()

# This line creates a new PiScout and starts the program
# It takes the main function as an argument and runs it when it finds a new sheet
PiScout(main)
