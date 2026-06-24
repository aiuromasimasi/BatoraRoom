const GAMES = [{"id": 2, "pos": 1, "title": "ティアーズ オブ ザ キングダム", "img": "game_covers/c2.jpg"}, {"id": 41, "pos": 2, "title": "うみねこのなく頃に", "img": "game_covers/c41.jpg"}, {"id": 1, "pos": 3, "title": "ブレス オブ ザ ワイルド", "img": "game_covers/c1.jpg"}, {"id": 65, "pos": 4, "title": "UNREAL", "img": "game_covers/c65.jpg"}, {"id": 42, "pos": 5, "title": "ひぐらしのなく頃に", "img": "game_covers/c42.jpg"}, {"id": 67, "pos": 6, "title": "ディアブロII", "img": "game_covers/c67.jpg"}, {"id": 24, "pos": 7, "title": "ファイナルファンタジー5", "img": "game_covers/c24.jpg"}, {"id": 77, "pos": 8, "title": "テトリス グランドマスター2 THE ABSOLUTE PLUS", "img": "game_covers/c77.jpg"}, {"id": 64, "pos": 9, "title": "QUAKE II", "img": "game_covers/c64.jpg"}, {"id": 56, "pos": 10, "title": "レイディアント シルバーガン", "img": "game_covers/c56.jpg"}, {"id": 57, "pos": 11, "title": "怒首領蜂", "img": "game_covers/c57.jpg"}, {"id": 3, "pos": 12, "title": "ゼルダの伝説 神々のトライフォース", "img": "game_covers/c3.jpg"}, {"id": 14, "pos": 13, "title": "聖剣伝説2", "img": "game_covers/c14.jpg"}, {"id": 25, "pos": 14, "title": "ファイナルファンタジー6", "img": "game_covers/c25.jpg"}, {"id": 37, "pos": 15, "title": "かまいたちの夜", "img": "game_covers/c37.jpg"}, {"id": 54, "pos": 16, "title": "痕", "img": "game_covers/c54.jpg"}, {"id": 33, "pos": 17, "title": "クロノトリガー", "img": "game_covers/c33.jpg"}, {"id": 47, "pos": 18, "title": "スウィートホーム", "img": "game_covers/c47.jpg"}, {"id": 6, "pos": 19, "title": "スーパーマリオワールド", "img": "game_covers/c6.jpg"}, {"id": 60, "pos": 20, "title": "グラディウス外伝", "img": "game_covers/c60.jpg"}, {"id": 39, "pos": 21, "title": "ダンガンロンパ 希望の学園と絶望の高校生", "img": "game_covers/c39.jpg"}, {"id": 18, "pos": 22, "title": "ドラゴンクエスト3", "img": "game_covers/c18.jpg"}, {"id": 52, "pos": 23, "title": "Kanon", "img": "game_covers/c52.jpg"}, {"id": 48, "pos": 24, "title": "街 〜運命の交差点〜", "img": "game_covers/c48.jpg"}, {"id": 10, "pos": 25, "title": "スーパーマリオブラザーズ2（ディスクシステム）", "img": "game_covers/c10.jpg"}, {"id": 55, "pos": 26, "title": "ブランディッシュ3", "img": "game_covers/c55.jpg"}, {"id": 98, "pos": 27, "title": "NiGHTS into dreams...", "img": "game_covers/c98.jpg"}, {"id": 79, "pos": 28, "title": "スーパーストリートファイターII X", "img": "game_covers/c79.jpg"}, {"id": 40, "pos": 29, "title": "スーパーダンガンロンパ2", "img": "game_covers/c40.jpg"}, {"id": 90, "pos": 30, "title": "ロックマン2", "img": "game_covers/c90.jpg"}, {"id": 78, "pos": 31, "title": "TETRIS THE GRAND MASTER 4 -ABSOLUTE EYE-", "img": "game_covers/c78.jpg"}, {"id": 100, "pos": 32, "title": "セガラリー", "img": "game_covers/c100.jpg"}, {"id": 62, "pos": 33, "title": "Gダライアス", "img": "game_covers/c62.jpg"}, {"id": 32, "pos": 34, "title": "英雄伝説3 白き魔女", "img": "game_covers/c32.jpg"}, {"id": 29, "pos": 35, "title": "真・女神転生II", "img": "game_covers/c29.jpg"}, {"id": 69, "pos": 36, "title": "StarCraft", "img": "game_covers/c69.jpg"}, {"id": 70, "pos": 37, "title": "Left 4 Dead", "img": "game_covers/c70.jpg"}, {"id": 43, "pos": 38, "title": "STEINS;GATE", "img": "game_covers/c43.jpg"}, {"id": 51, "pos": 39, "title": "AIR", "img": "game_covers/c51.jpg"}, {"id": 35, "pos": 40, "title": "トルネコの大冒険 不思議のダンジョン", "img": "game_covers/c35.jpg"}, {"id": 28, "pos": 41, "title": "真・女神転生", "img": "game_covers/c28.jpg"}, {"id": 31, "pos": 42, "title": "デビルサマナー", "img": "game_covers/c31.jpg"}, {"id": 22, "pos": 43, "title": "ファイナルファンタジー3", "img": "game_covers/c22.jpg"}, {"id": 20, "pos": 44, "title": "ドラゴンクエスト5", "img": "game_covers/c20.jpg"}, {"id": 85, "pos": 45, "title": "将棋ウォーズ", "img": "game_covers/c85.jpg"}, {"id": 74, "pos": 46, "title": "PAINKILLER", "img": "game_covers/c74.jpg"}, {"id": 17, "pos": 47, "title": "魔界塔士Sa・Ga2 秘宝伝説", "img": "game_covers/c17.jpg"}, {"id": 15, "pos": 48, "title": "LIVE A LIVE", "img": "game_covers/c15.jpg"}, {"id": 27, "pos": 49, "title": "NieR:Automata", "img": "game_covers/c27.jpg"}, {"id": 26, "pos": 50, "title": "ファイナルファンタジー7", "img": "game_covers/c26.jpg"}, {"id": 95, "pos": 51, "title": "悪魔城ドラキュラX 月下の夜想曲", "img": "game_covers/c95.jpg"}, {"id": 16, "pos": 52, "title": "スーパーマリオRPG", "img": "game_covers/c16.jpg"}, {"id": 23, "pos": 53, "title": "ファイナルファンタジー4", "img": "game_covers/c23.jpg"}, {"id": 12, "pos": 54, "title": "ICO", "img": "game_covers/c12.jpg"}, {"id": 59, "pos": 55, "title": "グラディウスIII", "img": "game_covers/c59.jpg"}, {"id": 66, "pos": 56, "title": "Unreal Tournament", "img": "game_covers/c66.jpg"}, {"id": 89, "pos": 57, "title": "God of War", "img": "game_covers/c89.jpg"}, {"id": 86, "pos": 58, "title": "DDR（Dance Dance Revolution）", "img": "game_covers/c86.jpg"}, {"id": 71, "pos": 59, "title": "Plants vs. Zombies", "img": "game_covers/c71.jpg"}, {"id": 83, "pos": 60, "title": "ストリートファイターIII 3rd STRIKE", "img": "game_covers/c83.jpg"}, {"id": 44, "pos": 61, "title": "レイジングループ", "img": "game_covers/c44.jpg"}, {"id": 58, "pos": 62, "title": "グラディウスII", "img": "game_covers/c58.jpg"}, {"id": 87, "pos": 63, "title": "beatmania IIDX", "img": "game_covers/c87.jpg"}, {"id": 80, "pos": 64, "title": "バーチャファイター2", "img": "game_covers/c80.jpg"}, {"id": 68, "pos": 65, "title": "WarCraft III", "img": "game_covers/c68.jpg"}, {"id": 21, "pos": 66, "title": "ドラゴンクエスト10", "img": "game_covers/c21.jpg"}, {"id": 97, "pos": 67, "title": "コナミワイワイワールド", "img": "game_covers/c97.jpg"}, {"id": 53, "pos": 68, "title": "雫", "img": "game_covers/c53.jpg"}, {"id": 72, "pos": 69, "title": "ウルティマオンライン", "img": "game_covers/c72.jpg"}, {"id": 91, "pos": 70, "title": "UNDERTALE", "img": "game_covers/c91.jpg"}, {"id": 61, "pos": 71, "title": "東方紺珠伝", "img": "game_covers/c61.jpg"}, {"id": 8, "pos": 72, "title": "スーパーマリオ オデッセイ", "img": "game_covers/c8.jpg"}, {"id": 75, "pos": 73, "title": "終ノ空", "img": "game_covers/c75.jpg"}, {"id": 81, "pos": 74, "title": "鉄拳3", "img": "game_covers/c81.jpg"}, {"id": 63, "pos": 75, "title": "斑鳩 IKARUGA", "img": "game_covers/c63.jpg"}, {"id": 94, "pos": 76, "title": "デイヴ・ザ・ダイバー", "img": "game_covers/c94.jpg"}, {"id": 88, "pos": 77, "title": "It Takes Two", "img": "game_covers/c88.jpg"}, {"id": 46, "pos": 78, "title": "都市伝説解体センター", "img": "game_covers/c46.jpg"}, {"id": 76, "pos": 79, "title": "マインクラフト", "img": "game_covers/c76.jpg"}, {"id": 45, "pos": 80, "title": "キミガシネ", "img": "game_covers/c45.jpg"}, {"id": 19, "pos": 81, "title": "ドラゴンクエスト4", "img": "game_covers/c19.jpg"}, {"id": 99, "pos": 82, "title": "デイトナUSA", "img": "game_covers/c99.jpg"}, {"id": 82, "pos": 83, "title": "THE KING OF FIGHTERS '98", "img": "game_covers/c82.jpg"}, {"id": 36, "pos": 84, "title": "不思議のダンジョン 風来のシレン", "img": "game_covers/c36.jpg"}, {"id": 4, "pos": 85, "title": "ゼルダの伝説 夢をみる島", "img": "game_covers/c4.jpg"}, {"id": 5, "pos": 86, "title": "星のカービィ ディスカバリー", "img": "game_covers/c5.jpg"}, {"id": 49, "pos": 87, "title": "VA-11 Hall-A", "img": "game_covers/c49.jpg"}, {"id": 34, "pos": 88, "title": "ロマンシング サガ2", "img": "game_covers/c34.jpg"}, {"id": 30, "pos": 89, "title": "真・女神転生III NOCTURNE", "img": "game_covers/c30.jpg"}, {"id": 7, "pos": 90, "title": "カエルのために鐘は鳴る", "img": "game_covers/c7.jpg"}, {"id": 9, "pos": 91, "title": "ヨッシーストーリー", "img": "game_covers/c9.jpg"}, {"id": 96, "pos": 92, "title": "レッドアリーマー（魔界村外伝）", "img": "game_covers/c96.jpg"}, {"id": 13, "pos": 93, "title": "朧村正", "img": "game_covers/c13.jpg"}, {"id": 38, "pos": 94, "title": "弟切草", "img": "game_covers/c38.jpg"}, {"id": 73, "pos": 95, "title": "Slay the Spire", "img": "game_covers/c73.jpg"}, {"id": 92, "pos": 96, "title": "CUPHEAD", "img": "game_covers/c92.jpg"}, {"id": 11, "pos": 97, "title": "ゼルダの伝説（初代）", "img": "game_covers/c11.jpg"}, {"id": 93, "pos": 98, "title": "PICO PARK", "img": "game_covers/c93.jpg"}, {"id": 84, "pos": 99, "title": "Deemo", "img": "game_covers/c84.jpg"}, {"id": 50, "pos": 100, "title": "魔法少女ノ魔女裁判", "img": "game_covers/c50.jpg"}];
const BANDS = [[1, 10], [11, 20], [21, 30], [31, 40], [41, 50], [51, 60], [61, 70], [71, 80], [81, 90], [91, 100]];
const PKEY='game_sort_prefs_v3', OKEY='game_sort_order_v3';
let prefs = JSON.parse(localStorage.getItem(PKEY)||'{}');
let order = JSON.parse(localStorage.getItem(OKEY)||'[]');
const keyOf=(a,b)=>Math.min(a,b)+'-'+Math.max(a,b);
let pending=null;
const EST=240;
const $=id=>document.getElementById(id);
function save(){localStorage.setItem(PKEY,JSON.stringify(prefs));localStorage.setItem(OKEY,JSON.stringify(order));}
function progress(){const n=Object.keys(prefs).length;$('cnt').textContent=n;$('pi').style.width=Math.min(100,Math.round(n/EST*100))+'%';}
function setBand(lo,hi,bi){$('band').textContent=lo+'〜'+hi+'位 グループを整理中（'+(bi+1)+'/'+BANDS.length+'）';}
function render(a,b){
  $('Limg').src=a.img;$('Lnm').textContent=a.title;$('Lrk').textContent='現在 '+a.pos+'位';
  $('Rimg').src=b.img;$('Rnm').textContent=b.title;$('Rrk').textContent='現在 '+b.pos+'位';
  $('undo').disabled = order.length===0;
}
function compare(a,b){
  const k=keyOf(a.id,b.id);
  if(prefs[k]!=null) return Promise.resolve(prefs[k]);
  return new Promise(res=>{pending={a,b,k,res};render(a,b);});
}
function choose(winnerId){
  if(!pending)return; const {k,res}=pending; prefs[k]=winnerId; order.push(k); pending=null; save(); progress(); res(winnerId);
}
async function mergeSort(arr){
  if(arr.length<=1)return arr;
  const mid=arr.length>>1;
  const L=await mergeSort(arr.slice(0,mid));
  const R=await mergeSort(arr.slice(mid));
  const out=[];let i=0,j=0;
  while(i<L.length&&j<R.length){const w=await compare(L[i],R[j]);if(w===L[i].id)out.push(L[i++]);else out.push(R[j++]);}
  while(i<L.length)out.push(L[i++]);while(j<R.length)out.push(R[j++]);return out;
}
function finish(sorted){
  $('game').classList.add('hide');
  $('result').classList.remove('hide');
  $('out').value='新順位CID: '+sorted.map(g=>g.id).join(',');
  $('list').innerHTML=sorted.map((g,i)=>'<li>'+g.title+' <span style="color:#bbb">(現'+g.pos+'位)</span></li>').join('');
}
// 途中でも、今ある回答だけで並べ替えを出力（回答収集と同じマージソート構造で再生。未回答ペアは現状順位で補完）
function msSync(arr){
  if(arr.length<=1)return arr;
  const mid=arr.length>>1;const L=msSync(arr.slice(0,mid)),R=msSync(arr.slice(mid));
  const out=[];let i=0,j=0;
  while(i<L.length&&j<R.length){const a=L[i],b=R[j];const k=keyOf(a.id,b.id);
    const w=(prefs[k]!=null)?prefs[k]:(a.pos<b.pos?a.id:b.id);
    if(w===a.id)out.push(L[i++]);else out.push(R[j++]);}
  while(i<L.length)out.push(L[i++]);while(j<R.length)out.push(R[j++]);return out;
}
function exportNow(){
  const result=[];
  for(const [lo,hi] of BANDS){const items=GAMES.filter(g=>g.pos>=lo&&g.pos<=hi);result.push(...msSync(items));}
  $('expbox').classList.remove('hide');
  $('out2').value='新順位ID: '+result.map(g=>g.id).join(',');
  const n=Object.keys(prefs).length;
  $('expnote').textContent='（'+n+'回ぶんの回答を反映。未回答ペアは現状順位のまま）';
}
async function run(){
  const result=[];
  for(let bi=0;bi<BANDS.length;bi++){
    const [lo,hi]=BANDS[bi]; setBand(lo,hi,bi);
    const items=GAMES.filter(g=>g.pos>=lo&&g.pos<=hi);
    const sorted=await mergeSort(items);
    result.push(...sorted);
  }
  finish(result);
}
function init(){
  $('L').onclick=()=>{if(pending)choose(pending.a.id);};
  $('R').onclick=()=>{if(pending)choose(pending.b.id);};
  document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'&&pending)choose(pending.a.id);if(e.key==='ArrowRight'&&pending)choose(pending.b.id);});
  $('undo').onclick=()=>{if(order.length===0)return;const k=order.pop();delete prefs[k];save();location.reload();};
  const reset=()=>{if(confirm('回答を全部消して最初から？')){localStorage.removeItem(PKEY);localStorage.removeItem(OKEY);location.reload();}};
  $('reset').onclick=reset; $('reset2').onclick=reset;
  const cp=id=>{const t=$(id);t.removeAttribute('readonly');t.select();try{navigator.clipboard.writeText(t.value)}catch(e){}try{document.execCommand('copy')}catch(e){}t.setAttribute('readonly','');};
  $('copy').onclick=()=>cp('out');
  $('exp').onclick=exportNow; $('copy2').onclick=()=>cp('out2');
  progress();
  run();
}
if(document.readyState!=='loading') init(); else document.addEventListener('DOMContentLoaded', init);
