import cherrypy
import sqlite3 as sql
import os
from ast import literal_eval

class ScoutServer(object):
	@cherrypy.expose
	def index(self):
		table = ''
		conn = sql.connect('data.db')
		averages = conn.cursor().execute('SELECT * FROM averages ORDER BY apr DESC').fetchall()
		conn.close()
		for team in averages:
			table += '''
			<tr>
				<td><a href="team?n={0}">{0}</a></td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
				<td>{5}</td>
				<td>{6}</td>
			</tr>
			'''.format(team[0], team[6], team[1], team[2], team[3], team[4], team[5])
		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
         		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
         		<script>
         		if (typeof jQuery === 'undefined')
				  document.write(unescape('%3Cscript%20src%3D%22/static/js/jquery.js%22%3E%3C/script%3E'));
         		</script>
				<script type="text/javascript" src="/static/js/jquery.tablesorter.js"></script>
				<script>
				$(document).ready(function() {{
					$("table").tablesorter();
				}});
				</script>
			</head>
			<body>
				<h1>PiScout</h1>
				<h2>FRC Team 2067</h2>
				<br><br>
				<p class="main">Choose a Team</p>
				<form method="get" action="team">
					<input id="team" type="text" maxlength="4" name="n" autocomplete="off"/>
					<br>
					<button id="submit" type="submit">Submit</button>
				</form>
				<br><br>
				<p class="main">Team Averages</p>
				<table style="font-size: 140%;" class="tablesorter">
					<thead><tr>
						<th>Team</th>
						<th>APR</th>
						<th>Auto</th>
						<th>Step</th>
						<th>Tote</th>
						<th>RC/Noodle</th>
						<th>Coop</th>
					</tr></thead>
					<tbody>{0}</tbody>
				</table>
			</body>
		</html>'''.format(table)

	@cherrypy.expose()
	def team(self, n=2067):
		conn = sql.connect('data.db')
		cursor = conn.cursor()
		entries = cursor.execute('SELECT * FROM scout WHERE team=? ORDER BY MATCH DESC', (n,)).fetchall()
		averages = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
		assert len(averages) < 2
		if len(averages):
			sum = averages[0]
		else:
			sum = [0]*7
		conn.close()
		output = ''
		dataset = []
		for e in entries:
			dp = {"match": e[1], "rc":0, "tote":0, "auto":0, "step":0}
			a = ''
			if e[5]: #stacked?
				a += "3 tote; "
				dp['auto'] += 20;
			elif e[2] == 3: #number of totes
				a += "3 tote, not stacked; "
				dp['auto'] += 6
			elif e[2]:
				a += str(e[2]) + ' totes; '
				dp['auto'] += 2*e[2]
			if e[3]:
				dp['auto'] += 8/3 * e[3]
				a += str(e[3]) +  ' RC(s) in zone; '
			if e[4]:
				dp['step'] = e[4]
				a += str(e[4]) + ' RC(s) from step; '
			if e[6]:
				dp['auto'] += 4/3
				a += 'moved into auto zone; '
			s = ''
			for stack in range(7, 13):
				if e[stack] == 'None':
					continue
				st = literal_eval(e[stack])
				if st['capping']:
					s += 'capped '
					dp['rc'] += st['height']*4
				else:
					dp['tote'] += st['height']*2
				s += str(st['height']) + ' stack'
				if st['capped']:
					dp['rc'] += st['height']*4
					s += ', capped'
				if st['noodled']:
					dp['rc'] += 6
					s += '/noodled'
				s += '; '

			o = ''
			if e[13]:
				o += str(e[13]) + ' coop totes; '
			if e[14]:
				o += str(e[14]) + ' RCs from step; '
			if e[16] == 1:
				o += 'all totes from HP'
			elif e[16] == 18:
				o += 'all totes from landfill'
			elif 2 <= e[16] <= 7:
				o += 'most totes from HP'
			elif 17 >= e[16] >= 12:
				o += 'most totes from landfill'
			elif e[16] == 0:
				o += "doesn't pick up gray totes"
			else:
				o += "totes equally from landfill/HP"
			output += '''
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
			</tr>'''.format(e[1], a[:-2], s[:-2], o)
			for key,val in dp.items():
				dp[key] = round(val, 2)
			dataset.append(dp)

		dataset.reverse()
		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
         		<script type="text/javascript" src="/static/js/amcharts.js"></script>
				<script type="text/javascript" src="/static/js/serial.js"></script>
				<script>
					var chart;
					var graph;

					var chartData = {8};

					AmCharts.ready(function () {{
						// SERIAL CHART
						chart = new AmCharts.AmSerialChart();

						chart.dataProvider = chartData;
						chart.marginLeft = 10;
						chart.categoryField = "match";

						// AXES
						// category
						var categoryAxis = chart.categoryAxis;
						categoryAxis.dashLength = 3;
						categoryAxis.minorGridEnabled = true;
						categoryAxis.minorGridAlpha = 0.1;

						// value
						var valueAxis = new AmCharts.ValueAxis();
						valueAxis.position = "left";
						valueAxis.axisColor = "#111111";
						valueAxis.gridAlpha = 0;
						valueAxis.axisThickness = 2;
						chart.addValueAxis(valueAxis)

						var valueAxis2 = new AmCharts.ValueAxis();
						valueAxis2.position = "right";
						valueAxis2.axisColor = "#FCD202";
						valueAxis2.gridAlpha = 0;
						valueAxis2.axisThickness = 2;
						chart.addValueAxis(valueAxis2);

						// GRAPH
						graph = new AmCharts.AmGraph();
						graph.title = "RC/Noodle Points";
						graph.valueAxis = valueAxis;
						graph.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph.lineColor = "#637bb6";
						graph.bullet = "round";
						graph.bulletSize = 8;
						graph.bulletBorderColor = "#FFFFFF";
						graph.bulletBorderAlpha = 1;
						graph.bulletBorderThickness = 2;
						graph.lineThickness = 2;
						graph.valueField = "tote";
						graph.balloonText = "Tote Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph);

						graph2 = new AmCharts.AmGraph();
						graph2.title = "Tote Points";
						graph2.valueAxis = valueAxis;
						graph2.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph2.lineColor = "#187a2e";
						graph2.bullet = "round";
						graph2.bulletSize = 8;
						graph2.bulletBorderColor = "#FFFFFF";
						graph2.bulletBorderAlpha = 1;
						graph2.bulletBorderThickness = 2;
						graph2.lineThickness = 2;
						graph2.valueField = "rc";
						graph2.balloonText = "RC Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph2);

						graph3 = new AmCharts.AmGraph();
						graph3.title = "Auto Points";
						graph3.valueAxis = valueAxis;
						graph3.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph3.lineColor = "#FF6600";
						graph3.bullet = "round";
						graph3.bulletSize = 8;
						graph3.bulletBorderColor = "#FFFFFF";
						graph3.bulletBorderAlpha = 1;
						graph3.bulletBorderThickness = 2;
						graph3.lineThickness = 2;
						graph3.valueField = "auto";
						graph3.balloonText = "Auto Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph3);

						graph4 = new AmCharts.AmGraph();
						graph4.valueAxis = valueAxis2;
						graph4.title = "Step RCs";
						graph4.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph4.lineColor = "#FCD202";
						graph4.bullet = "round";
						graph4.bulletSize = 8;
						graph4.bulletBorderColor = "#FFFFFF";
						graph4.bulletBorderAlpha = 1;
						graph4.bulletBorderThickness = 2;
						graph4.lineThickness = 2;
						graph4.valueField = "step";
						graph4.balloonText = "RCs from Step:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph4);

						// CURSOR
						var chartCursor = new AmCharts.ChartCursor();
						chartCursor.cursorAlpha = 0;
						chartCursor.cursorPosition = "mouse";
						chart.addChartCursor(chartCursor);

						var legend = new AmCharts.AmLegend();
						legend.marginLeft = 110;
						legend.useGraphSettings = true;
						chart.addLegend(legend);
						chart.creditsPosition = "bottom-right";

						// WRITE
						chart.write("chartdiv");
					}});
				</script>
			</head>
			<body>
				<h1>Team {0}</h1>
				<h2>PiScout Database</h2>
				<br><br>
				<div style="text-align:center;">
					<div id="apr">
						<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
						<p style="font-size: 400%; line-height: 0em">{7}</p>
					</div>
					<div id="stats">
						<p class="statbox" style="font-weight:bold">Average match:</p>
						<p class="statbox">Auto points: {2}</p>
						<p class="statbox">Step RCs: {3}</p>
						<p class="statbox">Tote points: {4}</p>
						<p class="statbox">RC/noodle points: {5}</p>
						<p class="statbox">Coop points: {6}</p>
					</div>
				</div>
				<br>
				<div id="chartdiv" style="width:1000px; height:400px; margin: 0 auto;"></div>
				<br>
				<table>
					<thead><tr>
						<th>Match</th>
						<th>Auto</th>
						<th>Stacks</th>
						<th>Other Teleop</th>
					</tr></thead>{1}
				</table>
			</body>
		</html>'''.format(n, output, sum[1], sum[2], sum[3], sum[4], sum[5], sum[6], str(dataset).replace("'",'"'))

	@cherrypy.expose
	def submit(self, data=''):
		d = literal_eval(data)
		conn = sql.connect('data.db')
		cursor = conn.cursor()
		cursor.execute('INSERT INTO scout VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',((d['team'],d['match']
			,d['auto_tote'],d['auto_RC_zone'],d['auto_RC_step'],int(d['auto_stack']),int(d['in_auto_zone']))
			+ tuple(map(str, d['stacks'])) + (d['coop'],d['tele_RC_step'],int(d['coop_stack']),d['tote_loc'])))
		conn.commit()

		entries = cursor.execute('SELECT * FROM scout WHERE team=? ORDER BY MATCH DESC', (d['team'],)).fetchall()

		sum = {'auto': 0, 'step': 0, 'tote': 0, 'rc': 0, 'coop': 0}
		for e in entries:
			if e[5]: #stacked?
				sum['auto'] += 20
			elif e[2] == 3: #number of totes
				sum['auto'] += 6
			elif e[2]:
				sum['auto'] += 2*e[2]
			if e[3]:
				sum['auto'] += 8/3 * e[3]
			if e[4]:
				sum['step'] += e[4]
			if e[6]:
				sum['auto'] += 4/3
			for stack in range(7, 13):
				if e[stack] == 'None':
					continue
				st = literal_eval(e[stack])
				if not st['capping']:
					sum['tote'] += st['height'] * 2
				if st['capped'] or st['capping']:
					sum['rc'] += st['height'] * 4
				if st['noodled']:
					sum['rc'] += 6
			if e[13]:
				sum['coop'] += 10*e[13]

		for key,val in sum.items():
			sum[key] = round(val/len(entries), 2)
		apr = int(sum['auto']*1.2 + sum['step']*5 + sum['tote'] + sum['rc'] + sum['coop']*0.2)

		cursor.execute('DELETE FROM averages WHERE team=?',(d['team'],))
		cursor.execute('INSERT INTO averages VALUES (?,?,?,?,?,?,?)',(d['team'], sum['auto'], sum['step'],
																sum['tote'], sum['rc'], sum['coop'], apr))
		conn.commit()
		conn.close()
		return data

if not os.path.isfile('data.db'):
	conn = sql.connect('data.db')
	conn.cursor().execute('''CREATE TABLE scout (team integer,match integer,auto_tote integer,auto_RC_zone integer
		,auto_RC_step integer,auto_stack integer,in_auto_zone integer,stack1 text,stack2 text,stack3 text,stack4 text
		,stack5 text,stack6 text,coop integer,tele_RC_step integer,coop_stack integer,tote_loc integer)''')
	conn.cursor().execute('''CREATE TABLE averages (team integer,auto real,step real,tote real,rc real
													,coop real,apr integer)''')
	conn.close()

conf = {
	 '/': {
		 'tools.sessions.on': True,
		 'tools.staticdir.root': os.path.abspath(os.getcwd())
	 },
	 '/static': {
		 'tools.staticdir.on': True,
		 'tools.staticdir.dir': './public'
	 },
	'global': {
		'server.socket_port': 8000
	}
}

#start method only to be used on the local version
def start():
	cherrypy.quickstart(ScoutServer(), '/', conf)