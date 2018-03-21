import numpy as np
import sqlite3 as sql
from enum import IntEnum
import proprietary as prop

#Defines the fields stored in the "Scout" table of the database. This database stores the record for each match scan
SCOUT_FIELDS = {"Team":0, "Match":0, "Start":0, "End":0, "ALine":0, "ASwitch":0,
        "AScale":0, "Defense":0, "TXch":0, "TOwnSwitch":0, "TScale":0, 
        "TOppSwitch":0, "SelfClimbAttempt":0, "SelfClimb":0, "SupportClimbAttempt":0,
        "SupportClimb":0, "Replay":0, "Flag":0}

#Defines the fields that are stored in the "averages" and similar tables of the database. These are the fields displayed on the home page of the website. Hidden average fields are only displayed when logged in or on local.
AVERAGE_FIELDS = {"team":0, "apr":0, "ASwitch":0, "AScale":0, "TXch":0, "TOwnSwitch":0, "TScale":0, "TOppSwitch":0, "Climb":0, "Defense":0}
HIDDEN_AVERAGE_FIELDS = {"CubeScore":0, "FirstP":0, "SecondP":0}

#Define the fields collected from Pit Scouting to display on the team page
PIT_SCOUT_FIELDS = {"Team":0, "Weight":0, "PitOrganization":0, "WiringQuality":0, "BumperQuality":0, "Batteries":0, "SillyWheels":0, "Pro775s":0, "Swerve":0, "FloorPickup":0, "Line":0, "CenterSwitch":0, "SideSwitch":0, "SideScale":0, "CPP":0, "Java":0, "LabVIEW":0}

#Defines the fields displayed on the charts on the team and compare pages
CHART_FIELDS = {"match":0, "ASwitch":0, "AScale":0, "TXch":0, "TOwnSwitch":0, "TScale":0, "TOppSwitch":0, "TCubes":0, "Climb":0}

class SheetType(IntEnum):
  MATCH = 0
  PIT = 1
        
     
# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
# The sheet is developed in Google Sheets and the coordinates are defined in terms on the row and column numbers from the sheet.
def processSheet(scout):
    for s in (0,16,32):
        #Sets the shift value (used when turning cell coordinates into pixel coordinates)
        scout.shiftDown(s)
        
        type = scout.rangefield('E-5', 0, 1)
        scout.setType(type)
        if(type == SheetType.MATCH):
          #Match scouting sheet
          num1 = scout.rangefield('AB-5', 0, 9)
          num2 = scout.rangefield('AB-6', 0, 9)
          num3 = scout.rangefield('AB-7', 0, 9)
          num4 = scout.rangefield('AB-8', 0, 9)
          scout.setMatchData("Team", 1000*num1 + 100*num2 + 10*num3 + num4)

          match1 = scout.rangefield('J-6', 0, 1)
          match2 = scout.rangefield('J-7', 0, 9)
          match3 = scout.rangefield('J-8', 0, 9)
          scout.setMatchData("Match", 100*match1 + 10*match2 + match3)
          
          scout.setMatchData("Replay", scout.boolfield('S-6'))
          
          scout.setMatchData("Start", scout.rangefield('J-12', 0, 2))
          scout.setMatchData("End", scout.rangefield('J-14', 0, 2))
          
          scout.setMatchData("ALine", scout.boolfield('J-16'))
          
          scout.setMatchData("ASwitch", scout.countfield('J-17', 'L-17', 0))
          scout.setMatchData("AScale", scout.countfield('J-18', 'L-18', 0))
          
          scout.setMatchData("Defense", scout.boolfield('V-17'))
          
          scout.setMatchData("TXch", scout.countfield('V-11', 'AK-11', 0))
          scout.setMatchData("TOwnSwitch", scout.countfield('V-12', 'AK-12', 0))
          scout.setMatchData("TScale", scout.countfield('V-13', 'AK-13', 0))
          scout.setMatchData("TOppSwitch", scout.countfield('V-14', 'AK-14', 0))
          
          scout.setMatchData("SelfClimbAttempt", scout.boolfield('AD-17'))
          scout.setMatchData("SelfClimb", scout.boolfield('AG-17'))
          scout.setMatchData("SupportClimbAttempt", scout.countfield('AD-18', 'AE-18', 1))
          scout.setMatchData("SupportClimb", scout.countfield('AG-18', 'AH-18', 1))
          
          scout.submit()
        elif(type == SheetType.PIT):
          #Pit scouting sheet
          num1 = scout.rangefield('M-5', 0, 9)
          num2 = scout.rangefield('M-6', 0, 9)
          num3 = scout.rangefield('M-7', 0, 9)
          num4 = scout.rangefield('M-8', 0, 9)
          scout.setPitData("Team", 1000*num1 + 100*num2 + 10*num3 + num4)
          
          weight1 = scout.rangefield('AB-5', 0, 1)
          weight2 = scout.rangefield('AB-6', 0, 9)
          weight3 = scout.rangefield('AB-7', 0, 9)
          scout.setPitData("Weight", 100*weight1 + 10*weight2 + weight3)
          
          scout.setPitData("CPP", scout.boolfield('J-12'))
          scout.setPitData("Java", scout.boolfield('K-12'))
          scout.setPitData("LabVIEW", scout.boolfield('L-12'))
          
          scout.setPitData("Line", scout.boolfield('K-14'))
          scout.setPitData("CenterSwitch", scout.boolfield('K-15'))
          scout.setPitData("SideSwitch", scout.boolfield('K-16'))
          scout.setPitData("SideScale", scout.boolfield('K-17'))
          
          scout.setPitData("SillyWheels", scout.boolfield('V-12'))
          scout.setPitData("Pro775s", scout.boolfield('V-13'))
          scout.setPitData("Swerve", scout.boolfield('V-14'))
          scout.setPitData("FloorPickup", scout.boolfield('V-16')) 
          
          scout.setPitData("PitOrganization", scout.rangefield('AF-12', 1, 3))
          scout.setPitData("WiringQuality", scout.rangefield('AF-13', 1, 3))
          scout.setPitData("BumperQuality", scout.rangefield('AF-14', 1, 3))
          scout.setPitData("Batteries", scout.rangefield('AC-16', 1, 7))
          
          scout.submit()   
        
