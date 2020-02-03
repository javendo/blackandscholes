"""
python bubble.py 100 simulation.log > graph1.html
"""

import csv
import sys

filename = sys.argv[2]
time_factor = int(sys.argv[1])

s = list(csv.reader(open(filename, 'r'), delimiter='\t'))
start_time = int(s[1][5])
result = {}

servers = [
        "10.58.182.234:[80]",
        "10.58.182.235:[80]",
        "10.58.182.236:[80]",
        "10.58.182.237:[80]",
        "10.58.182.238:[80]",
        "10.58.182.239:[80]",
        "10.58.182.240:[80]",
        "10.58.182.241:[80]",
        "10.58.182.242:[80]",
        "10.58.182.243:[80]"
]

html = """
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Time', '%s'],
          %s
        ]);

        var options = {
            title: "Requests per machine",
            width: 1600, height: 800,
            vAxis: {title: "Machines"},
            hAxis: {title: "Requests each %s second"}
        }

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <div id="chart_div" style="width: 1600px; height: 800px;"></div>
  </body>
</html>
""" % ("', '".join(servers), '%s', time_factor)

for line in s:
        if line[0] == 'REQUEST' and line[9] == 'OK':
                time = int((int(line[5]) - start_time) / (time_factor * 1000)) + 1
                ip = line[11].split(' ')[4]
                if not time in result:
                        result[time] = {}
                result[time][ip] = result[time].get(ip, 0) + 1

data = []
for k1, v1 in result.items():
        data_by_time = [str(v1.get(s, 0)) for s in servers]
        data.append("['%s',%s]" % (k1, ','.join(data_by_time)))

print(html % ",".join(data))
