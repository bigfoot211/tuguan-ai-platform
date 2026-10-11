# 土管AI实训平台（Streamlit 公网版）

土地资源管理专业课余自主学习系统（人工智能赋能教学改革课程群数字化建设项目）。

与本地 Flask 版同源数据：**5 门核心课程 · 68 个知识点（全部配示意图）· 904 条智能问答（答案配图）**。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

浏览器自动打开 http://localhost:8501

## 公网部署（Streamlit Community Cloud）

1. 将本目录推送到 GitHub 独立仓库（与《地籍管理》djgl-training 仓库完全分离）；
2. 登录 https://share.streamlit.io （用 GitHub 账号）；
3. 点击 **New app** → 选择本仓库 → 分支 main → 入口文件 `streamlit_app.py` → Deploy；
4. 部署完成后获得独立网址 `https://<仓库名>-<随机串>.streamlit.app`。

## 目录结构

```
tuguan_ai_web/
├── streamlit_app.py      # 主应用（含检索/问答引擎）
├── requirements.txt      # 依赖
├── data/
│   ├── courses.json      # 课程知识库（68知识点，含配图字段）
│   └── faq.json          # 智能问答库（904条，含配图字段）
└── static/img/
    ├── djgl/             # 地籍教学示意图（7幅，复用《地籍管理》实训系统成果）
    ├── landuse/          # 土地分类实景图（35张）
    ├── knowledge/        # 知识点要点卡片图（68张）
    └── course/           # 课程封面图（5张）
```

## 数据维护

编辑 `data/courses.json` / `data/faq.json` 后推送到 GitHub，Streamlit 会自动重新部署。
新增知识点配图：把图片放入 `static/img/knowledge/`，并在 JSON 的 `image` 字段填写 `/static/img/knowledge/<文件名>.png`。
