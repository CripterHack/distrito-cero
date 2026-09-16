"""Bounded, plain-text failure details for console/Actions; not a retry policy."""
import re
from pathlib import Path

def plain(text):
    # Never replay workflow commands or terminal escape/control sequences from logs.
    text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',str(text))
    text=''.join(c if c=='\n' or c=='\t' or ord(c)>=32 else ' ' for c in text)
    return text.replace('::',': :')

def failure_summary(entry, logfile):
    if entry.get('status')!='failed':
        return ''
    head=f"QA FAILURE: {entry.get('suite')} | exit={entry.get('exitCode')} | expected checks={entry.get('expectedChecks')}\n{entry.get('error','Failed verification')}"
    try:
        with Path(logfile).open('rb') as stream:
            stream.seek(0,2);size=stream.tell();stream.seek(max(0,size-12000))
            tail=stream.read(12000).decode('utf-8',errors='replace')
        tail='\n'.join(tail.splitlines()[-60:])
    except OSError as error:
        tail='Producer log unavailable: '+str(error)
    return plain(head)+'\n'+'\n'.join(' | '+line for line in plain(tail).splitlines())
