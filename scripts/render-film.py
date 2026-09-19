"""Render the silent initiative film. Run from repository root with Pillow and ffmpeg.
The reviewed src/film.json provides timing, captions, and public-facing copy.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'public/media';OUT.mkdir(exist_ok=True)
FONTS=ROOT/'public/fonts'
regular=lambda size:ImageFont.truetype(str(FONTS/'font-2.ttf'),size)
serif=lambda size:ImageFont.truetype(str(FONTS/'font-0.ttf'),size)
bold=lambda size:ImageFont.truetype(str(FONTS/'font-4.ttf'),size)
navy='#002755';blue='#002F6D';gold='#FFB600'
scenes=json.loads((ROOT/'src/film.json').read_text())
logo=Image.open(ROOT/'public/brand/cccco-logo.png').convert('RGBA');logo.thumbnail((800,90))
def wrap(text,font,width):
 lines=[]
 for para in text.split('\n'):
  line=''
  for word in para.split():
   trial=f'{line} {word}'.strip()
   if font.getlength(trial)>width and line:lines.append(line);line=word
   else:line=trial
  lines.append(line)
 return lines
def block(d,text,xy,font,fill,width,spacing=1.18):
 x,y=xy
 for line in wrap(text,font,width):d.text((x,y),line,font=font,fill=fill);y+=int(font.size*spacing)
 return y
def timestamp(t):return f'{t//3600:02d}:{t//60%60:02d}:{t%60:02d}.000'
def art(d,motif):
 cx,cy=1550,590
 if motif in ('opportunity','pathways'):
  for i in range(5):
   x=1355+i*37;y=315+i*36
   d.rounded_rectangle((x,y,1810-i*37,860-i*12),radius=110-i*18,outline=gold if i==4 else '#315579',width=4 if i==4 else 2)
  d.line((1300,862,1860,862),fill='#416084',width=2)
 elif motif=='growth':
  for y in (400,550,700,850):d.line((1280,y,1840,y),fill='#24486e',width=2)
  pts=[(1300,820),(1430,720),(1555,620),(1690,470),(1810,340)]
  d.line(pts,fill=gold,width=6)
  for x,y in pts:d.ellipse((x-17,y-17,x+17,y+17),fill=gold)
 else:
  for j in range(8):
   a=math.pi*2*j/8;x=cx+210*math.cos(a);y=cy+210*math.sin(a)
   d.line((cx,cy,x,y),fill='#416084',width=3)
   d.ellipse((x-37,y-37,x+37,y+37),fill=blue,outline=gold if j%3==0 else '#416084',width=3)
  d.ellipse((cx-83,cy-83,cx+83,cy+83),fill=gold)
  d.text((cx,cy),'EEO',font=bold(38),fill=navy,anchor='mm')
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);segments=[];captions=['WEBVTT',''];elapsed=0
 for idx,scene in enumerate(scenes):
  im=Image.new('RGB',(1920,1080),navy);d=ImageDraw.Draw(im)
  d.rectangle((0,0,1920,154),fill='white');im.paste(logo,(100,(154-logo.height)//2),logo)
  d.rectangle((0,154,1920,160),fill=gold);d.text((1450,66),'EEO IBP INITIATIVE',font=bold(24),fill=navy)
  d.text((100,235),scene['label'],font=bold(25),fill=gold)
  if 'districts' in scene:
   d.text((96,286),scene['title'],font=serif(66),fill='white')
   for j,g in enumerate(scene['districts']):
    y=402+j*172
    d.line((100,y,1820,y),fill='#416084',width=2)
    d.text((102,y+33),g['name'],font=serif(44),fill='white')
    block(d,g['description'],(965,y+29),regular(31),'#e4edf7',825,1.3)
   d.text((100,940),'11 PARTICIPATING DISTRICTS · A SHARED COMMITMENT TO OPPORTUNITY',font=bold(20),fill=gold)
  else:
   end=block(d,scene['title'],(96,345),serif(98),'white',1110,1.04)
   d.rectangle((100,end+36,190,end+41),fill=gold)
   block(d,scene['description'],(100,end+83),regular(36),'#e4edf7',1030,1.32)
   art(d,scene['motif'])
  d.line((100,982,1820,982),fill='#416084',width=2)
  d.text((100,1008),'EQUAL EMPLOYMENT OPPORTUNITY · INNOVATIVE BEST PRACTICES',font=bold(19),fill='#c6d7e8')
  d.text((1820,1008),f'{idx+1:02d} / {len(scenes):02d}',font=regular(21),fill='#c6d7e8',anchor='ra')
  f=tmp/f'{idx:02d}.png';im.save(f)
  if idx==0:im.save(OUT/'eeo-poster.jpg',quality=94)
  if idx in (0,5,6,8,12):im.save(f'/tmp/eeo-final-frame-{idx}.png')
  duration=scene['duration'];segment=tmp/f'{idx:02d}.mp4'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-i',str(f),'-t',str(duration),'-vf',f"fade=t=in:st=0:d=0.35:color=0x002755,fade=t=out:st={duration-.35}:d=0.35:color=0x002755",'-r','30','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-threads','2',str(segment)],check=True)
  segments.append(segment)
  captions += [f'{timestamp(elapsed)} --> {timestamp(elapsed+duration)}',scene['title'].replace('\n',' '),scene['description'].replace('\n',' '),''];elapsed+=duration
  print(f'Rendered scene {idx+1}/{len(scenes)}',flush=True)
 concat=tmp/'concat.txt';concat.write_text('\n'.join(f"file '{f}'" for f in segments))
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(OUT/'eeo-initiative.mp4')],check=True)
 (OUT/'eeo-initiative.en.vtt').write_text('\n'.join(captions))
 print('MP4 complete',flush=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(OUT/'eeo-initiative.mp4'),'-c:v','libvpx-vp9','-crf','36','-b:v','0','-deadline','good','-cpu-used','5','-threads','4',str(OUT/'eeo-initiative.webm')],check=True)
print('Film complete:',elapsed,'seconds',flush=True)
