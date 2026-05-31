---
name: xuanyin-bazi
description: |
  玄音八字 — 自包含八字命理分析引擎。玄之又玄，音韵悠长。支持：八字排盘、综合命理报告、黄历查询、八字反查。
  当用户要求：算命、八字、命理分析、排盘、看运势、黄历、择日、查八字时使用。
metadata:
  trigger: 八字、算命、命理、排盘、运势、黄历、择日、bazi、fortune、玄音
  version: 2.0
allowed-tools: Bash, Read
---

# 玄音八字 (Xuanyin-Bazi): 八字命理分析引擎

## 核心原则

1. **一步出报告** — 默认使用 `--action report`，脚本直接输出完整Markdown报告，AI只需呈现
2. **客观呈现** — 如实展示八字数据，不夸大不隐瞒
3. **辩证解读** — 十神/神煞/刑冲合会综合考量，吉凶相依
4. **尊重隐私** — 不追问敏感个人信息，出生时间精确到时辰即可

## 快速使用

> **核心命令**：`--action report` 一步输出完整命理报告（含排盘+解读+大运），无需AI二次推理

```bash
# 综合命理报告（推荐，一步到位）
python {{current_skill_dir_path}}/scripts/main.py --action report --gender 1 --datetime "1990-06-15T12:00:00+08:00"

# 黄历查询
python {{current_skill_dir_path}}/scripts/main.py --action huangli

# 八字反查
python {{current_skill_dir_path}}/scripts/main.py --action reverse --bazi "庚午 壬午 辛亥 甲午"
```

## 执行流程

### Step 1：解析用户输入

从用户消息中提取：
- **性别**：男→1，女→0
- **出生时间**：转为ISO格式 `YYYY-MM-DDTHH:MM:SS+08:00`

| 用户说法 | 转换 |
|----------|------|
| "1990年6月15日中午12点" | `1990-06-15T12:00:00+08:00` |
| "1990-06-15 12:00" | `1990-06-15T12:00:00+08:00` |
| "下午3点" → 15点 | `...T15:00:00+08:00` |

**时辰对照**：子23-1 丑1-3 寅3-5 卯5-7 辰7-9 巳9-11 午11-13 未13-15 申15-17 酉17-19 戌19-21 亥21-23

### Step 2：运行脚本，直接呈现

**综合命理**（默认）：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action report --gender <0或1> --datetime "<ISO时间>"
```
脚本直接输出完整Markdown报告，AI**原样呈现**即可，无需额外解读。

**黄历查询**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action huangli --datetime "<ISO时间>"
```

**八字反查**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action reverse --bazi "<年柱> <月柱> <日柱> <时柱>"
```

**仅排盘**（不要解读时）：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action bazi --gender <0或1> --datetime "<ISO时间>"
```

## report 输出内容

`--action report` 一次性输出以下全部内容：

| 章节 | 内容 |
|------|------|
| 基础信息 | 性别/阳历/八字/生肖/日主 |
| 四柱详析 | 天干/五行/十神/地支/藏干/纳音 |
| 五行统计 | 各五行次数 + 最旺最弱 |
| 日主旺衰 | 得令/失令 + 偏旺/偏弱/中和 + 用神方向 |
| 格局 | 十神格局判定 |
| 性格倾向 | 日主五行性格 + 主要十神特征 |
| 事业方向 | 十神取象 + 五行取行业 |
| 财运分析 | 正偏财 + 食伤生财 + 身旺身弱判断 |
| 感情婚姻 | 配偶宫十神 + 刑冲警示 |
| 健康提示 | 五行偏枯 + 对应脏腑 |
| 神煞 | 四柱神煞 + 重点解读 |
| 刑冲合会 | 四柱间冲合刑关系 |
| 大运走势 | 十步大运表 |
| 当前运势 | 当前大运 + 流年分析 |

## 使用场景

### 场景1：综合命理（最常用）

**用户**："帮我分析一下：男，1990年6月15日中午12点"

**执行**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action report --gender 1 --datetime "1990-06-15T12:00:00+08:00"
```
→ 直接呈现脚本输出的Markdown报告

### 场景2：黄历查询

**用户**："今天适合搬家吗？"

**执行**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action huangli
```

### 场景3：八字反查

**用户**："八字庚午壬午辛亥甲午对应什么时间？"

**执行**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action reverse --bazi "庚午 壬午 辛亥 甲午"
```

## 注意事项

| 事项 | 说明 |
|------|------|
| 早晚子时 | `--early-zi 1`表示23-24点日干支取次日，`--early-zi 2`表示取当日，默认2 |
| 时辰精度 | 出生时间最好精确到时辰（2小时），否则时柱可能有误 |
| 命理局限 | 八字为传统文化，解读仅供参考，不做绝对论断 |
| 隐私保护 | 不存储用户出生信息，每次分析需重新输入 |
| 依赖安装 | 首次使用需 `pip install -r {{current_skill_dir_path}}/scripts/requirements.txt` |
