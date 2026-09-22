########################################################
# read an event log .csv file and clean it up
#
# jech
########################################################

from pathlib import Path


elog_fn = Path('/home/user/DX202301/event_log/DX202301_10-sec.csv')
#elog_fn = Path('/home/user/DX202301/event_log/test.csv')
with elog_fn.open() as infl:
    elog_data = infl.readlines()
elog_outfn = Path('/home/user/DX202301/event_log/DX202301_eventlog_clean.csv')

# the begin, end, stop, resume are in the Comment column, which is 8
event_words = ['begin', 'end', 'start', 'resume', 'stop']
start_words = ['begin', 'start', 'resume']
end_words = ['stop', 'end']

# the index of the comments field
cidx = 8
event_list = []
hdr = elog_data[0].strip()
# select only those lines with the event_words in the comments
for line in elog_data[1:]:
    line = line.strip()
    comment = line.split(',')[cidx]
    if any(word in comment for word in event_words):
        event_list.append(line)
        #print(f'found: {word}')

# the index of the transect number
tridx = 7
# insert a field after the transect number indicating begin, end, ...
eventidx = tridx+1
# add the field heading to match the inserted column
hdrarr = hdr.split(',')
hdrarr.insert(eventidx, 'event_code')
hdr = ','.join(hdrarr)
# correct transect numbering
# the initial transect numbers start at zero
begin_tr_num = 0
tr_num = 0
for i in range(len(event_list)):
    larr = event_list[i].split(',')
    recorded_tr_num = int(larr[tridx])
    comment = larr[cidx]
    if any(word in comment for word in start_words):
        # the transect begins, starts, or resumes
        if ('begin' in comment): 
            tr_num += 1
            begin_tr_num = tr_num
            larr[tridx] = str(begin_tr_num)
            larr.insert(eventidx, 'begin')
        elif ('resume' in comment):
            larr[tridx] = str(begin_tr_num)
            larr.insert(eventidx, 'resume')
        elif ('start' in comment):
            tr_num += 1
            larr[tridx] = str(tr_num)
            larr.insert(eventidx, 'start')
    else:
        # the transect either stops or ends
        if ('stop' in comment):
            larr[tridx] = str(tr_num)
            larr.insert(eventidx, 'stop')
        else:
            larr[tridx] = str(begin_tr_num)
            larr.insert(eventidx, 'end')

    event_list[i] = ','.join(larr)

with elog_outfn.open('w') as outfl:
    outfl.write(hdr+'\n')
    for oline in event_list:
        outfl.write(oline+'\n')



