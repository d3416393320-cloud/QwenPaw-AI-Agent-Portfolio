# 澶栬锤寮€鍙戦偖浠惰嚜鍔ㄥ寲娴佺▼锛坉ev_email_flow锛?

> 馃 QwenPaw AI Agent 鈥?B2B 瀹㈡埛寮€鍙戝叏閾捐矾鑷姩鍖? 
> 瑙﹀彂璇嶏細"璧版祦绋? / "鎸夋祦绋嬬敓鎴愬紑鍙戦偖浠?

---

## 瀹屾暣娴佺▼锛?姝ワ級

### 绗?0 姝?- 璇诲彇鏈湴璐﹀彿
- 璇诲彇 `accounts.json` 鑾峰彇 Gemini 璐﹀彿瀵嗙爜
- 濡傛灉鏈櫥褰曪紝鍏堢敤 headed 娴忚鍣ㄦ墦寮€ gemini.google.com 鐧诲綍

### 绗?1 姝?- 瀹㈡埛鑳岃皟锛堝紑鍙戝鎴峰埄鍣?Gem锛?
- 鎵撳紑鑷畾涔?Gem锛屼笂浼犲鎴蜂俊鎭枃浠舵垨绮樿创鏂囨湰
- 鍚敤 **Deep Research** 妯″紡锛屾繁搴︽帰绱細
  ```
  璇蜂负浠ヤ笅瀹㈡埛鍋氭繁搴﹀晢涓氳儗璋冿紝鍖呭惈锛?
  1. 涓昏惀涓氬姟涓庨噰璐亸濂?
  2. 浜у搧闇€姹傛柟鍚戯紙瀵规爣鍨嬪彿锛?
  3. 鏍稿績鍏虫敞鐐癸紙鍒╂鼎銆佸寘瑁呫€佽繘鍙ｈ儗鏅瓑锛?
  4. 鎺ㄨ崘鍖归厤浜у搧鍙婄悊鐢?
  瀹㈡埛淇℃伅锛歔绮樿创鎴栨枃浠禲
  ```
- 杈撳嚭淇濆瓨鑷?`memory/鑳岃皟_瀹㈡埛鍚峗鏃ユ湡.txt`

### 绗?2 姝?- 鐢熸垚寮€鍙戦偖浠讹紙寮€鍙戦偖浠?Gem锛?
- 鎵撳紑鑷畾涔?Gem锛岀矘璐磋儗璋冪粨鏋?
- 鎸囦护妯℃澘锛?
  ```
  鍩轰簬浠ヤ笅鑳岃皟淇℃伅锛岀敓鎴愯嫳鏂囧紑鍙戦偖浠讹細
  - 鑻辨枃鐗堝彲鐩存帴澶嶅埗鍙戦€侊紝闄勫甫涓枃瀵圭収鐗?
  - 鍖呭惈瀹㈡埛閭銆佷富棰樿
  - 瀹氫綅涓?楂樺埄娑﹁ˉ鍏呯嚎"锛岄潪鏇夸唬鐜版湁鍝佺墝
  鑳岃皟淇℃伅锛歔绮樿创绗?姝ョ粨鏋淽
  ```

### 绗?3 姝?- 鍙慟Q閭纭
- 鐢?Gmail URL 鍙傛暟娉曟墦寮€鎾板啓锛?
  ```
  https://mail.google.com/mail/?view=cm&fs=1&to=your-qq@qq.com&su=寮€鍙戦偖浠?瀹㈡埛鍚?Gemini鐢熸垚
  ```
- 鈿狅笍 QQ 纭閭欢**蹇呴』鍖呭惈瀹屾暣涓嫳鏂囧鐓?*
- 姝ｆ枃瓒?2000 瀛楁椂鍒嗘壒鍙戦€侊紝鏍囨敞 `[1/N]`

### 绗?4 姝?- 绛夊緟鐢ㄦ埛纭
- 鐢ㄦ埛璇?纭"鎴?鍙? 鈫?杩涘叆涓嬩竴姝?
- 鐢ㄦ埛璇?鏀箈x" 鈫?淇敼鍚庨噸鏂扮‘璁?

