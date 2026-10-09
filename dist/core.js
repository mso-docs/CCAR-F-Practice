import {validateDecks,allPersonalCards} from './packs.js';
export const DAY=86400000;
export const defaults=()=>({version:1,cards:{},quiz:{},bookmarks:[],activity:{},sessions:[],settings:{newLimit:20,reviewLimit:100,goal:20},activeQuiz:null,enabledPacks:[],personalDecks:[]});
export function dayKey(time=Date.now()){const d=new Date(time);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
export function schedule(previous,rating,now=Date.now()){
 if(!['again','hard','good','easy'].includes(rating))throw new Error('Invalid recall rating');
 const p=previous||{ease:2.5,interval:0,reps:0,lapses:0};let ease=p.ease,interval,reps=p.reps,lapses=p.lapses,delay;
 if(rating==='again'){interval=0;reps=0;lapses++;ease=Math.max(1.3,ease-.2);delay=60000;}
 else if(rating==='hard'){interval=p.interval?Math.max(1,p.interval*1.2):0;ease=Math.max(1.3,ease-.15);delay=interval?interval*DAY:600000;}
 else {reps++;if(rating==='good'){interval=reps===1?1:reps===2?6:Math.max(1,p.interval*ease);}else{ease=Math.min(3,ease+.15);interval=p.interval?Math.max(4,p.interval*ease*1.3):4;}interval=Math.min(36500,Math.round(interval*100)/100);delay=interval*DAY;}
 return {ease,interval,reps,lapses,due:now+delay,last:now,reviews:(p.reviews||0)+1};
}
export function sameSet(a,b){return Array.isArray(a)&&a.length===b.length&&new Set(a).size===a.length&&a.every(x=>b.includes(x));}
export function shuffle(list,rng=Math.random){const a=[...list];for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
export function mockSelection(questions,rng=Math.random){const counts=[16,11,12,12,9];const pool=counts.flatMap((n,i)=>{const items=questions.filter(q=>q.domain===i+1);if(items.length<n)throw new Error('Not enough questions for a weighted mock');return shuffle(items,rng).slice(0,n);});return shuffle(pool,rng);}
export function streak(activity,now=Date.now()){let count=0,d=new Date(now);if(!(activity[dayKey(d.getTime())]?.total>0))d.setDate(d.getDate()-1);while(activity[dayKey(d.getTime())]?.total>0){count++;d.setDate(d.getDate()-1);}return count;}
export function dueCards(questions,state,domain=0,now=Date.now()){
 const candidates=questions.filter(q=>!domain||q.domain===Number(domain));
 const today=state.activity[dayKey(now)]||{newCards:0,cardReviews:0};
 const reviews=candidates.filter(q=>state.cards[q.id]&&state.cards[q.id].due<=now).sort((a,b)=>state.cards[a.id].due-state.cards[b.id].due).slice(0,Math.max(0,state.settings.reviewLimit-(today.cardReviews||0)));
 const fresh=candidates.filter(q=>!state.cards[q.id]).slice(0,Math.max(0,state.settings.newLimit-(today.newCards||0)));
 return [...reviews,...fresh];
}
export function validateBackup(value,questions){
 const result=defaults();result.personalDecks=validateDecks(value?.personalDecks);const validIds=new Set([...questions,...allPersonalCards(result)].map(q=>q.id));const knownPacks=new Set(questions.map(q=>q.origin).filter(Boolean));result.enabledPacks=Array.isArray(value?.enabledPacks)?[...new Set(value.enabledPacks.filter(id=>knownPacks.has(id)))]:[];
 if(!value||value.version!==1||typeof value.cards!=='object'||Array.isArray(value.cards))throw new Error('This is not a Study Studio version 1 backup.');
 const finite=(x,min=0,max=Number.MAX_SAFE_INTEGER)=>typeof x==='number'&&Number.isFinite(x)&&x>=min&&x<=max;
 for(const [id,c] of Object.entries(value.cards)){if(!validIds.has(id))continue;if(!c||!finite(c.due)||!finite(c.ease,1.3,3)||!finite(c.interval,0,36500)||!Number.isInteger(c.reps)||c.reps<0||!Number.isInteger(c.lapses)||c.lapses<0||!finite(c.last)||!finite(c.reviews))throw new Error('Invalid flashcard scheduling data.');result.cards[id]={due:c.due,ease:c.ease,interval:c.interval,reps:c.reps,lapses:c.lapses,last:c.last,reviews:c.reviews};}
 for(const [id,q] of Object.entries(value.quiz||{})){if(!validIds.has(id))continue;if(!q||!Number.isInteger(q.attempts)||q.attempts<0||!Number.isInteger(q.correct)||q.correct<0||q.correct>q.attempts||typeof q.lastCorrect!=='boolean')throw new Error('Invalid quiz progress.');result.quiz[id]={attempts:q.attempts,correct:q.correct,lastCorrect:q.lastCorrect};}
 result.bookmarks=Array.isArray(value.bookmarks)?[...new Set(value.bookmarks.filter(id=>validIds.has(id)))]:[];
 for(const [date,a] of Object.entries(value.activity||{})){if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!a||!['total','newCards','cardReviews'].every(k=>Number.isInteger(a[k])&&a[k]>=0))throw new Error('Invalid study activity.');result.activity[date]={total:a.total,newCards:a.newCards,cardReviews:a.cardReviews};}
 for(const key of ['newLimit','reviewLimit','goal']){const n=value.settings?.[key];if(!Number.isInteger(n)||n<1||n>500)throw new Error('Invalid study settings.');result.settings[key]=n;}
 result.sessions=(Array.isArray(value.sessions)?value.sessions:[]).filter(s=>s&&['practice','mock'].includes(s.mode)&&finite(s.date)&&Number.isInteger(s.total)&&s.total>0&&s.total<=questions.length&&Number.isInteger(s.correct)&&s.correct>=0&&s.correct<=s.total).slice(-100).map(s=>({date:s.date,mode:s.mode,total:s.total,correct:s.correct}));
 return result;
}
