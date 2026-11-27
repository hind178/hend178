# Align known script lines to the narration using pauses (silencedetect) + character-length weighting.
import json,re,subprocess
segs_raw=subprocess.run(["ffmpeg","-hide_banner","-i","assets/audio/narration.mp3","-af","silencedetect=noise=-35dB:d=0.35","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",segs_raw)]; en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",segs_raw)]
D=107.075875
speech=[]; prev=0.0
for s,e in zip(st,en): speech.append((prev,s)); prev=e
speech.append((prev,D))
lines=open("tools/script.txt",encoding="utf8").read().strip().split("\n")
L=[len(re.sub(r"\s","",l)) for l in lines]
tot_sp=sum(b-a for a,b in speech); tot=sum(L)
# map cumulative char fraction to speech time, then snap each boundary to nearest gap
gaps=[(speech[i][1],speech[i+1][0]) for i in range(len(speech)-1)]
def t_at(frac):
    target=frac*tot_sp; acc=0
    for a,b in speech:
        if acc+(b-a)>=target: return a+(target-acc)
        acc+=b-a
    return D
cum=0; bounds=[speech[0][0]]
for i,l in enumerate(L[:-1]):
    cum+=l; t=t_at(cum/tot)
    g=min(gaps,key=lambda g:abs((g[0]+g[1])/2-t))
    bounds.append(round(g[1],2))
bounds.append(D)
out=[{"i":i+1,"start":bounds[i],"end":bounds[i+1],"text":lines[i]} for i in range(len(lines))]
json.dump({"duration":D,"speech_segments":speech,"lines":out},open("output/timeline_align.json","w"),ensure_ascii=False,indent=1)
for o in out: print(f'{o["i"]:2d} {o["start"]:6.2f}-{o["end"]:6.2f} {o["text"][:40]}')
