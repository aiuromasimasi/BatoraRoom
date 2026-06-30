/**
 * オーバーレイ素材（自前生成・ライセンスクリーン）を作る。
 * Canvas で黒地に「ふんわり玉ボケ＋キラキラ」を描いてループ動画に。
 * 動画プレイヤー側は #ov を mix-blend-mode:screen で重ねるので、黒は透過し光だけ乗る。
 *
 * 使い方: node make_overlay.mjs
 * 出力:  overlays/sparkle.mp4  (1080x1920 / 8秒ループ / 30fps)
 *
 * フリー素材に差し替えたいときは overlays/sparkle.webm か sparkle.mp4 を
 * 好きな素材（Pixabay / Mixkit / Pexels 等のロイヤリティフリー）で置き換えるだけ。
 */
import puppeteer from 'puppeteer';
import { spawn } from 'child_process';
import { mkdirSync, writeFileSync, rmSync, statSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const W = 1080, H = 1920, FPS = 30, SEC = 8;

// 黒地に玉ボケ＋キラキラを描く自己完結HTML（8秒で完全ループ）
const PAGE = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}
</style></head><body><canvas id="c" width="${W}" height="${H}"></canvas><script>
const c=document.getElementById('c'),x=c.getContext('2d'),W=${W},H=${H},SEC=${SEC};
function rnd(s){return ()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};}
const R=rnd(20260630);
const BOKEH=[],COL=['#ffd9ee','#cdeaff','#fff3c4','#d9c2ff','#c6ffe9','#ffffff'];
for(let i=0;i<26;i++){BOKEH.push({x:R(),baseY:R(),r:30+R()*120,col:COL[(R()*COL.length)|0],ph:R(),amp:0.04+R()*0.06,al:0.10+R()*0.22});}
const STAR=[];
for(let i=0;i<40;i++){STAR.push({x:R(),y:R(),s:2+R()*5,ph:R(),sp:1+(R()*3|0)});}
function frame(t){// t:0..1 ループ位相
  x.clearRect(0,0,W,H);x.fillStyle='#000';x.fillRect(0,0,W,H);
  x.globalCompositeOperation='lighter';
  for(const b of BOKEH){
    const prog=(b.baseY - t)% 1; const y=((prog<0?prog+1:prog))*1.2*H - 0.1*H;
    const px=(b.x + Math.sin((t+b.ph)*Math.PI*2)*b.amp)*W;
    const g=x.createRadialGradient(px,y,0,px,y,b.r);
    g.addColorStop(0,b.col);g.addColorStop(.35,b.col);g.addColorStop(1,'rgba(0,0,0,0)');
    x.globalAlpha=b.al*(0.7+0.3*Math.sin((t+b.ph)*Math.PI*2));
    x.fillStyle=g;x.beginPath();x.arc(px,y,b.r,0,7);x.fill();
  }
  for(const s of STAR){
    const tw=0.5+0.5*Math.sin((t*s.sp+s.ph)*Math.PI*2);
    x.globalAlpha=tw*0.9;x.fillStyle='#fff';
    const px=s.x*W,py=s.y*H,r=s.s*(0.6+tw*0.8);
    x.beginPath();x.arc(px,py,r,0,7);x.fill();
    // 十字きらめき
    x.globalAlpha=tw*0.5;x.fillRect(px-r*3,py-0.6,r*6,1.2);x.fillRect(px-0.6,py-r*3,1.2,r*6);
  }
  x.globalAlpha=1;x.globalCompositeOperation='source-over';
}
window.__draw=(t)=>frame(t);
</script></body></html>`;

(async () => {
  mkdirSync(path.join(__dirname, 'overlays'), { recursive: true });
  const tmpDir = path.join(__dirname, `.ov_${Date.now()}`);
  mkdirSync(tmpDir, { recursive: true });

  console.log('overlay生成: ブラウザ起動...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', `--window-size=${W},${H}`, '--force-device-scale-factor=1'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  await page.setContent(PAGE, { waitUntil: 'networkidle0' });

  const total = FPS * SEC;
  console.log(`  ${total} フレーム描画中...`);
  for (let i = 0; i < total; i++) {
    const t = i / total; // 0..1 完全ループ
    await page.evaluate((tt) => window.__draw(tt), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    writeFileSync(path.join(tmpDir, `f${String(i).padStart(5, '0')}.jpg`), buf);
  }
  await browser.close();

  console.log('  ffmpeg エンコード...');
  await new Promise((resolve, reject) => {
    const ff = spawn('ffmpeg', [
      '-y', '-framerate', String(FPS),
      '-i', path.join(tmpDir, 'f%05d.jpg'),
      '-vcodec', 'libx264', '-crf', '20', '-preset', 'slow',
      '-pix_fmt', 'yuv420p',
      path.join(__dirname, 'overlays', 'sparkle.mp4'),
    ], { stdio: ['ignore', 'ignore', 'pipe'] });
    ff.stderr.on('data', () => {});
    ff.on('close', (code) => code === 0 ? resolve() : reject(new Error('ffmpeg ' + code)));
  });
  rmSync(tmpDir, { recursive: true });

  const mb = (statSync(path.join(__dirname, 'overlays', 'sparkle.mp4')).size / 1024 / 1024).toFixed(1);
  console.log(`✓ overlays/sparkle.mp4 (${mb} MB)`);
})().catch(e => { console.error(e); process.exit(1); });
