# 达喀尔赛车拉力赛（Dakar Desert Rally-epic平台版本语言包解锁-中文为例-可自行探索日语、俄语）

![platform](https://img.shields.io/badge/platform-Windows%20·%20Epic%20Games%20Store-0078D4)
![engine](https://img.shields.io/badge/engine-Unreal%20Engine%204-lightgrey)

**游戏自带官方中文，但语言菜单里不显示。本补丁把中文解锁出来。**

装完效果：

| 项目 | 结果 |
|---|---|
| 主菜单 / 界面 | **中文** |
| 游戏内页面 | **中文** |
| 字幕 | **中文** |
| 语音 | **英文** |

**进游戏什么都不用设置，保持默认就行。**

---

## 怎么用

### 第一步：拿到补丁文件

`pakchunk0-WindowsNoEditor_P.pak`（约 4 MB），在 [Releases](../../releases) 里下载。

### 第二步：放进游戏目录

复制到这个路径：

```
D:\EpicGames\DakarDesertRally\Dakar2Game\Content\Paks\
```

两点注意：

- 目录里原本的 10 个 pak **一个都不要删、不要改**
- 补丁文件名必须是 `pakchunk0-WindowsNoEditor_P.pak`（大小写完全一致）

### 第三步：启动游戏

**保持默认的 English 不要动。**主菜单、游戏内页面、字幕全是中文，语音是英文。

完成。

---

## 卸载

删掉 `pakchunk0-WindowsNoEditor_P.pak` 这一个文件，游戏立刻恢复原版。

原 `pakchunk0-WindowsNoEditor.pak`（11.5 GB）从未被修改。

---

## 想要日语或俄语

仓库里的脚本可以自己生成补丁。改 `scripts/unlock.py` 开头这一个常量：

```python
SRC_LANG = "10"    # 10=中文, 9=日语, 11=俄语
```

重新跑一遍脚本，生成新 pak，覆盖安装。

**`TARGET_LANG` 保持 `"1"` 不要改。**

自建需要的环境（Python 3.8+、repak、`oo2core_9_win64.dll`）见 [docs/TECHNICAL.md](docs/TECHNICAL.md)。

---

## 各语言数据完整度

| 语言 | ID | 界面文本 | 路书文本 | 能否解锁 |
|---|---|---|---|---|
| English | 1 | 99.9% | 100% | — |
| **中文（简体）** | **10** | **68.6%** | **96.6%** | ✅ 本补丁目标 |
| **日语** | **9** | **87.5%** | **96.6%** | ✅ 覆盖最高 |
| 俄语 | 11 | 68.7% | 96.6% | ✅ |
| 波兰语 | 5 | **0%** | **0%** | ❌ 无任何数据 |

> 中文缺的 31% 是车队名、厂商名、车手代号、纯数字和排版符号，不影响游玩。路书和界面基本全覆盖。

---

## ⚠️ 已知问题：不要反复切换语言选项

**这是游戏自身的 bug，与本补丁无关**（已实测：删掉补丁后问题依然存在）。

**症状**：语言下拉框里少了一项（最常见是 English 消失），或者界面语言切了不生效。

**原因**：反复切换 `Language` / `Subtitle Language` 会让游戏把异常值写进存档（如 `DKLanguage::Italian`），UI 拿这个值渲染下拉框时失败。游戏没有提供恢复默认的入口。

**修复**：退出游戏后运行附带脚本，会自动备份再修正存档：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fix-language-save.ps1
```

**预防**：装完补丁保持默认 English，不要来回切语言。

---

## ⚠️ 适用范围

**实测平台**：Epic Games Store 版 Dakar Desert Rally（Windows）。

Steam 版（appid 1839940）目录结构相同、原理一致，但**未做实测验证**。

---

## 原理

游戏的 pak 里打包了 **11 种语言**，简体中文（ID 10）是**官方成品**，共 3,789 条界面文本 + 1,255 条路书文本，带完整标点本地化。

但界面语言菜单被写死只暴露 7 种（English / Portuguese / French / German / Spanish / Italian / PortugueseBR），中文、日语、俄语、波兰语都被过滤掉了。

**本补丁不翻译、不修改游戏本体**：它把游戏自带的官方中文写进 **English 槽位**。English 是游戏默认语言且会被正常读取，所以装完什么都不用设置。

技术上走 UE4 官方的 `_P` patch pak 机制（同名文件覆盖，优先级高于原包），删掉即回滚。

技术细节见 [docs/TECHNICAL.md](docs/TECHNICAL.md)：pak 结构、`<!sp!>` 文本格式、`path hash seed` 十进制坑、Oodle DLL 坑。

---

## ⚠️ 版权与免责

- 本仓库**不包含任何游戏资源**。补丁 pak 由脚本在本地从使用者自己的游戏文件中生成
- 游戏资源版权归 **Saber Interactive / Saber Porto** 所有，本项目与其无任何关联
- 不绕过 DRM、不修改可执行文件、不做内存注入
- 仅供个人学习研究使用，请在下载后 24 小时内删除
- 使用风险自负，因使用本工具造成的任何后果由使用者自行承担

---

## 致谢

- [repak](https://github.com/trumank/repak) — UE4 pak 读写（Apache-2.0 / MIT）
- [OodleUE](https://github.com/WorkingRobot/OodleUE) — Oodle 库分发
- [DeepSeek](https://www.deepseek.com/) — 全程使用的推理模型（DeepSeek-V4.1-Flash），从 pak 结构分析、文本格式逆向，到解锁脚本与本文档成稿

## License

MIT

---

<a name="english"></a>
## English

**Dakar Desert Rally — hidden language pack unlocker (Epic Games Store PC).**

The PC build ships with **11 localizations** inside its pak archives, but the in-game language menu only exposes 7. Simplified Chinese (ID 10), Japanese (ID 9) and Russian (ID 11) are fully present in the data and yet have no UI entry. Polish (ID 5) is defined in the language table but contains **zero** strings.

**Install**: copy `pakchunk0-WindowsNoEditor_P.pak` into `Dakar2Game\Content\Paks\` and launch. Nothing to configure — the game's default English slot now shows Chinese text while voice-over stays English.

**Uninstall**: delete that one file. The original 11.5 GB pak is never modified.

**This repository contains no game assets.** Everything is read from your own legally purchased copy at runtime.

Coverage: message table 68.6% (Chinese), roadbook 96.6% plus 43 hand-translated rally terms. The remaining 1,736 entries are team/manufacturer names, numbers and driver interviews the publisher never localized either.

### Credits

- [repak](https://github.com/trumank/repak) — UE4 pak tooling (Apache-2.0 / MIT)
- [OodleUE](https://github.com/WorkingRobot/OodleUE) — Oodle library redistribution
- [DeepSeek](https://www.deepseek.com/) — the reasoning model used throughout this project
