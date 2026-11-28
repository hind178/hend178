from render_animatic import *
import render_animatic as r
r.W,r.H=1080,1920
shot=(0,5,'university_clean',[('Hind','standing',.23,.83,.37,'idle'),('Loreen','standing',.51,.83,.40,'idle'),('Lizette','standing',.80,.83,.36,'idle')],'Identity and edge test')
output=P/'Episode01_Identity_Test_v3.mp4'
cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-threads','4','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(150):
 im=frame(shot,n/30)
 if n==75:im.save(P/'Episode01_Identity_Test_v3.jpg',quality=95)
 proc.stdin.write(im.tobytes())
proc.stdin.close(); assert proc.wait()==0
