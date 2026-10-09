"""Build reviewed, attributed adapters from pinned public practice-bank snapshots.
No network access or upstream code execution. Run: python3 scripts/build-bank.py
"""
import json,re,pathlib,collections
root=pathlib.Path(__file__).resolve().parents[1]
raw=json.loads((root/'research/upstreams/raw.json').read_text())
origins={
'cassani':{'title':'CCAR-F Study Kit','author':'Alexio Cassani and contributors','url':'https://github.com/alexiocassanifm/anthropic-certifications','license':'CC BY-SA 4.0','licenseUrl':'https://creativecommons.org/licenses/by-sa/4.0/','revision':'b13f58a719962a19acb2ba9c1bfac4c897e2f85a'},
'aroui':{'title':'Claude Certified Architect Prep','author':'Haytam Aroui','url':'https://github.com/haytamAroui/Claude-Certified-Architect','license':'MIT','licenseUrl':'https://github.com/haytamAroui/Claude-Certified-Architect/blob/3bbc7f2529a1cbcd39324571fa73446b2ef26980/LICENSE','revision':'3bbc7f2529a1cbcd39324571fa73446b2ef26980'},
'choy':{'title':'Claude Architect Foundations Study Guide','author':'choychoy1','url':'https://github.com/choychoy1/claude-architect-foundations-study-guide','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','revision':'555a6e3d088e0a2626f2d9bf1c58f5ce3938c850'}
}
for o in origins.values():o['changes']='Adapted for this app: objective mapping, current terminology, answer-reference cleanup, official references, and selected answer corrections.'
maps={
'aroui1':'1.1 1.4 1.4 1.5 2.1 2.2 5.2 5.2 1.4 1.4 1.5 5.1 2.2 2.3 5.2 1.3 1.3 1.3 1.2 2.3 5.3 2.3 5.6 5.6 5.4 1.2 5.1 2.4 1.3 1.7 3.1 3.1 3.3 3.2 3.2 3.2 3.4 3.4 3.6 3.6 3.6 4.6 4.3 4.3 4.3 4.4 4.4 4.1 4.2 4.5 4.5 4.5 4.2 4.4'.split(),
'aroui2':'2.5 2.5 2.5 2.5 2.4 2.1 2.4 3.2 1.1 2.3 5.4 1.7 1.1 1.3 1.7 4.1 4.1 4.1 3.6 4.6 3.6 3.6 3.6 3.3 4.6 4.1 3.6 4.6 5.1 4.2 1.1 1.7 5.3 5.1 5.1 1.4 1.5 5.2 2.3 2.2 5.2 5.1 5.2 5.2 1.3 4.3 4.3 4.3 4.4 5.5 4.3 4.5 5.5 5.6 4.2 4.4 4.5 4.4 5.5 5.6'.split(),
'choy':'3.1 1.1 5.1 4.3 1.3 1.5 3.4 2.4 2.2 2.1 1.1 1.6 1.7 3.4 1.4 2.1 5.4 1.1 3.5 3.5 1.2 2.2 4.3 5.1 1.5 3.4 1.1 3.2 1.6 2.1 2.5 5.4 5.3 3.5 2.4 1.1 1.4 2.1 5.4 1.3 5.4 5.2 3.1 2.1 1.1 1.3 5.1 1.5 3.4 2.3 2.3 1.6 5.6 5.4 2.2 3.1 1.1 1.4 3.5 1.6'.split()}
assert len(maps['aroui1'])==54 and len(maps['aroui2'])==60 and len(maps['choy'])==60
refs={'1.1':'loop','1.2':'agents','1.3':'sub','1.4':'permissions','1.5':'hooks','1.6':'agents','1.7':'sessions','2.1':'tools','2.2':'loop','2.3':'tools','2.4':'mcp','2.5':'workflow','3.1':'memory','3.2':'skills','3.3':'memory','3.4':'workflow','3.5':'best','3.6':'workflow','4.1':'prompt','4.2':'prompt','4.3':'structured','4.4':'eval','4.5':'batch','4.6':'best','5.1':'context','5.2':'support','5.3':'errors','5.4':'best','5.5':'eval','5.6':'citations'}
excluded={
'cassani-d4-4.5-003':'Batch expiry does not guarantee successful completion; several cadence choices satisfy the simplified arithmetic.',
'cassani-d4-4.6-003':'Uncalibrated confidence is presented as an endorsed review mechanism without enough qualification.',
'aroui-exam1-q16':'Incorrectly places allowedTools on AgentDefinition instead of query options.',
'aroui-exam2-q13':'The implementation already checks stop_reason; a safety cap is not intrinsically incorrect.',
'aroui-exam2-q37':'Infers a cumulative refund policy not specified by the scenario.',
'choy-q16':'Tool descriptions alone do not enforce valid transactional identifiers.',
'choy-q20':'Conflicts with the guide’s advice to communicate interacting issues together.',
'choy-q37':'A path-scoped file permission does not guarantee protection through every tool such as Bash.',
'choy-q49':'Plan mode versus direct execution is underspecified for this refactor.'}
questions=[];seen=set();log=[]
def modern(s):
 s=re.sub(r'\bTask(?=\s+(?:tool|calls?|prompt))','Agent',s)
 s=s.replace('"Task"','"Agent"').replace("'Task'","'Agent'")
 s=re.sub(r'\bTask(?=\s*\()', 'Agent',s)
 return s
