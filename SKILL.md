---
name: xuanyin-bazi
description: |
  玄音八字 — 自包含八字命理分析引擎。玄之又玄，音韵悠长。支持：八字排盘、大运流年、神煞刑冲合会、黄历查询、八字反查公历时间等完整命理分析管线。
  当用户要求：算命、八字、命理分析、排盘、看运势、黄历、择日、查八字时使用。
metadata:
  trigger: 八字、算命、命理、排盘、运势、黄历、择日、bazi、fortune、玄音
  version: 1.1
allowed-tools: Bash, Read
---

# 玄音八字 (Xuanyin-Bazi): 八字命理分析引擎

## 核心原则

1. **客观呈现** — 如实展示八字数据，不夸大不隐瞒
2. **综合研判** — 多维度交叉分析，忌单一指标断论
3. **辩证解读** — 十神/神煞/刑冲合会综合考量，吉凶相依
4. **尊重隐私** — 不追问敏感个人信息，出生时间精确到时辰即可
5. **文化传承** — 以传统命理学为根基，结合现代视角解读

## 核心能力

| 能力 | 说明 |
|------|------|
| 八字排盘 | 公历/农历输入 → 四柱八字 + 日主 + 生肖 + 纳音 |
| 十神分析 | 天干十神 + 地支藏干十神 + 十神格局研判 |
| 大运推算 | 起运年龄 + 十步大运 + 每步干支/十神/年龄区间 |
| 神煞检索 | 年/月/日/时四柱神煞（天乙贵人、文昌、将星等） |
| 刑冲合会 | 天干冲/地支刑冲合害/暗合，全四柱交叉关系图 |
| 胎元命宫 | 胎元、胎息、命宫、身宫四柱延伸信息 |
| 黄历查询 | 任意日期 → 农历/干支/节气/宜忌/吉神方位/冲煞 |
| 八字反查 | 已知八字 → 反推所有可能的公历时间 |

## 计算引擎

所有命理计算由 `scripts/main.py` 完成，无需外部MCP服务。

| 动作 | 命令 | 说明 |
|------|------|------|
| 八字排盘 | `--action bazi` | 需要 `--gender` + `--datetime` |
| 黄历查询 | `--action huangli` | 可选 `--datetime`（默认今天） |
| 八字反查 | `--action reverse` | 需要 `--bazi` |

> 脚本路径: `{{current_skill_dir_path}}/scripts/main.py`

## 全流程管线

### Phase 1：需求采集

**目标**：获取用户分析所需的出生信息

**流程**：
1. 询问用户需要哪种分析服务（见下方服务类型表）
2. 根据服务类型收集必要信息
3. 确认输入无误后进入分析阶段

| 服务类型 | 必要信息 | 可选信息 |
|----------|----------|----------|
| 八字排盘 | 性别、出生时间（公历或农历） | 早晚子时配置 |
| 黄历查询 | 查询日期（默认今天） | 无 |
| 八字反查 | 四柱八字（如"庚午 壬午 辛亥 甲午"） | 无 |
| 综合命理 | 性别、出生时间 | 早晚子时配置 |

**时间输入规范**：
- **公历**：ISO格式 `YYYY-MM-DDTHH:MM:SS+08:00`（如 `1990-06-15T12:00:00+08:00`）
- **农历**：格式 `YYYY-M-D HH:MM:SS`（如 `1990-5-23 12:00:00` 表示农历1990年五月廿三午时）
- **时辰对应**：子时23-1点、丑时1-3点、寅时3-5点、卯时5-7点、辰时7-9点、巳时9-11点、午时11-13点、未时13-15点、申时15-17点、酉时17-19点、戌时19-21点、亥时21-23点

### Phase 2：数据获取

**目标**：调用计算脚本获取原始命理数据

**前置条件**：确保已安装依赖 `pip install -r {{current_skill_dir_path}}/scripts/requirements.txt`

#### 2A：八字排盘 / 综合命理

```bash
python {{current_skill_dir_path}}/scripts/main.py \
  --action bazi \
  --gender <0或1> \
  --datetime "<ISO时间>" \
  --early-zi <1或2>
```

**示例**：
```bash
python {{current_skill_dir_path}}/scripts/main.py \
  --action bazi \
  --gender 1 \
  --datetime "1990-06-15T12:00:00+08:00"
```

**返回数据结构**：
- 基本信息：性别、阳历、八字、生肖、日主、日主五行
- 四柱详情：年柱/月柱/日柱/时柱，每柱含天干（天干/五行/阴阳/十神）、地支（地支/五行/阴阳/藏干含主气中气余气及十神）、纳音、神煞
- 五行统计：木/火/土/金/水各出现次数
- 大运：起运年龄 + 十步大运（干支/起止年份/年龄区间）
- 刑冲合会：四柱间天干冲/地支刑冲合害关系图

#### 2B：黄历查询

```bash
python {{current_skill_dir_path}}/scripts/main.py \
  --action huangli \
  --datetime "<ISO时间>"
```

**示例**：
```bash
python {{current_skill_dir_path}}/scripts/main.py --action huangli
python {{current_skill_dir_path}}/scripts/main.py --action huangli --datetime "2026-05-31T00:00:00+08:00"
```

**返回数据结构**：
- 公历/农历/干支/生肖/节气
- 财神方位/宜/忌

#### 2C：八字反查

