# parallel_shakespeare
This repository contains an example use case of multithreading in Python.

It uses the JSTOR Shakespeare citational dataset, which you can download here: https://rice.box.com/s/z9o1f09bf4n4nvkwl794xcw7hcvni5da
(too large for my free Github account)

The basic outline of the project is this:
* We are given a list of citations of Shakespeare play lines in JSTOR articles
* We want to transform this into a co-citational list that shows us which lines are cited alongside which other lines in which articles
* We want to do this quickly, so we break the work up and spread it over an arbitrary number of processes
* We want to maximize our efficiency, so we include a few performance testing scripts
* Extra credit: turn this into a recommendation engine!

Files & functions

SOURCE DATABASE

* shakespeare.db -- download from https://rice.box.com/s/z9o1f09bf4n4nvkwl794xcw7hcvni5da -- an sqlite database that contains 3 tables
 * articles: basic metadata on 71,639 JSTOR articles that quote Shakespeare
* * play_lines: basic metadata on the 94,049 known Shakespearean play lines quoted by those articles
* * matches: 623,428 matches (one to one) of articles to play lines

DESTINATION DATABASE
* ariel.db -- a template into which we will pour our transformed data -- an sqlite database that contains 3 tables
* * docs: corresponds directly to the "articles" table in shakespeare.db
* * lines: the complete shakespearean dramatic corpus from the Folger library, line by line (114,985 entries)
* * lines_and_docs_matches: pairs of co-cited lines and the citing article

SCRIPTS
* shakespeare.py
* * input: the row id in shakespeare.db for a play line
* * output: an array of co-citations ready for ariel.db, each in the form (source_line,target_line,citing_article,*boolean*)
* * transformational quirk: an artifact of the process is that, when run through the whole dataset, it produces 2 copies of the same data -- we use the *boolean* slot to separate those into 2 streams, rather than deleting them, because it's a great for validation
* multiproc_on_shakespeare.py
* * options:
* * * -m = the number of lines to look up co-citations for. m=0 (default) runs through the full set of 94,049 lines
* * * -n = the number of processes to spread the work over
* * it creates intermediary csv files to store the different processes' work in
* * it creates ariel-a.db and ariel-b.db for the symmetrical outputs, injects the csv data into these, and deletes the intermediary csv files


The other scripts do some performance benchmarking to help you optimize the job.
