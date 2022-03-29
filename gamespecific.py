from enum import IntEnum

import server as server
import proprietary as prop

# Defines the fields stored in the "Scout" table of the database. This database stores the record for each match scan
SCOUT_FIELDS = {"Team": 0, "Match": 0, "Taxi": 0, "Hangar": 0, "FailedClimb": 0, "Disabled": 0, "Defense": 0,
                "Defended": 0, "FenderShot": 0, "LaunchPadShot": 0, "HPScore": 0, "AutoHigh": 0, "AutoLow": 0,
                "TeleHigh": 0, "TeleLow": 0, "Replay": 0, "Flag": 0}

# Defines the fields that are stored in the "averages" and similar tables of the database.
# These are the fields displayed on the home page of the website.
# Hidden average fields are only displayed when logged in or on local.
DISPLAY_FIELDS = {"Team": 0, "Cargo": 0, "CargoPoints": 0, "Hangar": 0, "Defense": 0}
HIDDEN_DISPLAY_FIELDS = {"FirstP": 0, "SecondP": 0}

# Define the fields collected from Pit Scouting to display on the team page
PIT_SCOUT_FIELDS = {"TeamNumber": 0, "Weight": 0, "PitOrganization": 0, "WiringQuality": 0, "BumperQuality": 0,
                    "Batteries": 0, "SillyWheels": 0, "Swerve": 0,
                    "BallCapacity": 0, "VisionTarget": 0, "FloorPickup": 0, "ShortBot": 0, "ClimbLevel": 0,
                    "ClimbNarrow": 0}

# Define which pit scout fields to display on alliance page
PIT_DISPLAY_FIELDS = {"Weight": 0, "SillyWheels": 0, "Swerve": 0, "ClimbLevel": 0}

# Defines the fields displayed on the charts on the team and compare pages
CHART_FIELDS = {"match": 0, "AutoHigh": 0, "AutoLow": 0, "CargoTotal": 0, "CargoPoints": 0, "TeleHigh": 0, "TeleLow": 0, "Hangar": 0 }


class SheetType(IntEnum):
    MATCH = 0
    PIT = 1


def getDisplayFieldCreate():
    retVal = "Cargo AS (AutoHigh+AutoLow+TeleHigh+TeleLow) STORED, "
    retVal += "CargoPoints AS (4*AutoHigh+2*AutoLow+2*TeleHigh+TeleLow) STORED, "
    retVal += "FirstP AS (CargoPoints*" + str(prop.FIRST_CARGO_POINTS) + "*(1+Defended)+Hangar*" + str(prop.FIRST_HANGAR) + ") STORED, "
    retVal += "SecondP AS (CargoPoints*" + str(prop.SECOND_CARGO_POINTS) + "*(1+Defended)+Hangar*" + str(prop.SECOND_HANGAR) + \
              "+Defense*"+str(prop.SECOND_DEFENSE) + "+Disabled*" + str(prop.SECOND_DISABLED) + ") STORED, "
    return retVal


# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
# The sheet is developed in Google Sheets and the coordinates are
# defined in terms on the row and column numbers from the sheet.
def processSheet(scout):
    for s in (0, 16, 32):
        # Sets the shift value (used when turning cell coordinates into pixel coordinates)
        scout.shiftDown(s)

        type = scout.rangefield('E-5', 0, 1)
        scout.setType(type)
        if (type == SheetType.MATCH):
            # Match scouting sheet
            num1 = scout.rangefield('AB-5', 0, 9)
            num2 = scout.rangefield('AB-6', 0, 9)
            num3 = scout.rangefield('AB-7', 0, 9)
            num4 = scout.rangefield('AB-8', 0, 9)
            scout.setMatchData("Team", 1000 * num1 + 100 * num2 + 10 * num3 + num4)

            match1 = scout.rangefield('J-6', 0, 1)
            match2 = scout.rangefield('J-7', 0, 9)
            match3 = scout.rangefield('J-8', 0, 9)
            scout.setMatchData("Match", 100 * match1 + 10 * match2 + match3)

            scout.setMatchData("Replay", scout.boolfield('S-6'))

            scout.setMatchData("Taxi", scout.boolfield('G-11'))
            scout.setMatchData("HPScore", scout.boolfield('Q-11'))

            scout.setMatchData("FenderShot", scout.boolfield('AA-11'))
            scout.setMatchData("LaunchPadShot", scout.boolfield('AI-11'))

            scout.setMatchData("AutoLow", scout.rangefield('G-12', 0, 9))
            scout.setMatchData("AutoHigh", scout.rangefield('G-13', 0, 9))

            low1 = scout.rangefield('AA-13', 0, 9)
            low2 = scout.rangefield('AA-14', 0, 9)
            scout.setMatchData("TeleLow", 10 * low1 + low2)

            high1 = scout.rangefield('AA-16', 0, 9)
            high2 = scout.rangefield('AA-17', 0, 9)
            scout.setMatchData("TeleHigh", 10 * high1 + high2)

            scout.setMatchData("FailedClimb", scout.boolfield('N-16'))
            scout.setMatchData("Hangar", 4*scout.boolfield('T-15') + 6*scout.boolfield('T-16') +
                               10*scout.boolfield('T-17') + 15*scout.boolfield('T-18'))

            scout.setMatchData("Defense", scout.boolfield('G-15'))
            scout.setMatchData("Defended", scout.boolfield('G-16'))
            scout.setMatchData("Disabled", scout.boolfield('G-17'))

            scout.submit()
        elif (type == SheetType.PIT):
            # Pit scouting sheet
            num1 = scout.rangefield('M-5', 0, 9)
            num2 = scout.rangefield('M-6', 0, 9)
            num3 = scout.rangefield('M-7', 0, 9)
            num4 = scout.rangefield('M-8', 0, 9)
            scout.setPitData("Team", 1000 * num1 + 100 * num2 + 10 * num3 + num4)

            weight1 = scout.rangefield('AB-5', 0, 1)
            weight2 = scout.rangefield('AB-6', 0, 9)
            weight3 = scout.rangefield('AB-7', 0, 9)
            scout.setPitData("Weight", 100 * weight1 + 10 * weight2 + weight3)

            scout.setPitData("BallCapacity", scout.rangefield('M-10', 1, 2))
            scout.setPitData("VisionTarget", scout.boolfield('Q-12'))
            scout.setPitData("FloorPickup", scout.boolfield('Q-13'))
            scout.setPitData("ShortBot", scout.boolfield('Q-14'))
            scout.setPitData("ClimbLevel", scout.rangefield('Q-15', 1, 4))
            scout.setPitData('NarrowClimb', scout.boolfield('Q-16'))

            scout.setPitData("SillyWheels", scout.boolfield('X-12'))
            scout.setPitData("Swerve", scout.boolfield('X-13'))

            scout.setPitData("PitOrganization", scout.rangefield('AF-12', 1, 3))
            scout.setPitData("WiringQuality", scout.rangefield('AF-13', 1, 3))
            scout.setPitData("BumperQuality", scout.rangefield('AF-14', 1, 3))
            scout.setPitData("Batteries", scout.rangefield('AC-16', 1, 7))

            scout.submit()

        # Takes an entry from the Scout database table and generates text for display on the team page.
        # This page has 4 columns, currently used for auto, 2 teleop, and other (like fouls and end game)


def generateTeamText(e):
    text = {'auto': "", 'teleop1': "", 'teleop2': "", 'other': ""}
    text['auto'] += 'Low: ' + str(e['AutoLow']) + ', ' if e['AutoLow'] else ''
    text['auto'] += 'High: ' + str(e['AutoHigh']) + ', ' if e['AutoHigh'] else ''
    text['auto'] += 'Taxi: ' + str(e['Taxi']) + ', ' if e['Taxi'] else ''
    text['auto'] += 'HP: ' + str(e['HPScore']) + ', ' if e['HPScore'] else ''

    text['teleop1'] += 'Low: ' + str(e['TeleLow']) + ', ' if e['TeleLow'] else ''
    text['teleop1'] += 'High: ' + str(e['TeleHigh']) + ', ' if e['TeleHigh'] else ''
    text['teleop1'] += 'Fender' ', ' if e['FenderShot'] else ''
    text['teleop1'] += 'LaunchPad' + ', ' if e['LaunchPadShot'] else ''
    text['teleop1'] = text['teleop1'][:-2]

    text['teleop2'] += 'Failed Climb  ' if e['FailedClimb'] else ''
    text['teleop2'] += 'Low Bar  ' if e['Hangar'] == 4 else ''
    text['teleop2'] += 'Mid Bar  ' if e['Hangar'] == 6 else ''
    text['teleop2'] += 'High Bar  ' if e['Hangar'] == 10 else ''
    text['teleop2'] += 'Traversal Bar  ' if e['Hangar'] == 15 else ''
    text['teleop2'] = text['teleop2'][:-2]

    text['other'] += 'Defense, ' if e['Defense'] else ''
    text['other'] += 'Defended, ' if e['Defended'] else ''
    text['other'] += 'Disabled, ' if e['Disabled'] else ''
    text['other'] = text['other'][:-2]

    return text


