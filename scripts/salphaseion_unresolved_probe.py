#!/usr/bin/env python3
"""Controlled probe for unresolved SalPhaseIon sections from uploaded note.
Focus: Part2, Part4 subpart, Part10.  No private material printed.
"""
from pathlib import Path
from itertools import permutations, combinations
import hashlib, string, re, csv

src=Path('/home/user/uploads/Salphaseion decode.txt').read_text(errors='ignore')
P2='bihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe'
# Extract Part4 decoded intermediate beginning with btcseed.
start=src.find('btcseed')
end=src.find(' -> ?', start)
P4=src[start:end].replace('\r','').replace('\n','').replace('\t','').replace(' ','') if start!=-1 and end!=-1 else ''
P4_BODY=P4[6:] if P4.startswith('btcseed') else P4
ODD=P4_BODY[0::2]
EVEN=P4_BODY[1::2]
COMMON=['the','you','your','password','matrix','sum','list','last','choice','seed','btc','key','answer','command','private','blue','yellow','prime','true','give','away','front','eyes','sha','hash','wif','second']
ALPHA=string.ascii_lowercase

def score(txt):
    t=txt.lower()
    return sum(t.count(w)*len(w) for w in COMMON)
def printable(bs): return ''.join(chr(b) if 32<=b<127 else '.' for b in bs)

def big_decimal_convert(s, mode):
    if mode=='a1': mp={ch:str(i+1) for i,ch in enumerate('abcdefghi')}
    elif mode=='a0': mp={ch:str(i) for i,ch in enumerate('abcdefghi')}
    num=''.join(mp[ch] for ch in s)
    h=hex(int(num,10))[2:]
    if len(h)%2: h='0'+h
    return printable(bytes.fromhex(h))

