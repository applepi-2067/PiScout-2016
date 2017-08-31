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
        scout.set("TechFouls", scout.rangefield('L-17', 1, 4)) #3
        
        scout.set("AutoGears", scout.boolfield('O-11')) #4
        scout.set("AutoBaseline", int(0)) #5
        
        highGoal = scout.boolfield('V-13')
        lowGoal = scout.boolfield('V-14')
        balls1 = scout.rangefield('F-12', 0, 9)
        balls2 = scout.rangefield('F-13', 0, 9)
        scout.set("AutoLowBalls", lowGoal * (balls1*10 + balls2)) #6
        scout.set("AutoHighBalls", highGoal * (balls1*10 + balls2)) #7
        
        scout.set("FloorIntake", scout.boolfield('V-11')) #8
        scout.set("Feeder", 0) #9
        scout.set("Defense", scout.boolfield('V-17')) #10
        scout.set("Defended", scout.boolfield('AB-17')) #11
        scout.set("TeleopGears", scout.rangefield('AB-10', 1, 9)) #12
        scout.set("TeleopGearDrops", scout.rangefield('AB-11', 1, 9)) #13
        balls1 = scout.rangefield('AA-13', 1, 10)
        balls2 = scout.rangefield('AA-14', 11, 20)
        balls3 = scout.rangefield('AA-15', 21, 30)
        scout.set("TeleopLowBalls", lowGoal * 5 * (balls1 + balls2 + balls3)) #14
        scout.set("TeleopHighBalls", highGoal * 5 * (balls1 + balls2 + balls3)) #15
        
        scout.set("Hang", scout.boolfield('G-16')) #16
        scout.set("FailedHang", scout.boolfield('G-17')) #17
        
        scout.set("Replay", scout.boolfield('AK-5'))
        sideAttempt = scout.boolfield('F-11') and not scout.boolfield('O-11')
        centerAttempt = scout.boolfield('J-11') and not scout.boolfield('O-11')
        sideSuccess = scout.boolfield('F-11') and scout.boolfield('O-11')
        centerSuccess = scout.boolfield('J-11') and scout.boolfield('O-11')
        scout.set("AutoSideAttempt", int(sideAttempt)) #18
        scout.set("AutoCenterAttempt", int(centerAttempt)) #19
        scout.set("AutoSideSuccess", int(sideSuccess)) #20
        scout.set("AutoCenterSuccess", int(centerSuccess)) #21

        scout.submit()

# This line creates a new PiScout and starts the program
# It takes the main function as an argument and runs it when it finds a new sheet
PiScout(main)
