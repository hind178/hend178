import sys,glob
from PIL import Image, ImageDraw
fs=sorted(glob.glob('build/stills/*.jpg')); sel=[f for f in fs if any(('t%06.2f'%float(x)) in f for x in sys.argv[2:])] if len(sys.argv)>2 else fs
cols=6; w,h=270,480
rows=(len(sel)+cols-1)//cols
S=Image.new('RGB',(cols*w,rows*h),'black'); d=ImageDraw.Draw(S)
for i,f in enumerate(sel):
    im=Image.open(f).resize((w,h)); S.paste(im,((i%cols)*w,(i//cols)*h)); d.text(((i%cols)*w+6,(i//cols)*h+6),f.split('/')[-1][1:-4],fill='yellow')
S.save(sys.argv[1]); print(len(sel))
