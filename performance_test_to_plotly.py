import re
import plotly
from plotly.graph_objs import Scatter, Layout
import sys

fnames = sys.argv[1:len(sys.argv)]

databuffer=[]
p = re.compile('[0-9]+ lookups in [0-9]+ seconds on [0-9]+ threads')

for fname in fnames:

	d=open(fname,'r')
	t=d.read()
	d.close()

	x_vals=[]
	y_vals=[]
	for line in t.split('\n'):
	
		if re.match(p,line):
			lookups,seconds,threads=re.findall('[0-9]+',line)
			print(lookups,seconds,threads)
			
			lookupspersecond=int(lookups)/int(seconds)
			
			x_vals.append(threads)
			y_vals.append(lookupspersecond)
			count=lookups



	databuffer.append(Scatter(x=x_vals,y=y_vals,name=fname))
	
plotly.offline.plot({
"data":databuffer,
"layout": Layout(title="Performance: Lookups per second vs. processes count, finding %s matches" %count)},
filename="performance_test.html")