### 绗?5 姝?- Gmail 鍙戦€佺粰瀹㈡埛

#### 5a. 杩炴帴鐢ㄦ埛 Chrome锛堝甫 Mailsuite 鎵╁睍锛?
```
鍏?stop 褰撳墠娴忚鍣?鈫?taskkill /f /im chrome.exe
鍚姩: chrome.exe --user-data-dir=... --profile-directory="Default" --remote-debugging-port=9222
connect_cdp 鈫?cdp_url="http://127.0.0.1:9222"
```

#### 5b. 鎵撳紑鎾板啓绐楀彛
```
https://mail.google.com/mail/?view=cm&fs=1&to=瀹㈡埛閭&su=鑻辨枃涓婚
```
- 濉叆鑻辨枃鐗堟鏂囷紙鈿狅笍 鍙彂鑻辨枃鐗堢粰瀹㈡埛锛?

#### 5c. 鍙夋帀 Mailsuite 鎻掍欢
- Mailsuite 鏍囪瘑鍑虹幇鍦?*姝ｆ枃妗嗗唴閮?*
- 姝ラ锛?
  1. 鐐瑰嚮 **`button.mt-remove`**锛圕SS 閫夋嫨鍣級
  2. 寮瑰嚭鍗囩骇瀵硅瘽妗嗗悗鐐瑰嚮 **"Skip for now"**
- 纭 "Help me write" 涔熷叧闂悗鍐嶇偣 Send

---

## Gmail URL 鍙傛暟娉曢€熸煡

```
https://mail.google.com/mail/?view=cm&fs=1&to=鏀朵欢浜?su=涓婚&body=姝ｆ枃
```

**鍏抽敭鍘熷垯锛氫笉鐐?Compose 鎸夐挳锛屾案杩滅敤 URL 鍙傛暟娉曪紒**

---

## 甯歌闂

| 闂 | 瑙ｆ硶 |
|------|------|
| Gemini 1099 閿欒 | 鏂囦欢澶ぇ 鈫?鎻愬彇鏂囨湰鍚庣矘璐?|
| Gmail Compose 鐐逛笉鍔?| 姘歌繙鐢?URL 鍙傛暟娉?|
| Mailsuite 鎻掍欢 | 姝ｆ枃妗嗗唴 鈫?`button.mt-remove` + "Skip for now" |
| 杩炴帴鐢ㄦ埛 Chrome | 鏉€杩涚▼ 鈫?`--remote-debugging-port=9222` 鈫?`connect_cdp` |
| 鍐呭澶暱 | 鍒嗘壒鍙戦€侊紝鏍囨敞 `[1/N]` |

---

## 瀹炴垬妗堜緥

### Case 1: Mextech Technologies (India) 馃嚠馃嚦
- 骞磋惀鏀?180 涓?USD锛屼粠涓浗 OEM 璐寸墝 Mextech 鍝佺墝
- Deep Research 鍙戠幇锛氫緵搴旈摼涓?ZOYI 鍏宠仈锛岀己 CAT IV 宸ヤ笟绾т骇鍝?
- 鍒囧叆鐐癸細DM102 True RMS DMM + VC17B+ + BIS 璁よ瘉鏀寔

### Case 2: Pribor-Universal (Russia) 馃嚪馃嚭
- 270 鎵规杩涘彛 / 65+ 渚涘簲鍟嗭紝姝ｄ粠浠ｇ悊鍚戣嚜鏈夊搧鐗?OEM 杞瀷
- Deep Research 鍙戠幇锛欰B Universal锛堝埗瑁佸悕鍗曪級鈮?Pribor Universal锛屽悎瑙勫畨鍏?
- 鍒囧叆鐐癸細WILK316/317 鐒婂彴鏇夸唬 ATTEN + OEM 璐寸墝 + 淇勮鏂囨。

---

*Built with QwenPaw Multi-Agent Framework*
