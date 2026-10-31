# 达喀尔赛车拉力赛（Dakar Desert Rally）Epic 版语言包解锁

> **以简体中文为例** · 日语 / 俄语 同理可解锁 · 波兰语数据为空（见下方说明）

![platform](https://img.shields.io/badge/platform-Windows%20·%20Epic%20%2F%20Steam-blue)
![engine](https://img.shields.io/badge/engine-Unreal%20Engine%204-lightgrey)
![python](https://img.shields.io/badge/python-3.8%2B-yellow)

---

## 这是什么

《达喀尔赛车拉力赛》（Dakar Desert Rally）PC 版的语言菜单只提供 7 种语言，**没有中文**。

但游戏的 pak 归档里实际打包了 **11 种语言**——简体中文、日语、俄语、波兰语都在里面，
只是 UI 从来没给它们入口。

**本工具不解包、不翻译、不修改游戏本体**：它把游戏自己藏着的那份语言包，
搬到某个可见语言的槽位上，让你能在菜单里选到它。

> 选 English → 界面变中文，语音仍是英文。
> 想换日语 / 俄语，改一个常量即可，方法完全一样。

---

## 语言数据实况（实测统计）

| ID | 语言 | 消息条目覆盖 | 文本条目覆盖 | UI 可选 | 解锁后效果 |
|---|---|---|---|---|---|
| 1 | English | 99.9% | 100% | ✅ | — |
| 2 | Portuguese | 61.3% | 99.1% | ✅ | — |
| 3 | French | 61.3% | 99.8% | ✅ | — |
| 4 | German | 61.3% | 99.1% | ✅ | — |
| 5 | **Polish** | **0.0%** | **0.0%** | ❌ | ⚠️ **无数据，解锁后无内容** |
| 6 | Spanish | 61.3% | 99.8% | ✅ | — |
| 7 | Italian | 61.3% | 99.1% | ✅ | — |
| 8 | PortugueseBR | 61.3% | 99.1% | ✅ | — |
| **9** | **Japanese** | **87.5%** | 96.6% | ❌ | ✅ 覆盖最高 |
| **10** | **Chinese (Simplified)** | **68.6%** | 96.6% | ❌ | ✅ 本补丁默认目标 |
| **11** | **Russian** | **68.7%** | 96.6% | ❌ | ✅ 可解锁 |

**为什么波兰语不行**：`EFFLanguage.txt` 里确实有 `5<!sp!>Polish` 的定义，
但两个文本表里语言 ID 5 的记录数是 **0**。游戏从来没做过波兰语文本，只有一条语言名占位。

---

## 使用方法（以中文为例）

### 需要准备

| 项 | 说明 |
|---|---|
| 游戏 | 正版 Dakar Desert Rally（Epic 版 / Steam 版目录结构相同） |
| Python | 3.8 或更高 |
| [repak](https://github.com/trumank/repak) | UE4 pak 读写工具，单文件约 2 MB |
| `oo2core_9_win64.dll` | Oodle 解压库，**必须与 repak.exe 放在同一目录** |

`oo2core_9_win64.dll` 获取地址（repak 自动下载在国内通常失败，需手动放置）：

```
https://github.com/WorkingRobot/OodleUE
  → Engine/Source/Programs/Shared/EpicGames.Oodle/Sdk/2.9.10/win/redist/oo2core_9_win64.dll
```

### 一条命令搞定

```bat
git clone https://github.com/<用户名>/dakar-desert-rally-language-unlock.git
cd dakar-desert-rally-language-unlock

python scripts/unlock.py ^
  --game "D:\EpicGames\DakarDesertRally" ^
  --repak "C:\tools\repak\repak.exe"
```

脚本自动完成：**提取游戏文本 → 中文搬到英文槽位 → 打包 patch pak → 放进游戏目录**。

启动游戏，**语言选 English**，界面就是中文。

### 想要日语或俄语？

改脚本顶部的两个常量（`scripts/unlock.py`，文件开头）：

```python
SRC_LANG = "10"    # 要解锁的语言: 10=中文, 9=日语, 11=俄语
TARGET_LANG = "1"  # 覆盖哪个可见槽位: 1=English, 3=French, 7=Italian ...
```

改成 `SRC_LANG = "9"` 就是日文，`"11"` 就是俄文，方法完全一致。
游戏内要选的语言项也跟着变——覆盖 English 就选 English，覆盖 French 就选 French。

### 卸载

删除这一个文件，游戏 100% 恢复原版：

```
Dakar2Game\Content\Paks\pakchunk0-WindowsNoEditor_P.pak
```

原 `pakchunk0`（11.5 GB）**一个字节都不会被修改**。

---

## 中文覆盖范围

| 内容 | 官方中文 |
|---|---|
| UI / 菜单 / 赛事文本（`FFMessageLanguage.txt`） | 3,789 / 5,525 条（68.6%） |
| 路书 / 领航员指令（`FFTextLanguage.txt`） | 1,255 / 1,299 条（96.6%） |
| 缺失路书的手工补译 | 43 条（特殊赛段、中立化、发夹弯、时间控制点等标准术语） |

缺失的 1,736 条消息逐条核对，构成如下：

| 类别 | 条数 | 是否需要翻译 |
|---|---|---|
| 车队 / 厂商 / 代号 | 869 | ❌ 专有名词 |
| 数字 / 空值 / 字间距排版标题 | 527 | ❌ 无需翻译 |
| 车手访谈与生平（背景资料页） | 340 | ⚠️ 官方原版也未做全本地化 |

**实际驾驶与操作界面中不会有英文残留。**

---

## 常见问题

**Q：会不会被封号 / 影响联机？**
A：只改本地资源文件，不改可执行文件、不碰 DRM、不做内存注入。但游戏若有反作弊，任何文件改动都可能被检测，风险自负。

**Q：游戏更新后失效怎么办？**
A：重新跑一遍脚本，几秒钟的事。若更新重构了文本系统（比如改用 `.locres`），脚本需相应调整。

**Q：为什么我改的散文件没用？**
A：这游戏只从 pak 读文本，不认 `Content/` 下的散文件（实测）。必须打包成 `_P.pak`。

**Q：主机版能用吗？**
A：不能。PS / Xbox 文件加密，本工具只支持 PC。

**Q：为什么中文只有 68.6%？**
A：剩下的是车队名、数字和车手访谈资料页，发行商自己就没做完整本地化。路书和界面是全覆盖的。

---

## 原理（技术细节）

详见 [`docs/TECHNICAL.md`](docs/TECHNICAL.md)：pak 结构、`<!sp!>` 文本格式、语言 ID 表、
UE4 `_P` patch pak 机制、`path hash seed` 的十进制坑、Oodle DLL 坑，全部记录在案。

核心三步：

1. `repak` 从 `pakchunk0` 取出三个明文文本表
2. 把语言 ID 10 的字符串写进语言 ID 1 的槽位
3. 打成 `pakchunk0-WindowsNoEditor_P.pak`——UE4 官方热修机制，加载优先级高于原 pak

补丁只有 **3.9 MB**，却能让 11.5 GB 的原包"换掉"两个文件。

---

## 法律声明

- 本仓库**不包含任何游戏资源**：没有文本、没有 pak、没有 DLL。全部数据在运行时从用户本机的正版游戏中读取。
- 请支持正版。本项目仅对本地文件做读取与重打包，不绕过 DRM、不修改可执行文件、不提供任何破解内容。
- 《达喀尔赛车拉力赛》（Dakar Desert Rally）及相关内容的版权归 **Saber Interactive / Saber Porto** 所有，本项目与其无任何关联。
- 使用风险自负，建议先备份存档。

---

## 致谢

- [repak](https://github.com/trumank/repak) — UE4 pak 读写（Apache-2.0 / MIT）
- [OodleUE](https://github.com/WorkingRobot/OodleUE) — Oodle 库分发
- 以及所有发现这个游戏把语言包藏起来的人

---

<a name="english"></a>
## English

**Dakar Desert Rally — hidden language pack unlocker (Epic / Steam PC).**

The PC build ships with **11 localizations** inside its pak archives, but the in-game language
menu only exposes 7. Simplified Chinese (ID 10), Japanese (ID 9) and Russian (ID 11) are fully
present in the data and yet have no UI entry. Polish (ID 5) is defined in the language table
but contains **zero** strings — there is nothing to unlock.

This tool copies the hidden language's strings over a visible language slot and repacks them
into a UE4 patch pak (`pakchunk0-WindowsNoEditor_P.pak`). Selecting that slot in-game then shows
the hidden language while keeping the original voice-over. The original 11.5 GB pak is never
modified; deleting the `_P.pak` fully restores the vanilla game.

**This repository contains no game assets.** Everything is read from your own legally purchased
copy at runtime.

```bat
python scripts/unlock.py --game "D:\EpicGames\DakarDesertRally" --repak "C:\tools\repak\repak.exe"
```

Defaults to Chinese over the English slot. Change `SRC_LANG` / `TARGET_LANG` at the top of
`scripts/unlock.py` for Japanese (`9`) or Russian (`11`).

Coverage: message table 68.6% (Chinese), roadbook 96.6% plus 43 hand-translated rally terms.
The remaining 1,736 entries are team/manufacturer names, numbers and driver interviews that the
publisher never localized either.
