import subprocess, os, textwrap
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPS=30; X=0.5
from PIL import Image
def motion(base, n, zoom, drift_x, out_w, out_h, vf, out, crf="18"):
    """base: PIL image already at the framing we want (aspect out_w:out_h, any size >= 2x). Smooth push-in with float
    precision (no whole-pixel steps, so no shake); ease-in-out so the motion starts and ends gently."""
    W,H=base.size
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{out_w}x{out_h}","-r",str(FPS),"-i","-",
                        "-vf",vf+",format=yuv420p","-c:v","libx264","-crf",crf,"-preset","medium",out],stdin=subprocess.PIPE)
    for f in range(n):
        u=f/max(1,n-1); e=u*u*(3-2*u)            # smoothstep easing
        z=1+zoom*e                                 # zoom factor
        vw,vh=W/z,H/z                              # visible window in source pixels (float)
        cx=W/2+drift_x*W*(e-0.5); cy=H/2
        x0=min(max(cx-vw/2,0),W-vw); y0=min(max(cy-vh/2,0),H-vh)
        sx=vw/out_w; sy=vh/out_h
        fr=base.transform((out_w,out_h),Image.AFFINE,(sx,0,x0,0,sy,y0),resample=Image.BICUBIC)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); assert p.wait()==0

# (source, seconds, caption)
S=[("PHOTO", 3.6, "We are 628 Aerospace,\nand this is Flare AI."),
   ("s_overview.png", 4.7, "NASA's microgravity combustion research: 24 investigations\nand 537 experimental trials, consolidated into one resource."),
   ("s_moon.png", 4.3, "Investigations are ranked by their relevance to spacecraft,\nlunar habitats and Martian outposts."),
   ("cmp1.png", 4.6, "Comparisons are drawn only between commensurable data;\nincompatible requests are declined, with reasons given."),
   ("s_record.png", 4.4, "Every value is traceable to its NASA source,\nand all 537 records were verified by hand."),
   ("s_lab.png", 4.6, "Our SI responds exclusively from NASA's records\nand acknowledges when the evidence is insufficient."),
   ("s_scen2.png", 4.8, "For lunar and Martian missions, identifying what remains\nuntested may prove decisive for crew safety."),
   ("END", 2.0, "")]
def esc(p): return p.replace(":", "\\:")
def txt(name, s):
    open(name,"w").write(s); return name