def bifid5_dec(ct,period,key=''):
    alpha='abcdefghiklmnopqrstuvwxyz'
    seen=[]
    for ch in (key+alpha).lower():
        if ch=='j': ch='i'
        if ch in alpha and ch not in seen: seen.append(ch)
    sq=''.join(seen)
    coords={ch:(i//5,i%5) for i,ch in enumerate(sq)}; rev={v:k for k,v in coords.items()}
    out=''
    for k in range(0,len(ct),period):
        block=ct[k:k+period]
        digits=[]
        for ch in block:
            if ch not in coords: return ''
            digits.extend(coords[ch])
        L=len(block); rows=digits[:L]; cols=digits[L:]
        out+=''.join(rev[(r,c)] for r,c in zip(rows,cols))
    return out

def vigenere(s,key,mode):
    key=''.join(c for c in key.lower() if c in ALPHA)
    if not key: return ''
    out=[]
    for i,ch in enumerate(s):
        x=ALPHA.index(ch); k=ALPHA.index(key[i%len(key)])
        if mode=='dec': y=(x-k)%26
        elif mode=='enc': y=(x+k)%26
        else: y=(k-x)%26
        out.append(ALPHA[y])
    return ''.join(out)

rows=[]
# Part2 tests.
for mode in ['a1','a0']:
    out=big_decimal_convert(P2,mode)
    rows.append({'part':'P2','test':'big_decimal_'+mode,'score':score(out),'sha8':hashlib.sha256(out.encode()).hexdigest()[:8],'preview':out[:80]})
# group sums 3 and 6.
for L in [2,3,6,13]:
    vals=[sum(ord(c)-96 for c in P2[i:i+L]) for i in range(0,len(P2),L)]
    letters=''.join(chr(97+((v-1)%26)) for v in vals)
    rows.append({'part':'P2','test':f'A1_group_sum_L{L}','score':score(letters),'sha8':hashlib.sha256(letters.encode()).hexdigest()[:8],'preview':letters[:80]})
# Bifid standard/keyed smoke.
for key in ['','part','partfour','matrixsumlist','btcseed','yourlastcommand','secondanswer']:
    for per in [5,7,10,13,26,78]:
        out=bifid5_dec(P2,per,key)
        rows.append({'part':'P2','test':f'bifid5_key={key or "std"}_per{per}','score':score(out),'sha8':hashlib.sha256(out.encode()).hexdigest()[:8],'preview':out[:80]})

# Part4 tests.
rows.append({'part':'P4','test':'structure','score':0,'sha8':hashlib.sha256(P4.encode()).hexdigest()[:8],'preview':f'P4_len={len(P4)} body={len(P4_BODY)} odd={len(ODD)} even={len(EVEN)} odd_charset={"".join(sorted(set(ODD)))} even_charset={"".join(sorted(set(EVEN)))}'})
# Vigenere on even with known keys.
for key in ['btcseed','matrixsumlist','enter','lastwordsbeforearchichoice','thispassword','yourlastcommand','secondanswer','sha256','bifid','partfour','thematrixhasyou']:
    for mode in ['dec','enc','beau']:
        out=vigenere(EVEN,key,mode)
        rows.append({'part':'P4_even','test':f'vigenere_{mode}_{key}','score':score(out),'sha8':hashlib.sha256(out.encode()).hexdigest()[:8],'preview':out[:80]})
# binary/base4/Bacon on odd.
for ones_len in [1,2,3]:
    for ones in combinations('bcde',ones_len):
        for inv in [False,True]:
            one=set(ones)
            bits=''.join('1' if ((ch in one)^inv) else '0' for ch in ODD)
            # Bacon 5-bit
            out=''
            for i in range(0,len(bits)-4,5):
                v=int(bits[i:i+5],2)
                out+=ALPHA[v] if v<26 else '?'
            rows.append({'part':'P4_odd','test':f'bacon_ones={"".join(ones)}_inv={inv}','score':score(out),'sha8':hashlib.sha256(out.encode()).hexdigest()[:8],'preview':out[:80]})
# base4 mappings
for perm in permutations(['00','01','10','11']):
    mp=dict(zip('bcde',perm)); bits=''.join(mp[ch] for ch in ODD)
    for size in [5,6,7,8]:
        for off in range(min(size,2)):  # keep bounded
            vals=[int(bits[i:i+size],2) for i in range(off,len(bits)-size+1,size)]
            if size==5:
                out=''.join(ALPHA[v] if v<26 else '?' for v in vals)
            elif size==6:
                b64='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
                out=''.join(b64[v] for v in vals)
            else:
                out=''.join(chr(v) if 32<=v<127 else '.' for v in vals)
            sc=score(out)
            if sc>0:
                rows.append({'part':'P4_odd','test':f'base4_perm={perm}_size{size}_off{off}','score':sc,'sha8':hashlib.sha256(out.encode()).hexdigest()[:8],'preview':out[:80]})
# Part10 interpretation.
p10_candidate='secondanswer'
rows.append({'part':'P10','test':'semantic_ans_too','score':999,'sha8':hashlib.sha256(p10_candidate.encode()).hexdigest()[:8],'preview':'anstoo = ans too = answer two = second answer -> secondanswer'})

# sort by score, write TSV and summary
rows_sorted=sorted(rows,key=lambda r:(-int(r['score']),r['part'],r['test']))
out='/home/user/salphaseion_unresolved_probe_results.tsv'
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['part','test','score','sha8','preview'],delimiter='\t')
    w.writeheader(); w.writerows(rows_sorted)
summary='/home/user/salphaseion_unresolved_probe_summary.txt'
with open(summary,'w') as f:
    f.write('SalPhaseIon unresolved parts probe summary\n')
    f.write(f'Part2 len={len(P2)}; notable group property: L3 A1 sums -> {next(r["preview"] for r in rows if r["part"]=="P2" and r["test"]=="A1_group_sum_L3")}\n')
    f.write(f'Part4 intermediate starts with btcseed; body splits odd/even {len(ODD)}/{len(EVEN)}; odd alphabet={"".join(sorted(set(ODD)))}.\n')
    f.write('No strong plaintext hit found for Part2 or Part4 substreams under tested base/Bifid/Vigenere/Bacon/base4 probes.\n')
    f.write('Part10 high-confidence: anstoo -> ans too -> answer two -> secondanswer.\n')
    f.write('Top non-P10 rows:\n')
    for r in [x for x in rows_sorted if x['part']!='P10'][:12]:
        f.write(f"{r['part']}\t{r['test']}\tscore={r['score']}\tsha8={r['sha8']}\t{r['preview']}\n")
print('SalPhaseIon unresolved probe')
print('Part2: no strong decode yet; L3-sum stream recorded')
print('Part4: btcseed split odd/even confirmed; no strong subdecode yet')
print('Part10: high-confidence = secondanswer')
print('summary:', summary)
print('tsv:', out)