```bash
python {{current_skill_dir_path}}/scripts/main.py \
  --action reverse \
  --bazi "<年柱> <月柱> <日柱> <时柱>"
```

**示例**：
```bash
python {{current_skill_dir_path}}/scripts/main.py \
  --action reverse \
  --bazi "庚午 壬午 辛亥 甲午"
```

**返回数据**：所有对应的公历时间列表

### Phase 3：命理解读

**目标**：基于原始数据进行专业命理解读

> 详见 [interpretation-guide.md](references/guides/interpretation-guide.md)

**解读维度**（按服务类型选择性输出）：

| 维度 | 内容 | 适用服务 |
|------|------|----------|
| 日主强弱 | 根据得令/得地/得助判断日主旺衰 | 排盘/综合 |
| 十神格局 | 主要十神分布及格局特征 | 排盘/综合 |
| 性格倾向 | 日主五行+十神组合推导性格 | 排盘/综合 |
| 事业方向 | 十神+五行推导适宜行业/方向 | 综合 |
| 财运分析 | 正财/偏财+财库+食伤生财 | 综合 |
| 感情婚姻 | 日支（配偶宫）+正偏财/官+神煞 | 综合 |
| 健康提示 | 五行偏枯+对应脏腑 | 综合 |
| 大运走势 | 各步大运吉凶及关键年份 | 综合 |
| 流年提醒 | 当前/近期流年注意事项 | 综合 |
| 刑冲合会 | 四柱间冲合关系及影响 | 排盘/综合 |
| 神煞解读 | 重要神煞含义及影响 | 排盘/综合 |

### Phase 4：结果呈现

**目标**：以结构化、易读的方式呈现分析结果

**呈现规范**：
1. 先展示基础信息（八字/生肖/日主等）
2. 再展示核心分析（十神/格局/旺衰）
3. 后展示延伸解读（性格/事业/财运/感情/健康）
4. 最后展示大运走势与建议

**格式要求**：
- 使用表格展示结构化数据（四柱/大运/神煞等）
- 使用分段标题组织内容
- 关键结论加粗标注
- 吉凶用符号标注（吉▲ 凶▼ 平─）

## 使用场景

### 场景1：八字排盘

**用户**："帮我排个八字，男，1990年6月15日中午12点"

**执行**：
1. 运行 `python scripts/main.py --action bazi --gender 1 --datetime "1990-06-15T12:00:00+08:00"`
2. 展示四柱八字、十神、神煞、刑冲合会
3. 给出日主强弱与格局简要判断

### 场景2：综合命理分析

**用户**："帮我看看命理，女，1990年6月10日下午3点"

**执行**：
1. 运行 `python scripts/main.py --action bazi --gender 0 --datetime "1990-06-10T15:00:00+08:00"`
2. 完整排盘 + 全维度解读（性格/事业/财运/感情/健康/大运）
3. 给出综合建议

### 场景3：黄历查询

**用户**："今天适合搬家吗？" / "看看下周一的黄历"

**执行**：
1. 运行 `python scripts/main.py --action huangli --datetime "<对应日期>"`
2. 展示宜忌、财神方位
3. 给出择日建议

### 场景4：八字反查

**用户**："八字庚午壬午辛亥甲午对应什么时间？"

**执行**：
1. 运行 `python scripts/main.py --action reverse --bazi "庚午 壬午 辛亥 甲午"`
2. 展示所有对应的公历时间

### 场景5：运势速查

**用户**："我今年运势怎么样？"

**执行**：
1. 先获取用户出生信息（如已有则复用）
2. 运行 `python scripts/main.py --action bazi` 获取大运信息
3. 结合当前年份分析流年与大运交汇
4. 运行 `python scripts/main.py --action huangli` 获取当日黄历作为辅助参考

## 解读参考

命理解读时参考以下指南，确保专业性与一致性：

- [bazi-basics.md](references/guides/bazi-basics.md) — 八字基础知识：天干地支、五行生克、十神体系
- [interpretation-guide.md](references/guides/interpretation-guide.md) — 解读指南：各维度解读方法与话术规范
- [full-analysis-flow.md](references/flows/full-analysis-flow.md) — 完整分析流程：综合命理分析的标准步骤

## 注意事项

| 事项 | 说明 |
|------|------|
| 早晚子时 | `--early-zi 1`表示23-24点日干支取次日，`--early-zi 2`表示取当日，默认2 |
| 时辰精度 | 出生时间最好精确到时辰（2小时），否则时柱可能有误 |
| 命理局限 | 八字为传统文化，解读仅供参考，不做绝对论断 |
| 隐私保护 | 不存储用户出生信息，每次分析需重新输入 |

## 工具脚本

```bash
# 安装依赖
pip install -r {{current_skill_dir_path}}/scripts/requirements.txt

# 八字排盘
python {{current_skill_dir_path}}/scripts/main.py --action bazi --gender 1 --datetime "1990-06-15T12:00:00+08:00"

# 黄历查询（默认今天）
python {{current_skill_dir_path}}/scripts/main.py --action huangli

# 八字反查
python {{current_skill_dir_path}}/scripts/main.py --action reverse --bazi "庚午 壬午 辛亥 甲午"

# 输出到文件
python {{current_skill_dir_path}}/scripts/main.py --action bazi --gender 1 --datetime "1990-06-15T12:00:00+08:00" --output result.json
```