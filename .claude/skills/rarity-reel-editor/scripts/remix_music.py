import json,re,subprocess,sys,os,importlib.util
S=sys.argv[1]; W=sys.argv[2]; LUFS=float(sys.argv[3])
sys.path.insert(0,S+"/scripts")
def load(n):
    spec=importlib.util.spec_from_file_location(n,f"{S}/scripts/{n}.py"); m=importlib.util.module_from_spec(spec); sys.modules[n]=m; spec.loader.exec_module(m); return m
bvr=load("build_voiceover_reel")
import motion_graphics as mg, ad_graphics as ag
from pathlib import Path
cfg={"01":("deep-house-196.mp3",18),"02":("deep-house-196.mp3",18),"03":("deep-urban-623.mp3",10)}
for n,(mus,start) in cfg.items():
    log=open(f"{W}/v3_{n}.log").read(); T=re.search(r"\[keep-temp\] (\S+)",log).group(1)
    r=json.load(open(f"{W}/v3_{n}.remapped.json")); total=r["total"]
    sfx=[]
    for b in r["beats"]:
        sfx.append((b["start"]+0.02,"pop",-23))
        if b["type"]=="checklist":
            for k,v in b.get("anchors",{}).items():
                if k.startswith("r") and v>b["start"]+0.1: sfx.append((v+0.02,"pop",-25))
    mixed=Path(T)/"mix2.wav"
    bvr.mix_audio(Path(T)/"voice.wav", mixed, total, Path(T), music=f"{S}/music/{mus}", music_start=start, music_lufs=LUFS, sfx_events=sfx, voice_fx=True)
    inputs=["-i",f"{T}/base.mp4","-i",str(mixed),"-i",f"{T}/caps/caption_track.mov","-i",f"{T}/mg.mov"]
    chain=f"[0:v][2:v]overlay=0:0[a];[a][3:v]overlay=0:{mg.ZONE_Y0}[b]"; last,nxt="b",5
    if os.path.exists(f"{T}/mg_top.mov"):
        inputs+=["-i",f"{T}/mg_top.mov"]; chain+=f";[{last}][{nxt-1}:v]overlay=0:{ag.TOP_Y0}[t]"; last,nxt="t",nxt+1
    inputs+=["-i",f"{S}/../rarity-ig-designer/assets/rarity-symbol-white.png"]; chain+=f";[{nxt-1}:v]scale=64:-1[sym];[{last}][sym]overlay=W-w-40:40[c]"
    inputs+=["-i",f"{T}/progress.mov"]; chain+=f";[c][{nxt}:v]overlay=0:101[outv]"
    out=f"{W}/v4_{n}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",chain,"-map","[outv]","-map","1:a","-c:v","libx264","-preset","slow","-crf","21","-maxrate","14M","-bufsize","28M","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-movflags","+faststart","-shortest",out],check=True)
    print(n,"remixed ->",out)
