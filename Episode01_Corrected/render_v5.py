from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFilter
import subprocess, math, json, functools
P=Path(__file__).resolve().parent
W,H=540,960; FPS=15
# x and y are normalized ground anchors; h is fraction of canvas height.
# The editorial timings are approximate, not a verified transcript alignment.
shots=[
(0,10,'university_clean',[('Hind','standing',.43,.83,.39,'idle')],'Hind expects to be alone'),
(10,16,'computer_lab_clean',[],'Institute studies'),
(16,23,'institute_clean',[('Hind','standing',.34,.82,.37,'walk')],'Institute to university'),
(23,35,'computer_lab_clean',[],'Trip announcement and disappointment'),
(35,48,'campus_walk_clean',[('Loreen','standing',.34,.83,.40,'walk'),('Lizette','standing',.66,.83,.37,'walk')],'Loreen and Lizette friendship'),
(48,60,'campus_garden_clean',[('Hind','standing',.20,.85,.37,'idle'),('Loreen','standing',.60,.79,.34,'idle'),('Lizette','standing',.82,.79,.32,'idle')],'Hind is a classmate'),
(60,70,'university_clean',[('Hind','standing',.28,.84,.38,'walk'),('Loreen','standing',.63,.81,.38,'idle'),('Lizette','standing',.82,.81,.35,'idle')],'Arrival at the gate'),
(70,80,'university_clean',[('Hind','standing',.25,.84,.40,'idle'),('Loreen','greeting',.53,.84,.43,'idle'),('Lizette','greeting',.78,.84,.38,'idle')],'Loreen welcomes Hind'),
(80,86,'bus_interior_clean',[('Hind','standing',.30,.65,.27,'portrait'),('Loreen','talking',.60,.65,.29,'portrait')],'Bus seating proposal, close-up staging'),
(86,91,'bus_interior_clean',[('Hind','standing',.30,.65,.27,'portrait'),('Lizette','standing',.60,.65,.27,'portrait')],'Seat rotation'),
(91,100,'bus_interior_clean',[('Hind','talking',.30,.65,.27,'portrait'),('Loreen','standing',.60,.65,.29,'portrait')],'Loreen refuses to leave Hind alone'),
(100,103,'hotel_exterior_clean',[],'Journey transition'),
(103,107.075875,'hotel_lobby_clean',[('Hind','standing',.27,.71,.30,'idle'),('Loreen','standing',.51,.71,.33,'idle'),('Lizette','standing',.75,.71,.29,'idle')],'Hotel arrival cliffhanger')]
@functools.lru_cache(None)
def bg(name):
 im=Image.open(P/'backgrounds'/f'{name}.png').convert('RGB'); return ImageOps.fit(im,(W,H),Image.Resampling.LANCZOS)
@functools.lru_cache(None)
def sprite(c,pose,h,walk=0,portrait=False):
 path=P/'characters'/c/'cleaned_original.png' # identity lock; no unverified pose substitution
 im=Image.open(path).convert('RGBA'); im=im.crop(im.getbbox());
 if portrait: im=im.crop((0,0,im.width,round(im.height*.43)))
 return im.resize((round(im.width*h/im.height),h),Image.Resampling.LANCZOS)
def frame(shot,t):
 start,end,name,actors,_=shot; q=(t-start)/(end-start); canvas=bg(name).copy().convert('RGBA'); shadow=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(shadow); layers=[]
 for i,(c,pose,x,y,h,mode) in enumerate(actors):
  walking=False; portrait=mode=='portrait'; dx=(q-.5)*.16 if walking else 0; xx=round((x+dx)*W); yy=round(y*H); hh=round(h*H); a=sprite(c,pose,hh,1+int((t-start)*8)%8 if walking else 0,portrait)
  a=a.rotate(.35*math.sin((t-start)*1.8+i*1.7),Image.Resampling.BICUBIC,expand=True)
  if not portrait: d.ellipse((xx-hh*.12,yy-5,xx+hh*.12,yy+6),fill=(40,28,20,90))
  layers.append((yy,a,xx))
 canvas=Image.alpha_composite(canvas,shadow.filter(ImageFilter.GaussianBlur(5)))
 for yy,a,xx in sorted(layers,key=lambda z:z[0]):canvas.alpha_composite(a,(xx-a.width//2,yy-a.height))
 z=1+.045*q; cw,ch=round(W/z),round(H/z); left=(W-cw)//2; top=round((H-ch)*.65); canvas=canvas.crop((left,top,left+cw,top+ch)).resize((W,H),Image.Resampling.BILINEAR)
 # end on a suspenseful fade, no reveal
 if start==103 and q>.75: canvas=Image.blend(canvas,Image.new('RGBA',(W,H),'#151319'),min(.75,(q-.75)*3))
 return canvas.convert('RGB')
if __name__=='__main__':
 duration=107.075875
 (P/'shot_plan.json').write_text(json.dumps({'status':'approximate editorial timing; verify Arabic narration before final','shots':[{'start':a,'end':b,'background':c,'actors':d,'event':e} for a,b,c,d,e in shots]},indent=2))
 previews=P/'shot_previews';previews.mkdir(exist_ok=True)
 for i,s in enumerate(shots): frame(s,(s[0]+s[1])/2).save(previews/f'{i+1:02}.jpg',quality=92)
 cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'audio/narration.mp3'),'-vf','scale=1080:1920:flags=bilinear,fps=30','-c:v','libx264','-threads','4','-preset','ultrafast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',str(duration),'-movflags','+faststart',str(P.parent/'Episode01_V5_Animatic.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE); j=0
 for n in range(math.ceil(duration*FPS)):
  t=n/FPS
  while j+1<len(shots) and t>=shots[j][1]:j+=1
  proc.stdin.write(frame(shots[j],t).tobytes())
 proc.stdin.close(); assert proc.wait()==0
