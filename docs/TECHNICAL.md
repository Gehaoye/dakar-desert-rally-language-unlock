# 技术细节

记录这个补丁的完整技术路径，供后来者复用或改造。

## 1. 游戏与 pak 结构

| 项 | 值 |
|---|---|
| 游戏 | Dakar Desert Rally（**Epic Games Store 版，本文全部实测数据来自该版本**；Steam appid 1839940，目录结构相同） |
| 引擎 | Unreal Engine 4 |
| 安装目录结构 | `DakarDesertRally/{Dakar2Game,Engine}` |
| pak 数量 | 10 个，合计约 56 GB |
| 主 pak | `Dakar2Game/Content/Paks/pakchunk0-WindowsNoEditor.pak`（11,752 MB） |
| pak 内文件总数 | 117,517 |

`repak info` 给出的元数据（打包必须对齐）：

```
mount point: ../../../
version: V11
version major: Fnv64BugFix
encrypted index: false
encryption guid: Some(00000000000000000000000000000000)
compression: Oodle ,Zlib
path hash seed: Some(69FFE8B3)
```

## 2. 文本表定位

游戏**没有**使用 UE4 标准的 `.locres` 本地化系统。`pakchunk0` 里能找到的 `.locres`
全部属于引擎层（`Engine/Content/Localization/...`）和在线子系统插件。

真正的游戏文本是三个自定义格式的纯文本文件：

```
Dakar2Game/Content/Database/FFTranslation/
├── EFFLanguage.txt        200 B，11 行
├── FFMessageLanguage.txt  3.4 MB，38,294 行
└── FFTextLanguage.txt     754 KB，12,808 行
```

## 3. 文本格式

- 编码：**UTF-8 with BOM**（`EF BB BF`）
- 行尾：**混用 CRLF 与 LF**，处理时必须逐行保留原始行尾，否则会破坏文件
- 字段分隔符：自定义字符串 **`<!sp!>`**（不是 tab，也不是逗号）

### EFFLanguage.txt

两字段：`语言ID<!sp!>语言名`

```
1<!sp!>English
10<!sp!>Chinese (Simplified)
```

### FFMessageLanguage.txt

五字段（末字段常为空）：`行ID<!sp!>文本ID<!sp!>语言ID<!sp!>文本<!sp!>`

```
3204<!sp!>1<!sp!>1<!sp!>MAIN MENU<!sp!>
32246<!sp!>1<!sp!>10<!sp!>主菜单<!sp!>
```

### FFTextLanguage.txt

四字段：`行ID<!sp!>文本ID<!sp!>语言ID<!sp!>文本`

```
37681<!sp!>6589<!sp!>1<!sp!>CAP 1.
49032<!sp!>6589<!sp!>10<!sp!>CAP 1。
```

**同一个 `文本ID` 出现多次，每次对应一个 `语言ID`**。这就是解锁的关键：
数据按语言分槽存放，UI 只是不给某些槽位入口。

## 4. 语言 ID 对照

| ID | 语言 | UI 可选 |
|---|---|---|
| 1 | English | ✅ |
| 2 | Portuguese | ✅ |
| 3 | French | ✅ |
| 4 | German | ✅ |
| 5 | Polish | ❌ |
| 6 | Spanish | ✅ |
| 7 | Italian | ✅ |
| 8 | PortugueseBR | ✅ |
| 9 | Japanese | ❌ |
| **10** | **Chinese (Simplified)** | ❌ |
| 11 | Russian | ❌ |

UI 暴露的 7 种，与 Steam 商店页标注的 7 种语言完全一致。**中文数据齐全，只是没有入口。**

## 5. 解锁原理

把语言 ID `10` 的文本写入语言 ID `1`（English）的槽位。游戏选 English 时：

- 界面文本 → 读到中文
- 语音包 → 仍按 English 加载

### 实测结论（Epic 版，2026-10 验证）

| 项目 | 读取路径 | 结论 |
|---|---|---|
| 主菜单 / UI 页面 | English 槽位 | ✅ 写 English 槽位即生效 |
| 游戏内页面 | English 槽位 | ✅ 同上 |
| 字幕 | English 槽位 | ✅ 同上 |
| 语音 | Language 设置 | 保持 English 即英文配音 |

**只写 English(1) 这一个槽位就够了**，不需要动 French 等其他槽位，也不需要改游戏内任何语言设置——进游戏保持默认 English，界面、页面、字幕即全为中文。

### ⚠️ 语言设置不要来回切

游戏自身有语言缓存机制，反复切换 `Language` / `Subtitle Language` 会让界面语言"粘住"：切到别的语言再切回来，界面可能仍停在旧语言，或者只有部分界面刷新。**这是游戏的问题，不是补丁的问题**，但表现上很像补丁失效。

换语言请改 `SRC_LANG` 重新生成 pak 覆盖安装，不要靠游戏内切换。

### 两个语言设置的分工（实测）

| 设置 | 控制 |
|---|---|
| `Language` | 语音；字幕也读它对应的槽位 |
| `Subtitle Language` | 界面 / 页面 |

当两者都是 English 时，全部文本走 English 槽位，所以**补丁只要写 English 槽位，默认设置下即可全中文**。

