import subprocess, os, textwrap
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPS=30; X=0.5
# (source, seconds, caption)
S=[("PHOTO", 4.0, "We're 628 Aerospace,\nand this is Flare AI."),
   ("s_overview.png", 4.5, "NASA's space-fire experiments: 24 investigations,\n537 tests, in one place."),
   ("s_moon.png", 4.0, "Rank them for a spacecraft,\na Moon base or Mars."),
   ("cmp1.png", 4.5, "Compare tests like with like,\nor it refuses and explains why."),
   ("s_record.png", 4.5, "Every number cites NASA,\nand we checked all 537 by hand."),
   ("s_lab.png", 5.0, "Our SI answers only from NASA's records,\nor says the data isn't there."),
   ("s_scen2.png", 4.5, "On the Moon and Mars, knowing what's never\nbeen tested could save a crew."),
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
    draw.append(f"drawtext=fontfile={R}:text='Edited with SI (Claude)':fontsize=22:fontcolor=white@0.7:x=w-tw-28:y=h-44")
    if src=="PHOTO":
        t1=txt("t1.txt","Flare AI"); t2=txt("t2.txt","628 Aerospace  ·  NASA Space Apps 2026  ·  Flame in Freefall")
        t3=txt("t3.txt","Photo: NASA, BASS-II flame test on the ISS, Expedition 40 (iss040e088023)")
        # 4K NASA photo: crop to 16:9, then a slow push-in with a gentle drift; darkened a little so the title reads
        vf=("crop=3840:2160:0:(ih-2160)/2,"
            f"zoompan=z='1+0.08*on/{n}':x='(iw-iw/zoom)*(0.35+0.3*on/{n})':y='(ih-ih/zoom)/2':d={n}:s=1920x1080:fps={FPS},"
            "eq=brightness=-0.06:saturation=1.1,"
            f"drawtext=fontfile={B}:textfile={t1}:fontsize=120:fontcolor=white:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-tw)/2:y=170:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t2}:fontsize=34:fontcolor=white:shadowcolor=black@0.7:shadowx=2:shadowy=2:x=(w-tw)/2:y=320:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t3}:fontsize=22:fontcolor=white@0.8:x=28:y=24,"
            f"drawbox=x=0:y=880:w=1920:h=200:color=0x0b0b0b@0.85:t=fill,"+",".join(draw))
        cmd=["ffmpeg","-y","-loglevel","error","-loop","1","-i","bass2-flame-3840.jpg","-vf",vf+",format=yuv420p","-frames:v",str(n),"-c:v","libx264","-crf","16","-preset","medium",out]
    elif src=="JELLY":
        t1=txt("t1.txt","Flare AI"); t2=txt("t2.txt","628 Aerospace  ·  NASA Space Apps 2026  ·  Flame in Freefall")
        t3=txt("t3.txt","Footage: Science@NASA / NASA Goddard (SVS 11640)")
        vf=("scale=1920:-2,crop=1920:1080,"
            f"drawtext=fontfile={B}:textfile={t1}:fontsize=120:fontcolor=white:x=(w-tw)/2:y=170:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t2}:fontsize=34:fontcolor=white@0.9:x=(w-tw)/2:y=320:alpha='min(1,t/0.8)',"
            f"drawtext=fontfile={R}:textfile={t3}:fontsize=22:fontcolor=white@0.75:x=28:y=24,"+",".join(draw))
        cmd=["ffmpeg","-y","-loglevel","error","-ss","20","-t",str(d),"-i","/home/user/flare-ai/site/media/jelly-loop.mp4","-vf",vf+f",fps={FPS},format=yuv420p","-an","-c:v","libx264","-crf","18","-preset","medium",out]
    elif src=="END":
        a=txt("e1.txt","Flare AI"); b=txt("e2.txt","What NASA's fire experiments prove, and where the data stops."); c=txt("e3.txt","github.com/aaa628/flare-ai")
        vf=(f"drawtext=fontfile={B}:textfile={a}:fontsize=110:fontcolor=white:x=(w-tw)/2:y=360,"
            f"drawtext=fontfile={R}:textfile={b}:fontsize=38:fontcolor=white@0.9:x=(w-tw)/2:y=520,"
            f"drawtext=fontfile={B}:textfile={c}:fontsize=40:fontcolor=0xE0405A:x=(w-tw)/2:y=620,"+draw[-1])
        cmd=["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"color=c=0x0b0b0b:s=1920x1080:d={d}:r={FPS}","-vf",vf+",format=yuv420p","-c:v","libx264","-crf","18",out]
    else:
        # fit image into 1920x1080 on a dark background, then a slow push-in (Ken Burns)
        # screenshot in the top 880 px with a slow push-in; captions get their own band below, so nothing is covered
        vf=("scale=1840:860:force_original_aspect_ratio=decrease,pad=1920:880:(ow-iw)/2:(oh-ih)/2+10:color=0x0b0b0b,"
            "scale=3840:1760,"
            f"zoompan=z='1+0.04*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1920x880:fps={FPS},"
            "pad=1920:1080:0:0:color=0x0b0b0b,"+",".join(draw))
        cmd=["ffmpeg","-y","-loglevel","error","-loop","1","-i",src,"-vf",vf+",format=yuv420p","-frames:v",str(n),"-c:v","libx264","-crf","18","-preset","medium",out]
    subprocess.run(cmd,check=True); clips.append((out,d))
# crossfade chain
inputs=[]; [inputs.extend(["-i",c]) for c,_ in clips]
f=[]; prev="[0:v]"; t=0
for i in range(1,len(clips)):
    t+=clips[i-1][1]-X
    lab=f"[v{i}]"; f.append(f"{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={t:.3f}{lab}"); prev=lab
subprocess.run(["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",";".join(f),"-map",prev,"-c:v","libx264","-crf","18","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart","flare-ai-demo-silent.mp4"],check=True)
# SRT with the same timings
def ts(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h:02}:{m:02}:{int(s):02},{int(round((s%1)*1000)):03}"
srt=[]; t=0
for i,(src,d,cap) in enumerate(S):
    if cap: srt.append(f"{len(srt)+1}\n{ts(t+0.1)} --> {ts(t+d-X)}\n{cap}\n")
    t+=d-X
open("flare-ai-demo.srt","w").write("\n".join(srt))