#Takes an entry from the Scout database table and generates text for display on the team page. This page has 4 columns, currently used for auto, 2 teleop, and other (like fouls and end game)
def generateTeamText(e):
    text = {'auto':"", 'teleop1':"", 'teleop2':"", 'other':""}
    text['auto'] += 'Start: '
    text['auto'] += 'L' if e['Start'] == 0 else 'C' if e['Start'] == 1 else 'R'
    text['auto'] += ', End: '
    text['auto'] += 'L' if e['End'] == 0 else 'C' if e['End'] == 1 else 'R'
    text['auto'] += ', '
    text['auto'] += 'Line, ' if e['ALine'] else ''
    text['auto'] += 'Switch: ' + str(e['ASwitch']) + ', ' if e['ASwitch'] else ''
    text['auto'] += 'Scale: ' + str(e['AScale']) + ', ' if e['AScale'] else ''
    text['auto'] = text['auto'][:-2]
    
    text['teleop1'] += 'Exchange: ' + str(e['TXch']) + ', ' if e['TXch'] else ''
    text['teleop1'] += 'Own Switch: ' + str(e['TOwnSwitch']) + ', ' if e['TOwnSwitch'] else ''
    text['teleop1'] = text['teleop1'][:-2]
    
    text['teleop2'] += 'Scale: ' + str(e['TScale']) + ', ' if e['TScale'] else ''
    text['teleop2'] += 'Opp Switch: ' + str(e['TOppSwitch']) + ', ' if e['TOppSwitch'] else ''
    text['teleop2'] = text['teleop2'][:-2]
    
    text['other'] = 'Climb, ' if e['SelfClimb'] else 'Failed Climb, ' if e['SelfClimbAttempt'] else ''
    text['other'] += 'Supported: ' + str(e['SupportClimb']) + ', ' if e['SupportClimb'] else ''
    text['other'] += 'Failed Support: ' + str(e['SupportClimbAttempt']) + ', ' if e['SupportClimbAttempt'] else ''
    text['other'] += 'Defense, ' if e['Defense'] else ''
    text['other'] = text['other'][:-2]
    
    return text
    
#Takes an entry from the Scout database table and generates chart data. The fields in the returned dict must match the CHART_FIELDS definition at the top of this file
def generateChartData(e):
    dp = dict(CHART_FIELDS)
    dp["match"]= e['match']
    
    dp['ASwitch'] += e['ASwitch']
    dp['AScale'] += e['AScale']
    
    dp['TXch'] += e['TXch']
    dp['TOwnSwitch'] += e['TOwnSwitch']
    dp['TScale'] += e['TScale']
    dp['TOppSwitch'] += e['TOppSwitch']
    dp['TCubes'] += e['TOwnSwitch'] + e['TScale'] + e['TOppSwitch'] + e['TXch']
    dp['Climb'] += 30*(e['SelfClimb'] + e['SupportClimb'])
    
    return dp
    
#Takes a set of team numbers and a string indicating quals or playoffs and returns a prediction for the alliances score and whether or not they will achieve any additional ranking points
def predictScore(datapath, teams, level='quals'):
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        
        autoRP = 0
        climbRP = 0
        climbTotal = 0
        
        aprTotal = 0

        for n in teams:
            average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
              entry = average[0]
            else:
              entry = dict(AVERAGE_FIELDS)
              entry.update(HIDDEN_AVERAGE_FIELDS)
            
            aprTotal += entry['CubeScore']
            
            if(entry['Climb'] > 30):
              climbRP = 1
            else:
              climbTotal += entry['Climb']
              
            if(entry['ASwitch'] > 0.5):
              autoRP = 1
              
        if (climbTotal > 30):
          climbRP = 1
              
        retVal = {'score': 0, 'RP1': 0, 'RP2': 0}
       
        retVal['score'] = aprTotal
        retVal['RP1'] = autoRP
        retVal['RP2'] = climbRP
        
        return retVal