clips=[]
for i,(src,d,cap) in enumerate(S):
    out=f"c{i}.mp4"; n=int(d*FPS)
    capf=txt(f"cap{i}.txt",cap) if cap else None
    draw=[]
    if cap:
        lines=cap.split("\n"); y0=1080-200+ (200-len(lines)*58)//2
        for k,l in enumerate(lines):
            lf=txt(f"cap{i}_{k}.txt",l)
            draw.append(f"drawtext=fontfile={B}:textfile={lf}:fontsize=44:fontcolor=white:x=(w-tw)/2:y={y0+k*58}")
    draw.append(f"drawtext=fontfile={R}:text='Edited with SI':fontsize=22:fontcolor=white@0.7:x=w-tw-28:y=h-44")
    if src=="PHOTO":
        t1=txt("t1.txt","Flare AI"); t2=txt("t2.txt","628 Aerospace  ·  NASA Space Apps 2026  ·  Flame in Freefall")
        t3=txt("t3.txt","Photo: NASA, BASS-II flame test on the ISS, Expedition 40 (iss040e088023)")
        # 4K NASA photo: crop to 16:9, then a slow push-in with a gentle drift; darkened a little so the title reads
        vf=("eq=brightness=-0.06:saturation=1.1,"
            f"drawtext=fontfile={B}:textfile={t1}:fontsize=120:fontcolor=white:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-tw)/2:y=170:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t2}:fontsize=34:fontcolor=white:shadowcolor=black@0.7:shadowx=2:shadowy=2:x=(w-tw)/2:y=320:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t3}:fontsize=22:fontcolor=white@0.8:x=28:y=24,"
            f"drawbox=x=0:y=880:w=1920:h=200:color=0x0b0b0b@0.85:t=fill,"+",".join(draw))
        im=Image.open("bass2-flame-3840.jpg").convert("RGB"); top=(im.height-2160)//2
        motion(im.crop((0,top,3840,top+2160)), n, 0.08, 0.06, 1920, 1080, vf, out, crf="16")
        clips.append((out,d)); continue
    elif src=="JELLY":
        t1=txt("t1.txt","Flare AI"); t2=txt("t2.txt","628 Aerospace  ·  NASA Space Apps 2026  ·  Flame in Freefall")
        t3=txt("t3.txt","Footage: Science@NASA / NASA Goddard (SVS 11640)")
        vf=("scale=1920:-2,crop=1920:1080,"
            f"drawtext=fontfile={B}:textfile={t1}:fontsize=120:fontcolor=white:x=(w-tw)/2:y=170:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t2}:fontsize=34:fontcolor=white@0.9:x=(w-tw)/2:y=320:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t3}:fontsize=22:fontcolor=white@0.75:x=28:y=24,"+",".join(draw))
        cmd=["ffmpeg","-y","-loglevel","error","-ss","20","-t",str(d),"-i","/home/user/flare-ai/site/media/jelly-loop.mp4","-vf",vf+f",fps={FPS},format=yuv420p","-an","-c:v","libx264","-crf","18","-preset","medium",out]
    elif src=="END":
        a=txt("e1.txt","Flare AI"); b=txt("e2.txt","What NASA's fire experiments prove, and where the data stops."); c=txt("e3.txt","flare-ai-628-by-628aerospace.netlify.app")
        vf=(f"drawtext=fontfile={B}:textfile={a}:fontsize=110:fontcolor=white:x=(w-tw)/2:y=360,"
            f"drawtext=fontfile={R}:textfile={b}:fontsize=38:fontcolor=white@0.9:x=(w-tw)/2:y=520,"
            f"drawtext=fontfile={B}:textfile={c}:fontsize=40:fontcolor=0xE0405A:x=(w-tw)/2:y=620,"+draw[-1])
        cmd=["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"color=c=0x0b0b0b:s=1920x1080:d={d}:r={FPS}","-vf",vf+",format=yuv420p","-c:v","libx264","-crf","18",out]
    else:
        # fit image into 1920x1080 on a dark background, then a slow push-in (Ken Burns)
        # screenshot in the top 880 px with a smooth push-in; captions get their own band below, so nothing is covered
        im=Image.open(src).convert("RGB"); bw,bh=3840,1760
        r=min((1840*2)/im.width,(860*2)/im.height); im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
        canvas=Image.new("RGB",(bw,bh),(11,11,11)); canvas.paste(im,((bw-im.width)//2,(bh-im.height)//2+20))
        motion(canvas, n, 0.04, 0.0, 1920, 880, "pad=1920:1080:0:0:color=0x0b0b0b,"+",".join(draw), out)
        clips.append((out,d)); continue
    subprocess.run(cmd,check=True); clips.append((out,d))
# crossfade chain
inputs=[]; [inputs.extend(["-i",c]) for c,_ in clips]
f=[]; prev="[0:v]"; t=0
for i in range(1,len(clips)):
    t+=clips[i-1][1]-X
    lab=f"[v{i}]"; f.append(f"{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={t:.3f}{lab}"); prev=lab
subprocess.run(["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",";".join(f),"-map",prev,"-c:v","libx264","-crf","18","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart","flare-ai-demo-formal.mp4"],check=True)
# SRT with the same timings
def ts(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h:02}:{m:02}:{int(s):02},{int(round((s%1)*1000)):03}"
srt=[]; t=0
for i,(src,d,cap) in enumerate(S):
    if cap: srt.append(f"{len(srt)+1}\n{ts(t+0.1)} --> {ts(t+d-X)}\n{cap}\n")
    t+=d-X
open("flare-ai-demo-formal.srt","w").write("\n".join(srt))