# Takes an entry from the Scout database table and generates chart data.
# The fields in the returned dict must match the CHART_FIELDS definition at the top of this file
def generateChartData(e):
    dp = dict(CHART_FIELDS)
    dp["match"] = e['match']

    dp['AutoLow'] += e['AutoLow']
    dp['AutoHigh'] += e['AutoHigh']
    dp['TeleLow'] += e['TeleLow']
    dp['TeleHigh'] += e['TeleHigh']
    dp['CargoTotal'] += e['AutoLow'] + e['AutoHigh'] + e['TeleLow'] + e['TeleHigh']
    dp['Hangar'] += e['Hangar']

    return dp


# Takes a set of team numbers and a string indicating quals or playoffs
# and returns a prediction for the alliances score and whether or not they will achieve any additional ranking points
def predictScore(event, teams, level='quals'):
    cargoRP = 0
    climbRP = 0
    climbTotal = 0
    cargoTotal = 0
    autoCargo = 0
    hpScore = 0
    traversalBar = 0
    highBar = 0
    mediumBar = 0
    lowBar = 0

    pointsTotal = 0

    for n in teams:
        average = server.getAggregateData(Team=n, Event=event, Mode="Averages")
        assert len(average) < 2
        if len(average):
            entry = average[0]
        else:
            entry = dict(SCOUT_FIELDS)
            entry.update(DISPLAY_FIELDS)
            entry.update(HIDDEN_DISPLAY_FIELDS)

        pointsTotal += entry['CargoPoints'] + entry['Taxi']
        cargoTotal += entry['Cargo']
        autoCargo += entry['AutoLow'] + entry['AutoHigh']
        if entry['HPScore'] > .5:
            hpScore = 1;
        if(entry['Hangar'] > 10):
            if(traversalBar<2):
                traversalBar += 1
            else:
                highBar += 1
        elif (entry['Hangar'] > 6):
            if (highBar < 2):
                highBar += 1
            else:
                mediumBar += 1
        elif (entry['Hangar'] > 4):
            if (mediumBar < 2):
                mediumBar += 1
            else:
                lowBar += 1
        elif (entry['Hangar'] > 0):
            if (lowBar < 2):
                lowBar += 1

    autoCargo += hpScore
    if (autoCargo > 4):
        if (cargoTotal > 18):
            cargoRP = 1
    else:
        if (cargoTotal > 20):
            cargoRP = 1

    climbTotal = traversalBar * 15 + highBar * 10 + mediumBar * 6 + lowBar * 4
    if (climbTotal > 15):
        climbRP = 1
    pointsTotal += climbTotal

    retVal = {'score': 0, 'RP1': 0, 'RP2': 0}

    retVal['score'] = pointsTotal
    retVal['RP1'] = cargoRP
    retVal['RP2'] = climbRP

    return retVal


# Takes an entry from the Scout table and returns
# whether or not the entry should be flagged based on contradictory data.
def autoFlag(entry):
    # Failed climb + hangar entry is invalid
    if (entry['FailedClimb'] and entry['Hangar']):
        return 1
    # Multiple hangar entries is invalid. Unfortunately Low + Medium is not caught
    if not (entry['Hangar'] == 4 or entry['Hangar'] == 6 or entry['Hangar'] == 10 or entry['Hangar'] == 15 ):
        return 1
