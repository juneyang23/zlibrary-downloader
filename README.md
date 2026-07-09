# Z-Library Downloader

从 Z-Library 按书名搜索和下载书籍，自动选择中文译本中热度最高的版本，下载并转换为 PDF。

## 功能特性

-   **智能搜索**：根据书名在 Z-Library 中搜索匹配图书
-   **中文优先**：自动筛选中文翻译版本，选取下载量最高的结果
-   **自动转 PDF**：非 PDF 文件（epub、mobi 等）自动通过 Calibre 转换为 PDF
-   **登录持久化**：首次登录后保存 Cookie，后续无需重复认证
-   **WorkBuddy Skill**：可直接作为 AI 技能调用

## 环境要求

- Python 3.8+
- [Calibre](https://calibre-ebook.com/download)（用于格式转换，需 `ebook-convert` 在 PATH 中）

依赖安装：

```bash
pip install requests beautifulsoup4
```

## 快速开始

### 1. 首次登录

运行登录脚本，输入 Z-Library 账号密码或 Token：

```bash
python scripts/zlibrary_login.py
```

登录成功后，Cookie 自动保存至 `~/.zlibrary_cookies.json`，后续下载无需再次登录。

### 2. 下载书籍

```bash
python scripts/zlibrary_download.py 三体
```

脚本会自动：
1. 搜索 "三体" 的中文版本
2. 选择下载量最高的结果
3. 下载到 `~/Downloads/books/` 目录
4. 若非 PDF 格式，自动转换为 PDF

### 输出示例

```
Searching: 三体
Best match: 三体 (12345 downloads)
Downloading...
Downloaded: ~/Downloads/books/三体.epub (2.3 MB)
Converted to PDF: ~/Downloads/books/三体.pdf

Done! Saved to: ~/Downloads/books/三体.pdf
```

## 项目结构

```
zlibrary-downloader/
├── SKILL.md                      # Skill 定义文件（WorkBuddy）
├── README.md                     # 项目说明
├── agents/
│   └── interface.yaml            # Agent 接口配置
├── scripts/
│   ├── zlibrary_login.py         # 登录脚本
│   └── zlibrary_download.py      # 下载脚本
└── .gitignore
```

## 注意事项

- 仅支持书名搜索，不支持 DOI/ISBN 精确查询
- 不处理期刊论文下载
- 若搜索无中文译本，程序会直接退出
- 下载失败最多重试 3 次
- 格式转换超时时间为 120 秒

## 许可

MIT License
