# OFD → PDF 转换工具

基于 [ofd-utility](https://github.com/ofd-utility/ofd-utility) 的 `ofd-cli`，用 Python 封装：**OFD 渲染为页面图片 → 合成为 PDF**。

支持 **Windows / Linux / macOS**，可通过 **PyPI 平台 wheel** 安装，或下载 **独立可执行文件**。

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

Release 产物中的 `ofd2pdf-<os>-<arch>`（PyInstaller onefile）可直接运行：

```bash
./ofd2pdf-linux-x86_64 input.ofd -o out.pdf
ofd2pdf-windows-amd64.exe input.ofd -o out.pdf
```

本地打包：

```bash
# 先编译 ofd-cli
bash scripts/build_ofd_cli.sh   # Linux / macOS
# 或
powershell -NoProfile -File scripts/build_ofd_cli.ps1

uv sync --group dev
uv run python scripts/build_standalone.py
# 产物: dist/standalone/
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

## 构建平台 wheel / 发布

请分别构建（不要用默认的 `python -m build` 一次打齐：它会先打 sdist 再从 sdist 打 wheel，此时没有捆绑二进制）。

```bash
# 1) 当前平台 wheel（强制捆绑 ofd-cli）
bash scripts/build_wheel.sh
# 或
powershell -NoProfile -File scripts/build_wheel.ps1

# 2) 源码包（不含 ofd-cli）
uv run python -m build --sdist

# 上传（需配置 PyPI token / Trusted Publishing）
uv run twine upload dist/*
```

打 tag 或发布 GitHub Release 时，Actions 会在 **Windows / Linux / macOS** runner 上分别编译 `ofd-cli` 并打出对应 `.whl`，再挂到 Release Assets（并可推 PyPI）：

```bash
git tag v0.2.0
git push origin v0.2.0
# 或在 GitHub → Releases → Draft a new release 并 Publish
```

产物示例：

- `ofd2pdf-*-py3-none-win_amd64.whl`
- `ofd2pdf-*-py3-none-manylinux*.whl`（或 `linux_x86_64`，经 auditwheel 修复）
- macOS arm64 / x86_64 wheel
- 各平台独立可执行文件（PyInstaller）

PyPI：在仓库 Settings 中配置 Trusted Publishing（OIDC），或手动 `workflow_dispatch` 勾选 publish。

## 目录结构

```
ofd2pdf/
├── src/ofd2pdf/           # Python 包
│   └── bin/               # 构建时放入的 ofd-cli（随平台 wheel 发布）
├── scripts/               # ofd-cli / wheel / standalone 构建脚本
├── hatch_build.py         # 平台 wheel 标记
└── .github/workflows/     # CI 与 Release
```

## 许可证

本项目为 MIT（见 [LICENSE](LICENSE)）。

捆绑 / 依赖的 [ofd-utility](https://github.com/ofd-utility/ofd-utility)（`ofd-cli`）同为 MIT；上游版权与许可全文见 [NOTICE](NOTICE)。
