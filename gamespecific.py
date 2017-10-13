import numpy as np

SCOUT_FIELDS = {"Team":0, "Match":0, "Fouls":0, "TechFouls":0, "AutoGears":0, "AutoBaseline":0,
        "AutoLowBalls":0, "AutoHighBalls":0, "FloorIntake":0, "Feeder":0, "Defense":0, "Defended":0,
        "TeleopGears":0, "TeleopGearDrops":0, "TeleopLowBalls":0, "TeleopHighBalls":0, "Hang":0,
        "FailedHang":0, "Replay":0, "AutoSideAttempt":0, "AutoSideSuccess":0, "AutoCenterAttempt":0,
        "AutoCenterSuccess":0, "Flag":0}


AVERAGE_FIELDS = {"team":0, "apr":0, "autogear":0, "teleopgear":0, "geardrop":0, "autoballs":0, "teleopballs":0, 
        "end":0, "defense":0}

CHART_FIELDS = {"match":0, "autoshoot":0, "autogears":0, "gears":0, "geardrop":0, "shoot":0}
        
     
# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
def processSheet(scout):
    for s in (0,16,32):
        scout.shiftDown(s)

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

def generateTeamText(e):
    text = {'auto':"", 'teleop1':"", 'teleop2':"", 'other':""}
    text['auto'] += 'baseline, ' if e['AutoBaseline'] else ''
    text['auto'] += 'side try, ' if e['AutoSideAttempt'] else ''
    text['auto'] += 'center try, ' if e['AutoCenterAttempt'] else ''
    text['auto'] += 'side peg, ' if e['AutoSideSuccess'] else ''
    text['auto'] += 'center peg, ' if e['AutoCenterSuccess'] else ''
    text['auto'] += str(e['AutoLowBalls']) + 'x low goal, ' if e['AutoLowBalls'] else ''
    text['auto'] += str(e['AutoHighBalls']) + 'x high goal, ' if e['AutoHighBalls'] else ''
    
    text['teleop1'] += str(e['TeleopGears']) + 'x gears, ' if e['TeleopGears'] else ''
    text['teleop1'] += str(e['TeleopGearDrops']) + 'x gears dropped, ' if e['TeleopGearDrops'] else ''
    
    text['teleop2'] += str(e['TeleopLowBalls']) + 'x low goal, ' if e['TeleopLowBalls'] else ''
    text['teleop2'] += str(e['TeleopHighBalls']) + 'x high goal, ' if e['TeleopHighBalls'] else ''
    
    text['other'] = 'hang, ' if e['Hang'] else 'failed hang, ' if e['FailedHang'] else ''
    text['other'] += str(e['Fouls']) + 'x foul, ' if e['Fouls'] else ''
    text['other'] += str(e['TechFouls']) + 'x tech foul, ' if e['TechFouls'] else ''
    text['other'] += 'defense, ' if e['Defense'] else ''
    text['other'] += 'feeder, ' if e['Feeder'] else ''
    text['other'] += 'defended, ' if e['Defended'] else ''
    
    return text
    
