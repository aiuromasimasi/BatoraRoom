import json, urllib.request, ssl, os, subprocess
UA={"User-Agent":"Mozilla/5.0"}
CTX=ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
def getj(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30,context=CTX) as r:
        return json.load(r)
KNOWN = {
 132: (939520, "HELLGATE: London"),
 137: (3023190, "みんなで推理"),
 140: (550, "Left 4 Dead 2"),
 141: (41014, "Serious Sam HD: The Second Encounter"),
 143: (582500, "We Were Here"),
 144: (1801110, "違う冬のぼくら(BOKURA)"),
 145: (2023000, "Batsugun"),
 148: (620, "Portal 2"),
}
os.makedirs("game_trailers", exist_ok=True)
index = json.load(open("game_trailers/index.json")) if os.path.exists("game_trailers/index.json") else {}
for cid,(appid,name) in KNOWN.items():
    if str(cid) in index:
        print(f"c{cid}: SKIP(済)", flush=True); continue
    try:
        ad = getj(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=jp&l=japanese")
        data = (ad.get(str(appid)) or {}).get("data") or {}
        movies = (data.get("movies") or [])[:5]
        ent = {"appid":appid,"game":data.get("name",name),"movies":[]}
        for i,mv in enumerate(movies):
            f_ = f"game_trailers/c{cid}_t{i}.mp4"
            if os.path.exists(f_) and os.path.getsize(f_) > 30000:
                p = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f_],capture_output=True,text=True)
                dur = round(float(p.stdout.strip() or 0))
                ent["movies"].append({"i":i,"name":mv.get("name",f"トレーラー{i+1}"),"file":f_,"dur":dur})
                print(f"c{cid} t{i}: 既存流用 {dur}s", flush=True)
                continue
            stream = mv.get("hls_h264") or mv.get("dash_h264")
            if not stream: continue
            rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",stream,
                                 "-vf","scale=-2:360","-c:v","libx264","-preset","veryfast","-crf","30",
                                 "-c:a","aac","-b:a","64k","-pix_fmt","yuv420p",f_],
                                capture_output=True, timeout=180)
            if rr.returncode!=0 or not os.path.exists(f_) or os.path.getsize(f_)<30000:
                if os.path.exists(f_): os.remove(f_)
                print(f"c{cid} t{i}: DL失敗", flush=True); continue
            p = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f_],capture_output=True,text=True)
            dur = round(float(p.stdout.strip() or 0))
            ent["movies"].append({"i":i,"name":mv.get("name",f"トレーラー{i+1}"),"file":f_,"dur":dur})
            print(f"c{cid} t{i}: OK {dur}s", flush=True)
        if ent["movies"]:
            index[str(cid)] = ent
            json.dump(index, open("game_trailers/index.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"c{cid} {ent['game']}: {len(ent['movies'])}本 保存", flush=True)
    except Exception as e:
        print(f"c{cid}: ERR {type(e).__name__} {e}", flush=True)
print("done, total entries:", len(index))
