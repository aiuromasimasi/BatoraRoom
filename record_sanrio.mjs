/**
 * sanrio_movie.html を Puppeteer でヘッドレス録画 → ffmpeg で MP4 化
 *
 * 使い方:
 *   node record_sanrio.mjs                        # 全4本
 *   node record_sanrio.mjs standard fast          # 個別指定
 *   node record_sanrio.mjs standard60 fast60      # 60fps 版
 *
 * 出力:
 *   sanrio_standard.mp4 / sanrio_fast.mp4         (30fps)
 *   sanrio_standard_60fps.mp4 / sanrio_fast_60fps.mp4 (60fps)
 *
 * 事前: npm install puppeteer  （初回のみ。Chromium を自動ダウンロード）
 */
import puppeteer from 'puppeteer';
import { spawn }  from 'child_process';
import { mkdirSync, writeFileSync, rmSync, statSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const URL  = 'http://localhost:8141/sanrio_movie.html';
const W    = 1080;
const H    = 1920;
// ブラウザプレビューと同じ比率にするため、logical 540×960 で描画 (DSF=2 → 物理 1080×1920)
const LW   = 540;
const LH   = 960;

//  speed       : mult 値（1=標準 / 0.6=速い）
//  durationSec : 録画待機秒（映像尺 + バッファ）
//  fps         : 出力フレームレート
//  everyNth    : CDP screencast 間引き（1=毎フレーム≒60fps取得 / 2=隔フレーム≒30fps取得）
const MODES = {
  standard:   { speed: 1,   durationSec: 190, fps: 30, everyNth: 2, out: 'sanrio_standard.mp4',       label: '標準/30fps' },
  fast:       { speed: 0.6, durationSec: 115, fps: 30, everyNth: 2, out: 'sanrio_fast.mp4',           label: '速い/30fps' },
  standard60: { speed: 1,   durationSec: 190, fps: 60, everyNth: 1, out: 'sanrio_standard_60fps.mp4', label: '標準/60fps' },
  fast60:     { speed: 0.6, durationSec: 115, fps: 60, everyNth: 1, out: 'sanrio_fast_60fps.mp4',     label: '速い/60fps' },
};

async function record({ speed, durationSec, fps, everyNth, out, label }) {
  const tmpDir = path.join(__dirname, `.rec_${Date.now()}`);
  mkdirSync(tmpDir, { recursive: true });

  console.log(`\n━━━ ${label} ━━━`);
  console.log('  ブラウザ起動中...');

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      `--window-size=${W},${H}`,
      '--disable-dev-shm-usage',
      `--force-device-scale-factor=2`,
    ],
  });

  const page = await browser.newPage();
  // logical 540×960 (DSF=2) → 物理 1080×1920。ブラウザプレビューと同じ cqw スケール
  await page.setViewport({ width: LW, height: LH, deviceScaleFactor: 2 });

  console.log('  ページ読み込み中...');
  await page.goto(URL, { waitUntil: 'networkidle2', timeout: 30000 });

  // コントロール非表示・フレームを viewport いっぱいに（flex を解除して fixed fill）
  await page.addStyleTag({ content: `
    html,body{width:100%;height:100%;margin:0;padding:0!important;gap:0!important;
              background:#000!important;overflow:hidden!important;display:block!important}
    #frame{position:fixed!important;inset:0!important;
           width:100%!important;height:100%!important;
           border-radius:0!important;border:none!important;box-shadow:none!important}
    .ctl,.hint,#pbar{display:none!important}
  ` });

  // 速度設定 & オーバーレイ素材ON & 最初から再生
  await page.evaluate((s) => {
    clearPending();
    mult = s;
    buildSteps();
    const ovb = document.getElementById('ovb');
    if (ovb && !document.getElementById('ov').classList.contains('on')) ovb.click();
    si = 0;
    playing = true;
    step();
  }, speed);

  // CDP スクリーンキャスト開始
  const client = await page.createCDPSession();
  const frames = [];
  let capturing = true;

  client.on('Page.screencastFrame', async (event) => {
    if (!capturing) return;
    const fn = path.join(tmpDir, `f${String(frames.length).padStart(6, '0')}.jpg`);
    writeFileSync(fn, Buffer.from(event.data, 'base64'));
    frames.push({ path: fn, ts: event.metadata.timestamp });
    await client.send('Page.screencastFrameAck', { sessionId: event.sessionId }).catch(() => {});
  });

  await client.send('Page.startScreencast', {
    format: 'jpeg',
    quality: 88,
    maxWidth: W,
    maxHeight: H,
    everyNthFrame: everyNth,
  });

  console.log(`  録画中... (${durationSec}秒待機)`);
  process.stdout.write('  [');
  const TICK = durationSec / 40;
  for (let i = 0; i < 40; i++) {
    await new Promise(r => setTimeout(r, TICK * 1000));
    process.stdout.write('█');
  }
  process.stdout.write(']\n');

  capturing = false;
  await client.send('Page.stopScreencast').catch(() => {});
  await browser.close();

  console.log(`  ${frames.length} フレーム取得完了`);
  if (frames.length === 0) {
    console.error('  ERROR: フレームが取得できませんでした');
    rmSync(tmpDir, { recursive: true });
    return;
  }

  // concat ファイル生成（可変フレームレート対応）
  let concat = '';
  for (let i = 0; i < frames.length; i++) {
    const nextTs = i < frames.length - 1 ? frames[i + 1].ts : frames[i].ts + 1 / fps;
    const dur    = Math.max(0.01, nextTs - frames[i].ts);
    concat += `file '${frames[i].path}'\nduration ${dur.toFixed(5)}\n`;
  }
  concat += `file '${frames[frames.length - 1].path}'\n`;
  writeFileSync(path.join(tmpDir, 'list.txt'), concat);

  console.log('  ffmpeg エンコード中...');
  await new Promise((resolve, reject) => {
    const ff = spawn('ffmpeg', [
      '-y',
      '-f', 'concat', '-safe', '0',
      '-i', path.join(tmpDir, 'list.txt'),
      '-vf', `fps=${fps}`,
      '-vcodec', 'libx264', '-crf', '22', '-preset', 'fast',
      '-pix_fmt', 'yuv420p',
      path.join(__dirname, out),
    ], { stdio: ['ignore', 'ignore', 'pipe'] });

    ff.stderr.on('data', (d) => {
      const m = d.toString().match(/time=(\S+)/);
      if (m) process.stdout.write(`\r  エンコード: ${m[1]}   `);
    });
    ff.on('close', (code) => {
      process.stdout.write('\n');
      code === 0 ? resolve() : reject(new Error(`ffmpeg exited with ${code}`));
    });
  });

  rmSync(tmpDir, { recursive: true });

  const mb = (statSync(path.join(__dirname, out)).size / 1024 / 1024).toFixed(1);
  console.log(`  ✓ ${out}  (${mb} MB)`);
}

// ----- main -----
const targets = process.argv.slice(2).filter(a => MODES[a]);
const keys = targets.length ? targets : Object.keys(MODES);

(async () => {
  for (const k of keys) await record(MODES[k]);
  console.log('\n✓ 全録画完了！');
})().catch(e => { console.error(e); process.exit(1); });
