import sqlite3
import re
import time
import csv
import shakespeare
from multiprocessing import Pool,TimeoutError
from optparse import OptionParser, Option, OptionValueError
import numpy
import os
import shutil

#m will be the number of lines to find matches for
##TO RUN LOOKUPS ON THE WHOLE DATABASE, USE m=0
#n will be the number of threads to run

#Example: to look up and record 500 matches on 10 threads you would run python3 multiproc_on_shakespeare.py -m 500 -n 10

parser = OptionParser()
parser.add_option("-m", action="store", type="int", dest="m",default=0)
parser.add_option("-n", action="store", type="int", dest="n",default=0)
(options, args) = parser.parse_args()
m=options.m
n=options.n


#This function collects "m" row id's to be looked up
def get_work(limit=0):
	cnx = sqlite3.connect('shakespeare.db')
	jstor_shakespeare_cursor = cnx.cursor()
	if limit==0:
		jstor_shakespeare_cursor.execute("SELECT rowid FROM play_lines order by random();")
	else:
		jstor_shakespeare_cursor.execute("SELECT rowid FROM play_lines order by random() limit %d;" %limit)
	#return jstor_shakespeare_cursor
	work_rows = [i[0] for i in jstor_shakespeare_cursor]
	cnx.close()
	return work_rows

#This is the function that each process runs
#It spawns 2 csv files specific to the process to record its outputs
#And then runs the shakespeare.py script/algorithm to find the matches
def multi_process(work):

	p_id=os.getpid()
	process_start_time = time.time()
	print("process %s starting %s lookups at %s" %(str(p_id),str(len(work)),str(process_start_time)))
	with open(r'%s-a.csv' %str(p_id),'a') as csvfilea:
		with open(r'%s-b.csv' %str(p_id),'a') as csvfileb:
			writera=csv.writer(csvfilea,delimiter='|')
			writerb=csv.writer(csvfileb,delimiter='|')
			for jstor_line_rowid in work:
				#loop_start_time=time.time()
				matches = shakespeare.find_matches(jstor_line_rowid)
				for match in matches:
					if match[3]==False:
						writera.writerow(match[0:3])
					else:
						writerb.writerow(match[0:3])
				#print("step time: %s" %(str(time.time()-loop_start_time)))
	print("process %s finished in %s seconds" %(str(p_id),str(time.time()-process_start_time)))

#this function feeds the completed csv files into their appropriate destination databases
#and deletes the csv's when it's finished
def add_csvs():
	csvs = [i for i in os.listdir('.') if i.endswith('.csv')]
	print('test')
	for csv in csvs:
		print(csv)
		loop_start = time.time()
		tag = re.search('(?<=-)[a|b](?=\.csv)',csv).group(0)
		os.system('sqlite3 ariel-%s.db ".import %s lines_and_docs_matches"' %(tag,csv))
		print("%s seconds" %(time.time()-loop_start))
		os.remove(csv)


if __name__ == '__main__':
	start_time = time.time()
	
	#clean slate.
	#remove the a & b destination databases, and create new, clean ones
	if os.path.exists('ariel-a.db'):
		os.remove('ariel-a.db')
	if os.path.exists('ariel-b.db'):
		os.remove('ariel-b.db')
	shutil.copyfile('ariel.db','ariel-a.db')
	shutil.copyfile('ariel.db','ariel-b.db')
	
	
	with Pool(processes=n) as pool:
		work_rows = get_work(m)
		#jstor_shakespeare_cursor=get_cursor(m)
		#work_rows = [i[0] for i in jstor_shakespeare_cursor]
		if m==0:
			m=len(work_rows)
		
		#this implementation splits up the work evenly amongst the workers rather than farm out the distribution to pool.map
		#why? because my final result is going to be some very large csv files
		#and i don't want a) 95,000 file i/o's or b) the bottleneck/memory leak problem that comes with the pool manager having to handle 29 million objects in unstructured arrays
		batch_size = int(m/n)
		#even distribution of m/n batches
		work_assignments = [work_rows[i*batch_size:i*batch_size + batch_size] for i in range(n)]
		#then layer on the remainders
		remainder_count = m%n
		for r in range(remainder_count):
			work_assignments[r].append(work_rows[-(r+1)])
		
		for wa in work_assignments:
			print(len(wa))
		#print(work_assignments)
		pool.map(multi_process,work_assignments)
	
	total_running_time =  time.time() - start_time
	
	print("%d lookups in %d seconds on %d threads" %(m,int(total_running_time),n))
	
	print("adding results to ariel-a.db and ariel-b.db")
	
	add_csvs()
	
	print("added results to ariel databases (presumably)")
	
	print("final running time including import to ariel is %s seconds" %(str(int(time.time() - start_time))))
