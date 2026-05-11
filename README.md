# 馃 AI 澶栬锤瀹㈡埛寮€鍙?Agent

> 鍩轰簬 QwenPaw 澶氭櫤鑳戒綋妗嗘灦鏋勫缓鐨?B2B 澶栬锤鑷姩鍖栧姪鎵嬧€斺€斾粠瀹㈡埛鑳岃皟銆侀偖浠剁敓鎴愬埌 Gmail 鍙戦€侊紝鍏ㄩ摼璺嚜鍔ㄥ寲銆?

## What It Does | 鑳藉姏

```
瀹㈡埛鍚嶅崟 鈫?Deep Research 鑳岃皟 鈫?Gemini 鐢熸垚閭欢 鈫?QQ瀹℃牳 鈫?Gmail鍙戦€?
   鈫?           鈫?                   鈫?             鈫?          鈫?
  杈撳叆        79涓暟鎹簮          涓嫳瀵圭収         浜哄伐纭    鑷姩鍙戜欢
```

| Step | Action | Tool |
|:---:|--------|------|
| 鈶?| 瀹㈡埛鑳岃皟 | Gemini Deep Research锛?9+ sources锛?|
| 鈶?| 閭欢鐢熸垚 | Gemini "寮€鍙戦偖浠? Gem锛圗N + CN锛?|
| 鈶?| QQ瀹℃牳 | Gmail 鈫?QQ閭锛堜腑鑻卞鐓э級 |
| 鈶?| 浜哄伐纭 | 瀹℃牳鍚庣偣"纭" |
| 鈶?| 鍙戦€佸鎴?| Gmail锛堢函鑻辨枃锛岃嚜鍔ㄧЩ闄よ拷韪彃浠讹級 |

## Real Cases | 瀹炴垬妗堜緥

### Case 1: Mextech Technologies (India)
- **瀹㈡埛**: 鍗板害瀛熶拱锛屽勾钀ユ敹 180 涓?USD锛屼粠涓浗 OEM 璐寸墝
- **鍙戠幇**: 渚涘簲閾句笌 ZOYI 鍏宠仈锛岀己 CAT IV 宸ヤ笟绾т骇鍝?
- **鍒囧叆**: DM102 True RMS DMM + VC17B+锛孊IS 璁よ瘉鏀寔

### Case 2: Pribor-Universal (Russia)
- **瀹㈡埛**: 淇勭綏鏂湥褰煎緱鍫★紝270 鎵规杩涘彛/65+ 渚涘簲鍟?
- **鍙戠幇**: AB Universal锛堝埗瑁侊級鈮?Pribor Universal锛屽悎瑙勫畨鍏?
- **鍒囧叆**: WILK316/317 鐒婂彴鏇夸唬 ATTEN + OEM 璐寸墝

## Tech Stack | 鎶€鏈爤

| Layer | Technology |
|-------|-----------|
| Agent Framework | QwenPaw Multi-Agent |
| Browser Automation | Playwright + CDP |
| Deep Research | Gemini Deep Research |
| Email Generation | Gemini Custom Gem |
| Email Sending | Gmail + URL Parameter |

## Architecture | 鏋舵瀯

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? QwenPaw     鈹傗攢鈹€鈹€鈻垛攤  Gemini      鈹傗攢鈹€鈹€鈻垛攤  Gmail       鈹?
鈹? Agent       鈹?   鈹? DeepResearch鈹?   鈹? (User Chrome鈹?
鈹? Orchestrator鈹?   鈹? + Email Gem 鈹?   鈹?  + CDP)     鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
       鈹?                  鈹?                  鈹?
       鈻?                  鈻?                  鈻?
   璇诲彇瀹㈡埛淇℃伅         鐢熸垚閭欢鍐呭          鑷姩鍙戦€?绉婚櫎杩借釜
```

## Key Features | 鏍稿績浜偣

- 鉁?**鍏ㄩ摼璺嚜鍔ㄥ寲**锛氫粠杈撳叆瀹㈡埛鍒伴偖浠跺彂閫侊紝涓€閿Е鍙?
- 鉁?**Deep Research**锛?9+ 鏁版嵁婧愭繁搴﹁儗璋冿紙璐㈠姟銆佹捣鍏炽€佸埗瑁佸悕鍗曪級
- 鉁?**涓嫳鍙岃**锛氱敓鎴愬鐓х増鏈紝浜哄伐瀹℃牳鍚庡彂閫?
- 鉁?**Mailsuite 鑷姩绉婚櫎**锛氭娴嬪苟鍏抽棴閭欢杩借釜鎻掍欢
- 鉁?**鍚堣浼樺厛**锛氳嚜鍔ㄦ牳鏌?OFAC SDN 鍒惰鍚嶅崟
- 鉁?**鍒嗘壒澶勭悊**锛氶暱閭欢鑷姩鍒嗘鍙戦€?

## Getting Started | 浣跨敤

```bash
# 瑙﹀彂璇嶏紙瀵?Agent 璇达級
"璧版祦绋? 鎴?"鎸夋祦绋嬬敓鎴愬紑鍙戦偖浠?
```

Agent 鑷姩璇诲彇 `skills/dev_email_flow/SKILL.md` 骞舵墽琛屽叏閾捐矾銆?

## File Structure | 鏂囦欢缁撴瀯

```
skills/dev_email_flow/SKILL.md    # 瀹屾暣鑷姩鍖栨祦绋?
MEMORY.md                          # Agent 闀挎湡璁板繂锛堢粡楠屾暀璁級
memory/*.md                        # 姣忔棩浠诲姟璁板綍
```

## Author | 浣滆€?

澶栬锤鑷姩鍖栧疄璺甸」鐩紝鍩轰簬 QwenPaw 妗嗘灦鏋勫缓銆?

---

*Built with QwenPaw Multi-Agent Framework*
