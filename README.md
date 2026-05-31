# 玄音八字 (Xuanyin-Bazi): 八字命理分析引擎

玄之又玄，音韵悠长。自包含八字命理分析 Skill，无需外部MCP服务，所有计算由内置Python脚本完成。

## 功能

- **八字排盘**：公历输入 → 四柱八字 + 十神 + 神煞 + 刑冲合会
- **大运推算**：起运年龄 + 十步大运
- **综合命理**：性格/事业/财运/感情/健康多维度解读
- **黄历查询**：任意日期 → 农历/干支/宜忌/财神方位
- **八字反查**：已知八字 → 反推公历时间

## 依赖

- **Python 3.8+**
- **pip依赖**：`pip install -r scripts/requirements.txt`（lunisolar-calendar，用于农历转换，可选）

## 目录结构

```
xuanyin-bazi/
├── SKILL.md                              # Skill主定义文件
├── README.md                             # 本文件
├── scripts/
│   ├── main.py                           # 八字计算引擎（自包含）
│   └── requirements.txt                  # Python依赖
└── references/
    ├── guides/
    │   ├── bazi-basics.md                # 八字基础知识（天干地支/五行/十神/神煞）
    │   └── interpretation-guide.md       # 命理解读指南（各维度解读方法与话术规范）
    └── flows/
        └── full-analysis-flow.md         # 完整分析流程（综合命理分析标准步骤）
```

## 使用示例

```bash
# 八字排盘
python scripts/main.py --action bazi --gender 1 --datetime "1990-06-15T12:00:00+08:00"

# 黄历查询
python scripts/main.py --action huangli

# 八字反查
python scripts/main.py --action reverse --bazi "庚午 壬午 辛亥 甲午"

#或者安装技能后直接对话：
用户：帮我排个八字，男，1990年6月15日中午12点
用户：看看我今年的运势
用户：今天适合搬家吗？
用户：八字庚午壬午辛亥甲午对应什么时间？
```

## 安装

将 `xuanyin-bazi` 目录复制到 `~/.xxx/skills/` 下即可自动加载。

安装Python依赖：
```bash
pip install -r scripts/requirements.txt
```