这就是"中文界面 + 英文语音"的由来。

> ⚠️ **不建议改 `TARGET_LANG`。** 固定写 English(1) 槽位，配合游戏默认设置即可全部生效；改到其他槽位要额外改游戏设置，且容易触发语言状态错乱。

## 6. 为什么必须打成 pak

| 尝试 | 结果 |
|---|---|
| 把 txt 放到 `Dakar2Game/Content/Database/FFTranslation/`（散文件） | ❌ 游戏忽略，仍读 pak |
| 改 ini 里的 `Culture` / `Language` | ❌ 配置里根本没有这些字段 |
| 打 `_P.pak` patch 包 | ✅ 生效 |

UE4 的散文件优先级在这里不成立，因为游戏通过 pak 挂载点访问，不走文件系统回退。

## 7. `_P` patch pak 机制

`pakchunk0-WindowsNoEditor_P.pak` 中的 **`_P` 后缀**是 UE4 官方热修约定：
加载优先级高于同名的普通 pak，会覆盖其中同名文件的内容。

所以补丁只有 **3.9 MB**，却能让 11.5 GB 的原包"换掉"两个文件。
原 pak 一个字节都不修改，删除 `_P.pak` 即刻恢复原版。

## 8. 打包参数

```bash
repak pack \
  --version V11 \
  --mount-point ../../../ \
  --path-hash-seed 1778378931 \
  <输入目录> <输出.pak>
```

### 两个坑

**坑一：`--path-hash-seed` 要十进制**

`repak info` 打印的是十六进制 `Some(69FFE8B3)`，但 `repak pack` 只接受十进制，
直接填 `69FFE8B3` 会报：

```
error: invalid value '69FFE8B3' for '--path-hash-seed': invalid digit found in string
```

正确值是 `0x69FFE8B3 = 1778378931`。

**坑二：Oodle 解压库**

pak 用 Oodle 压缩，`repak` 需要一个 `oo2core_9_win64.dll`，且**必须与 repak.exe 同目录**。

源码逻辑（`repak/oodle_loader/src/lib.rs`）：

```rust
let oodle_path = std::env::current_exe()?.with_file_name("oo2core_9_win64.dll");
if !oodle_path.exists() {
    // 自动从 GitHub 下载 —— 国内通常失败
    let buffer = ureq::get(&url()).call()?...
}
```

国内网络下自动下载会报 `ureq error Timeout(Global)` 或 `ConnectionReset`，
需手动放置 DLL。获取地址：

```
https://github.com/WorkingRobot/OodleUE
  → Engine/Source/Programs/Shared/EpicGames.Oodle/Sdk/2.9.10/win/redist/oo2core_9_win64.dll
```

## 9. 输入目录结构

`repak pack` 的目标目录结构必须与 pak 内路径一致（相对 mount point）：

```
<输入目录>/
└── Dakar2Game/
    └── Content/
        └── Database/
            └── FFTranslation/
                ├── FFMessageLanguage.txt
                └── FFTextLanguage.txt
```

打包后用 `repak list` 验证，应输出：

```
Dakar2Game/Content/Database/FFTranslation/FFMessageLanguage.txt
Dakar2Game/Content/Database/FFTranslation/FFTextLanguage.txt
```

## 10. 调试命令速查

```bash
# pak 元数据（拿 mount point / version / path hash seed）
repak info pakchunk0-WindowsNoEditor.pak

# 列出全部文件（11.7 万条，可管道过滤）
repak list pakchunk0-WindowsNoEditor.pak | Select-String "FFTranslation"

# 取单个文件到 stdout（重定向保存，注意用 cmd /c 保持二进制安全）
repak get pakchunk0-WindowsNoEditor.pak "Dakar2Game/Content/Database/FFTranslation/FFTextLanguage.txt" > out.txt

# 验证新 pak
repak list pakchunk0-WindowsNoEditor_P.pak
```

## 11. 中文覆盖情况

| 文件 | 条目 | 有官方中文 | 覆盖率 |
|---|---|---|---|
| FFMessageLanguage.txt | 5,525 | 3,789 | 68.6% |
| FFTextLanguage.txt | 1,299 | 1,255 | 96.6% |

缺少的 1,736 条（`FFMessageLanguage`）逐条核对构成：

| 类别 | 条数 |
|---|---|
| 车队 / 厂商 / 代号（不应翻译） | 869 |
| 数字 / 空值 / 字间距排版标题 | 527 |
| 车手访谈与生平介绍（背景资料页） | 340 |

`FFTextLanguage.txt` 缺的 44 条是**领航员路书指令**，属于真正影响驾驶体验的内容，
已在脚本内用中文拉力赛标准术语补齐 43 条（`特殊赛段`、`中立化`、`发夹弯`、`时间控制点` 等）。

## 12. 字体

游戏已内置中文字形，无需处理字体：

```
Dakar2Game/Plugins/Game/DakarGame/Content/UMG2/Fonts/NotoSans/EXTRA_Languages/
├── NotoSansSC-Regular.ufont   ← 简体中文
└── NotoSansSC-Bold.ufont
```

同目录还有 JP / KR / Thai / Bengali / Devanagari 字体。这也是为什么中文能直接显示，
不会出现方块或空白。
