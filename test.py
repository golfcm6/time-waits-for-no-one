import pandas as pd

# process logs to compile all reads and sends
sends = dict()
reads = dict()
for l in ['a', 'b', 'c']:
    df = pd.read_csv(f'machine_log_{l}.txt', sep = '|').rename(str.strip, axis='columns')
    l_sends = list(df[df['E'] == 'send '].apply(lambda row: (row['M'].strip(), row['Clock']), axis = 1))
    new_sends = []
    # split up multiple process sends into two single sends
    for send in l_sends:
        for m in send[0].split():
            new_sends.append((m, send[1]))
    sends[l] = new_sends
    reads[l] = list(df[df['E'] == 'read '].apply(lambda row: (row['M'].strip(), row['Clock']), axis = 1))

# ensure that all reads have a corresponding send by removing acknowledged sends as you
# process the corresponding read
for l in ['a', 'b', 'c']:
    # process all reads
    for sender, clock_r in reads[l]:
        found = False
        # for each read, find a corresponding send and ensure it has a lower or equal clock
        # lower or equal is fine because the log happens after the clock update
        # and the send happens before, so if send says t, log says t+1, and receiver
        # should say max(c,t) + 1 >= t + 1
        for i, (recipient, clock_s) in enumerate(sends[sender]):
            if recipient == l:
                assert clock_r >= clock_s, f'{l, sender, clock_r, clock_s}'
                found = True
                # remove the send to avoid acknowledging the same send twice
                sends[sender].pop(i)
                break
        assert found, f'{l, sender,clock_r}'