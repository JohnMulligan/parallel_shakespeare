import sqlite3
import re
from optparse import OptionParser, Option, OptionValueError
import sys
import time

raw_rowid=sys.argv[1]
	
def find_matches(jstor_line_rowid):
	
	jstor_shakespeare_db = sqlite3.connect('shakespeare.db',check_same_thread=False)
	ariel_check = sqlite3.connect('ariel.db',check_same_thread=False)
	jstor_cursor = jstor_shakespeare_db.cursor()
	ariel_cursor = ariel_check.cursor()
	
	#print(ariel_match_rowid)
	source_line = jstor_cursor.execute("select line from play_lines where rowid = ?", [jstor_line_rowid]).fetchone()[0]
	#print(source_line)
	
	
	
	#get the doc and the line on the match from shakespeare (our input database)
	#these will serve as our "source" line
	dois = jstor_cursor.execute("SELECT docid FROM matches WHERE line = ?;", [source_line]).fetchall()
	
	line_to_line_matches=[]
	
	if len(dois)>0:
		dois = [i[0] for i in dois]
		query="SELECT docid,line FROM matches WHERE docid IN ('%s') AND line <> '%s';" %("','".join(dois),source_line)
		#print(query)
		lines_and_dois=jstor_cursor.execute(query).fetchall()
		#print(lines_and_dois)
		
		line_to_line_matches=[]
		
		if len(lines_and_dois)>0:
			
			lines = list(set([i[1] for i in lines_and_dois]))
			dois = list(set([i[0] for i in lines_and_dois]))
			
			#print(lines)
			#print(dois)
			
			lines.append(source_line)
			
			query="SELECT line,rowid FROM lines WHERE line in ('%s')" %"','".join(lines)
			#print(query)
			ariel_lines_rowids_dict = dict(ariel_cursor.execute(query).fetchall())
			#print(dict(ariel_target_line_rowids))
			#print(ariel_target_line_rowids_dict)
			
			query = "SELECT doi,rowid FROM docs WHERE doi in ('%s')" %"','".join(dois)
			ariel_citing_dois_rowids_dict = dict(ariel_cursor.execute(query).fetchall())
			#print(ariel_citing_dois_rowids_dict)
			
			source_rowid=ariel_lines_rowids_dict[source_line]
			
			
			
			for target in lines_and_dois:
				
				try:
					target_line = target[1]
					target_doc = target[0]
					
					target_rowid = ariel_lines_rowids_dict[target_line]
					doc = ariel_citing_dois_rowids_dict[target_doc]
					
					
					line_to_line_matches.append((min(source_rowid,target_rowid),max(source_rowid,target_rowid),doc,source_rowid>target_rowid))
				except:
					print("error",target,source_line)
	
	
	final = list(set(line_to_line_matches))
	return(final)

		
if __name__ == '__main__':
	start_time=time.time()
	matches = find_matches(raw_rowid)
	print(matches)
	print("running time: ",time.time()-start_time)