def generateChartData(e):
    dp = dict(CHART_FIELDS)
    dp["match"]= e['match']
    
    dp['autoshoot'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
    dp['autogears'] += e['AutoGears']
    
    dp['gears'] += e['TeleopGears']
    dp['geardrop'] += e['TeleopGearDrops']
    
    dp['shoot'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
    
    return dp
    
def predictScore(teams, level='quals'):
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        ballScore = []
        endGame = []
        autoGears = []
        teleopGears = []
        for n in teams:
            average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
                entry = average[0]
            else:
                entry = [0]*8
            autoGears.append(entry[2])
            teleopGears.append(entry[3])
            ballScore.append((entry[5]+entry[6]))
            endGame.append((entry[7]))
        retVal = {'score': 0, 'gearRP': 0, 'fuelRP': 0}
        score = sum(ballScore[0:3]) + sum(endGame[0:3])
        if sum(autoGears[0:3]) >= 1:
            score += 60
        else:
            score += 40
        if sum(autoGears[0:3]) >= 3:
            score += 60
        elif sum(autoGears[0:3] + teleopGears[0:3]) >= 2:
            score += 40
        if sum(autoGears[0:3] + teleopGears[0:3]) >= 6:
            score += 40
        if sum(autoGears[0:3] + teleopGears[0:3]) >= 12:
            score += 40
            if level == 'playoffs':
                score += 100
            else:
                retVal['gearRP'] == 1
        if sum(ballScore[0:3]) >= 40:
            if level == 'playoffs':
                score += 20
            else:
                retVal['fuelRP'] == 1
        retVal['score'] = score
        return retVal
        
def autoFlag(entry):
    if (entry['AutoHighBalls'] or entry['TeleopHighBalls']) and (entry['AutoLowBalls'] or entry['AutoHighBalls']): 
        return 1
    if entry['Hang'] and entry['FailedHang']:
        return 1
    return 0
    
def calcTotals(entries):
    sums = dict(AVERAGE_FIELDS)
    noDefense = dict(AVERAGE_FIELDS)
    lastThree = dict(AVERAGE_FIELDS)
    noDCount = 0
    lastThreeCount = 0
    for key in sums:
        sums[key] = []
    for i, e in enumerate(entries):
        sums['autogear'].append(e['AutoGears'])
        sums['teleopgear'].append(e['TeleopGears'])
        sums['autoballs'].append(e['AutoLowBalls']/3 + e['AutoHighBalls'])
        sums['teleopballs'].append(e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3)
        sums['geardrop'].append(e['TeleopGearDrops'])
        sums['end'].append(e['Hang']*50)
        sums['defense'].append(e['Defense'])
        if not e['Defense']:
            noDefense['autogear'] += e['AutoGears']
            noDefense['teleopgear'] += e['TeleopGears']
            noDefense['autoballs'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
            noDefense['teleopballs'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
            noDefense['geardrop'] += e['TeleopGearDrops']
            noDefense['end'] += e['Hang']*50
            noDefense['defense'] += e['Defense']
            noDCount += 1
        if i < 3:
            lastThree['autogear'] += e['AutoGears']
            lastThree['teleopgear'] += e['TeleopGears']
            lastThree['autoballs'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
            lastThree['teleopballs'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
            lastThree['geardrop'] += e['TeleopGearDrops']
            lastThree['end'] += e['Hang']*50
            lastThree['defense'] += e['Defense']
            lastThreeCount += 1
    
    if(lastThreeCount):
        for key,val in lastThree.items():
            lastThree[key] = round(val/lastThreeCount, 2)
    if(noDCount):
        for key,val in noDefense.items():
            noDefense[key] = round(val/noDCount, 2)
    average = dict(AVERAGE_FIELDS)
    median = dict(AVERAGE_FIELDS)
    maxes = dict(AVERAGE_FIELDS)
    for key in sums:
        if key != 'team' and key!= 'apr':
            average[key] = round(np.mean(sums[key]), 2)
            median[key] = round(np.median(sums[key]), 2)
            maxes[key] = round(np.max(sums[key]), 2)
    retVal = {'averages':average, 'median':median, 'maxes':maxes, 'noDefense':noDefense, 'lastThree':lastThree}
    for key in retVal:
        apr = retVal[key]['autoballs'] + retVal[key]['teleopballs'] + retVal[key]['end']
        if retVal[key]['autogear']:
            apr += 20 * min(retVal[key]['autogear'], 1)
        if retVal[key]['autogear'] > 1:
            apr += (retVal[key]['autogear'] - 1) * 10   
            
        apr += max(min(retVal[key]['teleopgear'], 2 - retVal[key]['autogear']) * 20, 0)
        if retVal[key]['autogear'] + retVal[key]['teleopgear'] > 2:
            apr += min(retVal[key]['teleopgear'] + retVal[key]['autogear'] - 2, 4) * 10
        if retVal[key]['autogear'] + retVal[key]['teleopgear'] > 6:
            apr += min(retVal[key]['teleopgear'] + retVal[key]['autogear'] - 6, 6) * 7
        apr = int(apr)
        retVal[key]['apr'] = apr
    
    return retVal
            
        