#Takes an entry from the Scout table and returns whether or not the entry should be flagged based on contradictory data.
def autoFlag(entry):
    if entry['SelfClimb'] and entry['SelfClimbAttempt']:
        return 1
    return 0

#Takes a list of Scout table entries and returns a nested dictionary of the statistical calculations (average, maxes, median, etc.) of each field in the AVERAGE_FIELDS definition
def calcTotals(entries):
    sums = dict(AVERAGE_FIELDS)
    sums.update(HIDDEN_AVERAGE_FIELDS)
    noDefense = dict(AVERAGE_FIELDS)
    noDefense.update(HIDDEN_AVERAGE_FIELDS)
    lastThree = dict(AVERAGE_FIELDS)
    lastThree.update(HIDDEN_AVERAGE_FIELDS)
    noDCount = 0
    lastThreeCount = 0
    for key in sums:
        sums[key] = []
    #For each entry, add components to the running total if appropriate
    for i, e in enumerate(entries):
        sums['ASwitch'].append(e['ASwitch'])
        sums['AScale'].append(e['AScale'])
        sums['TXch'].append(e['TXch'])
        sums['TOwnSwitch'].append(e['TOwnSwitch'])
        sums['TScale'].append(e['TScale'])
        sums['TOppSwitch'].append(e['TOppSwitch'])
        sums['Climb'].append(e['SelfClimb']*30 + e['SupportClimb']*30)
        sums['Defense'].append(e['Defense'])
        sums['CubeScore'].append(0)
        sums['FirstP'].append(0)
        sums['SecondP'].append(0)
        if not e['Defense']:
          noDefense['ASwitch']+=e['ASwitch']
          noDefense['AScale']+=e['AScale']
          noDefense['TXch']+=e['TXch']
          noDefense['TOwnSwitch']+=e['TOwnSwitch']
          noDefense['TScale']+=e['TScale']
          noDefense['TOppSwitch']+=e['TOppSwitch']
          noDefense['Climb']+=e['SelfClimb']*30 + e['SupportClimb']*30
          noDefense['Defense']+=e['Defense']
          noDCount += 1
        if i < 3:
          lastThree['ASwitch']+=e['ASwitch']
          lastThree['AScale']+=e['AScale']
          lastThree['TXch']+=e['TXch']
          lastThree['TOwnSwitch']+=e['TOwnSwitch']
          lastThree['TScale']+=e['TScale']
          lastThree['TOppSwitch']+=e['TOppSwitch']
          lastThree['Climb']+=e['SelfClimb']*30 + e['SupportClimb']*30
          lastThree['Defense']+=e['Defense']
          lastThreeCount += 1
    
    #If there is data, average out the last 3 or less matches
    if(lastThreeCount):
        for key,val in lastThree.items():
            lastThree[key] = round(val/lastThreeCount, 2)
          
    #If there were matches where the team didn't play D, average those out
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
    
    #Calculate APRs. This is an approximate average points contribution to the match
    for key in retVal:
        CubeScore = round(retVal[key]['AScale']*prop.AUTO_SCALE + retVal[key]['ASwitch']*prop.AUTO_SWITCH + retVal[key]['TXch']*prop.EXCHANGE + retVal[key]['TOwnSwitch']*prop.OWN_SWITCH + retVal[key]['TScale']*prop.SCALE + retVal[key]['TOppSwitch']*prop.OPP_SWITCH, 2)
        FirstPick = round(retVal[key]['ASwitch']*prop.FIRST_AUTO_SWITCH+retVal[key]['AScale']*prop.FIRST_AUTO_SCALE + retVal[key]['TXch']*prop.FIRST_EXCHANGE + retVal[key]['TOwnSwitch']*prop.FIRST_OWN_SWITCH + retVal[key]['TScale']*prop.FIRST_SCALE + retVal[key]['TOppSwitch']*prop.FIRST_OPP_SWITCH + retVal[key]['Climb']*prop.FIRST_CLIMB, 2)
        SecondPick = round(retVal[key]['ASwitch']*prop.SECOND_AUTO_SWITCH+retVal[key]['AScale']*prop.SECOND_AUTO_SCALE + retVal[key]['TXch']*prop.SECOND_EXCHANGE + retVal[key]['TOwnSwitch']*prop.SECOND_OWN_SWITCH + retVal[key]['TScale']*prop.SECOND_SCALE + retVal[key]['TOppSwitch']*prop.SECOND_OPP_SWITCH + retVal[key]['Climb']*prop.SECOND_CLIMB, 2)
        apr = round(retVal[key]['TXch'] + retVal[key]['TOwnSwitch'] + retVal[key]['TScale'] + retVal[key]['TOppSwitch'], 2)
        
        retVal[key]['CubeScore'] = CubeScore
        retVal[key]['FirstP'] = FirstPick
        retVal[key]['SecondP'] = SecondPick
        retVal[key]['apr'] = apr
    
    return retVal
            
        