for q in raw:
 identity=q['origin']+'-'+q['originalId']
 if identity in excluded:log.append({'id':identity,'reason':excluded[identity]});continue
 q=json.loads(json.dumps(q));o=q['origin'];n=int(q['originalId'][-2:]) if o!='cassani' else 0
 task=q['task'] or maps['choy' if o=='choy' else 'aroui'+q['originalId'][4]][n-1]
 q['question']=modern(q['question']);q['options']=[modern(t) for t in q['options']]
 rationale=[modern(t) for t in q.get('rationales',[])];explanation=modern(q.get('explanation',''))
 notes=[]
 if any('Agent' in t for t in [q['question'],*q['options']]) and any('Task' in t for t in [next(x for x in raw if x['origin']==o and x['originalId']==q['originalId'])['question']]):notes.append('Current SDK tool calls use Agent; older guide/examples may call it Task.')
 if identity=='cassani-d1-1.3-003':
  q['question']='A TypeScript SDK coordinator is defined with specialists in query options, but its allowedTools lists only Read and Grep. Its permission policy blocks delegation calls. Which configuration change enables delegation?'
  q['options'][q['correct'][0]]='Include Agent in the coordinator query options’ allowedTools and permit delegation under the permission policy.'
  rationale[q['correct'][0]]='Current SDK examples configure delegation in query options using the Agent tool. AgentDefinition.tools scopes the specialist’s own tools.'
 if identity=='aroui-exam1-q35':
  explanation='A project .claude/commands/deploy.md is a supported shared command location. Commands and skills have merged in current Claude Code; a project .claude/skills/deploy/SKILL.md can also expose /deploy, so this item asks specifically about the command-file location.'
  q['question']='You need a custom /deploy command available to every teammate. If you use the supported Markdown command-file format, where should that file live?'
 if identity=='aroui-exam1-q36':
  q['question']='Your deploy skill should display a hint showing developers the expected target-environment argument in the slash-command menu. Which SKILL.md frontmatter field provides this hint?'
  explanation='argument-hint displays expected arguments. It does not enforce required arguments or automatically ask a missing-argument question; implement that behavior in the skill instructions.'
 if identity in ['aroui-exam1-q45','aroui-exam2-q39','choy-q51','cassani-d2-2.3-003']:
  q['question']='On a model and configuration supporting forced tool choice, '+q['question'][0].lower()+q['question'][1:]
  notes.append('Forced tool choice depends on model and thinking compatibility; it does not itself enforce business prerequisites.')
 if identity=='cassani-d4-4.3-001':
  q['options'][1]='Define an extraction tool with its JSON input schema, enable strict: true on a supported model, force that tool, and read its tool_use arguments.'
  rationale[1]='Strict tool use enforces the supported input schema. A schema description without strict mode is not itself a schema-adherence guarantee.'
  rationale[3]='Examples can improve compliance, but strict tool use provides schema enforcement for supported schemas and models.'
 if identity=='choy-q04':
  q['options'][q['correct'][0]]='Define a tool with the target input_schema, enable strict: true on a supported model, and force that tool for the extraction.'
  explanation='Strict tool use enforces supported schema constraints. Prompting alone does not guarantee structure. Check exceptional stop reasons and validate business semantics.'
 if identity=='choy-q23':
  q['options'][0]='It specifies the expected argument structure; even schema-conforming values can still be factually wrong.'
  explanation='The schema describes valid inputs. Strict tool use enforces supported schema constraints, while application validation must still check factual and business correctness.'
 if identity=='aroui-exam1-q46':
  q['question']=q['question'].replace('enforces correct syntax via tool_use','enforces schema-conforming arguments through strict tool use')
  explanation='Strict tool use enforces supported schema constraints, not the truth of extracted values or cross-field arithmetic. Validate totals against the source and flag inconsistent documents.'
 if identity=='aroui-exam2-q42':
  q['question']=q['question'].replace('Your agent receives','Your Claude Code agent receives');q['options'][q['correct'][0]]=q['options'][q['correct'][0]].replace('at turn 10','when context usage calls for it');explanation='Preserve critical case facts before compacting the conversation. Choose compaction based on context usage, rather than an arbitrary fixed turn.'
 if identity=='aroui-exam2-q02':
  q['options'][3]='First make the Edit anchor unique by including surrounding context; if a unique anchor is unavailable, Read the file and Write back the edited content.'
 if identity=='aroui-exam2-q14':q['options'][3]='Check both the specialist’s actual search-tool access and its instructions to investigate the repository rather than guess from general patterns.'
 if identity=='aroui-exam2-q56':q['options'][3]='Add semantic validation and improve field definitions and examples in the extraction prompt.'
 if identity=='aroui-exam2-q31':
  q['options'][q['correct'][0]]='Subsequent requests must retain the relevant accumulated context, including prior decisions and matching tool results; dropping everything except the latest result loses state.'
  explanation='The Messages API receives the context supplied in each request. You can summarize older history, but preserve relevant state and correctly paired tool-use/result messages.'
 if identity=='choy-q47':
  q['question']='A developer retains and re-sends the entire growing message history without caching or compaction. Comparable steps later in the session take more input tokens than earlier steps. What explains this?'
  explanation='Retaining the full accumulated history increases subsequent request input size. Compaction and prompt caching can alter the context and cost profile.'
 # Replace references to upstream answer letters with quoted options, since answer order is shuffled.
 def quote(m):
  letter=m[1];text=q['options'][ord(letter)-65];return '“'+text[:150]+('…' if len(text)>150 else '')+'”'
 def unletter(s):
  s=re.sub(r'\b([A-D])(?=\s+(?:is|are|would|adds?|helps?|misdiagnoses|fails?|confuses|makes|starts|contains|guarantees|only|does|puts))',quote,s)
  s=re.sub(r'(?<=[(,])\s*([A-D])(?=\s*[,):—–-])',quote,s)
  s=re.sub(r'\b([A-D])(?=\s+and\s+[A-D]\b)',quote,s)
  s=re.sub(r'(?<=and )([A-D])\b',quote,s)
  return s
 explanation=unletter(explanation);rationale=[unletter(t) for t in rationale]
 normalized=re.sub(r'\W+','',q['question']).lower()
 if normalized in seen:log.append({'id':identity,'reason':'Duplicate normalized stem'});continue
 seen.add(normalized)
 if not explanation:explanation=' '.join(rationale[i] for i in q['correct'])
 # Discard unsupported blanket claims and retain the guide-aligned decision being tested.
 explanation=explanation.replace('100% deterministic enforcement','programmatic enforcement').replace('100% enforcement','programmatic enforcement')
 assert len(q['options'])==4 and len(set(q['options']))==4 and len(set(q['correct']))==len(q['correct'])
 record={'id':identity,'task':task,'domain':int(task[0]),'source':refs[task],'question':q['question'],'options':q['options'],'correct':q['correct'],'explanation':explanation,'front':q['question'],'answer':'; '.join(q['options'][i] for i in q['correct'])+'. '+explanation,'difficulty':'Applied','origin':o,'originalId':q['originalId'],'reviewedOn':'2026-10-08','reviewNotes':' '.join(notes),'guideReference':True}
 if rationale:record['optionExplanations']=rationale
 questions.append(record)
(root/'dist/imported-bank.js').write_text('// Generated by scripts/build-bank.py. Adapted content retains its origin license.\nexport const bankOrigins='+json.dumps(origins,ensure_ascii=False,indent=2)+';\nexport const importedQuestions='+json.dumps(questions,ensure_ascii=False,indent=2)+';\n')
report={'reviewedOn':'2026-10-08','candidates':len(raw),'included':len(questions),'includedByOrigin':dict(collections.Counter(q['origin'] for q in questions)),'excluded':log,'origins':origins,'policy':'Community practice text adapted with attribution. Decisions referenced to Anthropic docs and exam objectives. This review is not psychometric calibration.'}
(root/'research/bank-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['origins','excluded']},indent=2))
