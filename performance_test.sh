for i in $(seq 1 ${1});
do
python3 multiproc_on_shakespeare.py -m ${2} -n $i;
done
