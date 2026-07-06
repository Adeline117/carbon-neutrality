# Response-to-Reviewer 预案(核对后分级版)/ Response Plan (verified & regraded)

**适用稿件 / Manuscript**: `docs/natcomms-draft/latex/manuscript.tex`(ERL Letter 版)
**分级结论 / Grading**: 硬伤 = 第 1、3、7 点 + copyedit;措辞 = 第 2、5、6 点;第 4 点保留但置信度调低。
**Hard flaws = Points 1, 3, 7 + copyedit; wording-only = Points 2, 5, 6; Point 4 retained at lowered confidence.**


## 硬伤 / Hard flaws

### 第 1 点:within-token 对照的四重局限 / Point 1: four limitations of the within-token contrast

- **指控**: n=14;100% 一侧部分由 selection-on-redemption 构造;two-pool 混杂;仅覆盖 nature-based,排除了占 69% 的可再生。最强的准因果证据落在一个不代表主线故事的子集上。
- **锚点**: `manuscript.tex:152`(局限段, "descriptive, not causal identifications ... rest on only two pools ... dominant renewables are structurally excluded");`manuscript.tex:177`(Methods, "The estimand is the pool-design effect on dual-eligible credits ... a higher-quality nature-based subset rather than the full unscreened pool");Fig. 4 caption `manuscript.tex:283`("descriptive; a two-pool comparison, not a causal identification")。
- **预案回应**: 四条局限全部已在正文逐条自标,不辩护、直接指认原句。主线结论(69.1% 对 4.2% 的组成反转、1.87 倍基率、赎回取证)不依赖 within-token;该对照回答的是另一个问题(对双池均可入的信用,池设计是否改变命运),正文在 154 行已明说可再生被结构性排除。若审稿人要求,可再降一档措辞:把摘要中 "consistent with pool design ... shaping outcomes" 保持原样,不加码。
- **Response (EN)**: All four limitations are already self-flagged verbatim in the text (lines 152, 177, Fig. 4 caption). The headline story (composition reversal, base-rate selection, redemption forensics) does not rest on the within-token contrast, which answers a narrower question about dual-eligible credits. We concede the subset is not representative and the text says so explicitly.

### 第 3 点:wallet 不等于 entity / Point 3: wallet is not entity(已根源修复 / root-fixed)

- **指控**: dual-margin「两个独立人群」的新颖性系于未证的实体级独立性。
- **锚点**: `manuscript.tex:111`(现行文本为 first-funder 审计句 "found entity-level links for a minority ... account-level, not entity-level";修复前的让步句已被其替代)。
- **预案回应**: 正文该句即是承认,直接引用。补充辩护:即使存款与赎回账户同属一实体,机制主张仍成立(连接两侧的是池的统一定价,不是人群身份);受威胁的只是「两个人群」这一表述,可让步为「两个账户群体」。可承诺的稳健性方向:资金图谱聚类作为未来工作,不作为本稿主张。
- **Response (EN)**: Previously conceded at what is now line 111 (sentence since replaced by the executed first-funder audit). Fallback: the mechanism claim survives entity overlap because uniform pricing, not population identity, connects the two margins; we can weaken "two distinct account populations" to a purely account-level statement if required.
- **已执行(2026-07-03)**: 完成链上 first-funder 审计(两侧各 top 20,33 个 EOA 全部解析)。发现:1 个跨侧共同资金来源、3 个账户间 7 笔直接转账、2 个双边际账户,合计占前 20 存入吨量 26\%、赎回吨量 9\%。正文已按结局 2 降级为账户级表述并如实报告;方法与逐项发现见补充材料 "Entity-level independence check";复现脚本 `data/depositor-analysis/entity_funding_analysis.py`。
- **Executed (EN)**: First-funder audit done (top 20 per margin, all 33 EOAs resolved). One cross-side common funder, seven direct transfers among three accounts, two dual-margin accounts (26\% of top-20 deposit, 9\% of top-20 redemption tonnage). Main text downgraded to an account-level statement reporting the links; full method in Supplementary.

### 第 7 点:顶层措辞强于 results / Point 7: top-level framing stronger than results(已执行 / executed)

- **指控**: 「REDD+ 叙事纠错 + 信用级取证」很硬;作为「强因果 + 新理论」则偏脆;标题与摘要的调门高于 results 支持的水平。
- **锚点**: 标题 `manuscript.tex:18`("Transparency without pricing: a credit-level forensic account");摘要 `manuscript.tex:32`(原最强句 "We show this collapse also occurs...",已改为 "We document a collapse that occurred despite quality being fully and publicly observable");导言 `manuscript.tex:46`(原 "strongly consistent with pool design","strongly" 已删)。
- **预案回应**: 标题已是描述性取证定位("forensic account"),摘要多处已用 "consistent with" "appears insufficient" "may need" 对冲。预备的退让编辑(若审稿人仍读出强因果):摘要该句改为 "We document a collapse that occurred despite quality being fully and publicly observable";导言 "strongly consistent" 去掉 "strongly"。两处改动均已预写,可即时执行。
- **Response (EN)**: Title and abstract are already forensic-descriptive with hedged verbs. 
- **已执行(2026-07-03)**: 两处退让编辑已主动落地:摘要改为 "We document a collapse that occurred despite...",导言删除 "strongly"。中英稿同步。

