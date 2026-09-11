# OFD → PDF 转换工具

基于 [ofd-utility](https://github.com/ofd-utility/ofd-utility) 的 `ofd-cli`，用 Python 封装：**OFD 渲染为页面图片 → 合成为 PDF**。

官方构建支持 **Windows / Linux**，可通过 **PyPI 平台 wheel** 安装，或下载 **独立可执行文件**。

## 原理

1. 调用 `ofd-cli render` 将各页光栅化为 PNG（或其它格式）
2. 用 Pillow 按页序合并为多页 PDF

## 安装（PyPI）

```bash
pip install ofd2pdf
# 或
uv add ofd2pdf
```

安装的是**当前平台**的 wheel，内置对应系统的 `ofd-cli` 二进制，无需本机安装 Rust。

> 纯源码 sdist **不**包含 `ofd-cli`。若仅装到 sdist，请自行构建二进制或设置 `OFD_CLI`。

## 独立二进制（无 Python 环境）

GitHub Release 产物中的 `ofd2pdf-<os>-<arch>`（PyInstaller onefile）可直接运行：

```bash
./ofd2pdf-linux-x86_64 input.ofd -o out.pdf
ofd2pdf-windows-amd64.exe input.ofd -o out.pdf
```

## 本地开发

```bash
uv sync --group dev
bash scripts/build_ofd_cli.sh    # 或 build_ofd_cli.ps1
uv run ofd2pdf sample.ofd -o out.pdf --dpi 200
```

也可手动指定：

```bash
export OFD_CLI=/path/to/ofd-cli      # Unix
set OFD_CLI=C:\path\to\ofd-cli.exe # Windows
```

## 用法

```bash
ofd2pdf sample.ofd
ofd2pdf sample.ofd -o out.pdf --dpi 200
ofd2pdf sample.ofd --keep-images --images-dir ./pages
ofd2pdf sample.ofd --info
```

库调用：

```python
from ofd2pdf import convert_ofd_to_pdf

pdf = convert_ofd_to_pdf("sample.ofd", "out.pdf", dpi=150)
```

## 发布（仅 GitHub Actions）

打包与上传 **只在 CI 完成**：打 `v*` tag 后，Actions 会构建多平台 wheel / sdist / 独立二进制，挂到 GitHub Release，并自动上传 PyPI。

```bash
git tag v0.2.1
git push origin v0.2.1
# 进度: https://github.com/rhq-git/ofd2pdf/actions
```

也可在 Actions → **Release** → **Run workflow**，填已有 tag 补打并重新上传（PyPI 已有文件会 `skip-existing`）。

前置：在 [PyPI](https://pypi.org) 为该项目配置 **Trusted Publishing（OIDC）**，Workflow 填 `release.yml`。

产物示例（Windows / Linux）：

- `ofd2pdf-*-py3-none-win_amd64.whl`
- `ofd2pdf-*-py3-none-linux_x86_64.whl`（或 manylinux）
- `ofd2pdf-windows-amd64.exe` / `ofd2pdf-linux-x86_64`

## 目录结构

```
ofd2pdf/
├── src/ofd2pdf/           # Python 包
│   └── bin/               # 构建时放入的 ofd-cli（随平台 wheel 发布）
├── scripts/               # ofd-cli / standalone 构建脚本（供 CI / 本地开发）
├── hatch_build.py         # 平台 wheel 标记
└── .github/workflows/     # CI 与 Release
```

## 许可证

本项目为 MIT（见 [LICENSE](LICENSE)）。

捆绑 / 依赖的 [ofd-utility](https://github.com/ofd-utility/ofd-utility)（`ofd-cli`）同为 MIT；上游版权与许可全文见 [NOTICE](NOTICE)。
