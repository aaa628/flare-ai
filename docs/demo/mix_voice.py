"""Puts the narrator's recording on the silent video, one line per scene (used for flare-ai-demo.mp4).
Line boundaries were found from the pauses in the recording (ffmpeg silencedetect at -30 dB / 0.18 s).
The recording ran 35 s, so only the 7 script lines are used; the last ~5 s after line 7 are left out."""
import subprocess
segs=[(1.06,3.95),(4.56,9.16),(9.47,12.29),(12.40,15.95),(16.23,20.37),(20.55,24.74),(25.01,29.35)]  # seconds in voice.ogg
d=[3.49,5.20,3.42,4.15,4.74,4.79,4.94,2.0]; X=0.5   # scene lengths in build.py, crossfade
t=[0]
for x in d[:-1]: t.append(t[-1]+x-X)
starts=[0.3]+[ti+0.2 for ti in t[1:len(segs)]]
f=[f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={b-a-0.08:.3f}:d=0.08,adelay={int(starts[i]*1000)}:all=1[a{i}]" for i,(a,b) in enumerate(segs)]
f.append("".join(f"[a{i}]" for i in range(len(segs)))+f"amix=inputs={len(segs)}:normalize=0,highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:29.233[out]")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","voice.ogg","-filter_complex",";".join(f),"-map","[out]","-ar","48000","-ac","2","-c:a","pcm_s16le","voice_timed.wav"],check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","flare-ai-demo-silent.mp4","-i","voice_timed.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart","flare-ai-demo.mp4"],check=True)