### Copyedit(硬伤级,已处理 / handled)

- **状态(2026-07-04 洛基轮后更新)**: 六个猎手 + 逐条反驳的 agent 团队审计已完成,43 条确认发现全部处置。关键更正:gating 数字改为真实存款流口径(0.689 至 0.506,放行 7.2% 吨量;旧 0.724/0.405 出自风格化模拟,已全库取代);滞留量 9.6M 改 9.3M;专家小组 ρ=0.814(虚构模板数据)已从论文删除;BeZero ρ=0.901 改标非盲一致性;利润改为脚本推导的中点约 \$10M;五条引文元数据修正。全部头条数字现由 `tools/verify_headline_numbers.py`(21 项断言)机器守护。
- **Status (EN)**: The six numeric inconsistencies were reconciled in the ERL-conformance pass; all load-bearing terms are glossed at first use. One final proofread pass before submission.


## 措辞 / Wording-only

### 第 2 点:design-enabled adverse selection 的命名与新颖性 / Point 2: naming and novelty

- **核对结论**: 底层经济学(统一定价下的 Gresham/pooling)不新,但论文没有假装它新;命名与「distinct pathway(质量可观测)」的定位站得住。
- **锚点**: `manuscript.tex:48`("We term this outcome ... We argue that uniform pricing ... is sufficient");`manuscript.tex:140`(明确归功 Akerlof 与 Manshadi et al. 的理论化, "runs through market architecture rather than information asymmetry")。
- **预案回应**: 指认 48 行的 "We argue" 与 140 行的文献归属即可。唯一注意事项:任何新增文字不得让它听起来像提出了新机制,只是命名了一条已知逻辑的新路径。无需改稿。
- **Response (EN)**: The text attributes the economics to Akerlof and Manshadi et al. and hedges with "We argue". Keep the framing as naming a pathway, never as proposing a new mechanism. No edit needed.

### 第 5 点:(内容不可得 / content unavailable)

- **状态**: 原文在用户两次粘贴中于同一位置被截断,内容不可得(源文本损坏)。已知结论:经复核后从「硬伤」降级为「措辞」。占位保留。
- **Status (EN)**: The pasted review was truncated here; the substance of Point 5 was lost. Known: you regraded it from hard flaw to wording-only. Supply one line and this entry will be completed.

### 第 6 点:福利口径(基本撤回 / largely withdrawn)

- **核对结论**: welfare gap 是组成对照量(反事实池按 VCS 基率组成的期望气候价值,减去 BCT 实际组成的期望气候价值),不是「junk 被当真退休」的欺骗性退休机制;「\$146M gap」与「搁浅是意外的质量过滤」两个 frame 可同时为真,无内在矛盾。原先「改写成 junk-retired」的建议会歪曲方法,已撤回。
- **锚点**: `manuscript.tex:205`(Methods 定义, "the difference in expected climate value between the counterfactual pool and BCT's actual composition");`manuscript.tex:144`(两个 frame 并排出现的讨论段)。
- **已执行(2026-07-03)**: 过渡句已加入 146 行两个 frame 之间(中英稿同步)。
- **Response (EN)**: The metric is a compositional counterfactual (Methods, line 205), not a deceptive-retirement measure; the two frames at line 144 measure different objects and can both hold. Optional one-sentence clarifier bridging them; no substantive change.


## 置信度调低 / Lowered confidence

### 第 4 点:价格与质量的关系 / Point 4: price-quality relationship(Granger 已迁移 / relocated)

- **指控(调低后)**: 价格与质量的相关可能被加密市场周期混杂;Granger 结论脆弱。
- **锚点**: `manuscript.tex:79`(首选规格为一阶差分 OLS, "the credible specification for non-stationary series");Granger 已从 Results 删除(原 :81),现仅存于补充材料、Methods `manuscript.tex:197` 与 FDR 清单 `manuscript.tex:209`;`manuscript.tex:197`(Methods 自认 "the small sample limits statistical power",周频 n=55);`manuscript.tex:120`(2022 年 5 月加密崩盘作为外生冲击, d=0.49 中等效应)。
- **预案回应**: 正文已把 Granger 降为探索性、把推断重心放在日频一阶差分回归(n=330),并主动用加密崩盘作外生冲击佐证渠道。回应口径:相关与回归是共变描述而非识别;周期混杂正是采用一阶差分与冲击事件设计的原因。已执行(2026-07-03):Granger 全部移入补充材料,正文仅保留一阶差分回归与加密崩盘冲击;Fig. 2 caption 同步改为按图实际内容描述(原 caption 误写 Granger)。
- **Response (EN)**: The text already treats Granger as exploratory ("consistent with", Supplementary), rests inference on the first-differenced daily regression, and uses the May 2022 crash as the exogenous check. Framing: descriptive co-movement, not identification. Pre-approved fallback: relocate all Granger material to Supplementary if requested.


*版本 / Version: 2026-07-04(洛基轮后;行号可能再度漂移,以 grep 原句为准)。*
