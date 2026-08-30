# 24点算法求解器（Python + Kivy）

单功能安卓 App：输入 4 个数字，自动求解 24 点算式。

## 功能

| 功能 | 说明 |
|---|---|
| **数字24算法** | 输入 4 个数字（空格分隔），点击「计算」自动求解并显示算式。支持扑克牌符号：`A`=1、`J`=11、`Q`=12、`K`=13。 |

### 交互细节
- **输入框**：单行文本，空格分隔 4 个值，如 `10 11 13 2` 或 `A J Q K`
- **计算**：深度优先搜索所有运算组合（`+ - × ÷`），全程使用 `Fraction` 精确分数运算，避免浮点误差
- **结果**：
  - 能算出 24 → 卡片下方**绿字显示算式**（如 `(A+J)×(Q-K) = 24`）
  - 不能算出 → **红字提示"这 4 个数根本不可能算出 24"**
- **重置**：清空输入框、卡片、结果
- **退出**：关闭应用

## 项目结构

```
game24/
├── main.py                  # 全部程序代码（单文件）
├── buildozer.spec           # 安卓打包配置
├── assets/fonts/
│   └── NotoSansSC-Regular.otf   # 内置中文字体（Kivy 默认字体不含中文）
└── README.md
```

## 一、在电脑上试玩

```bash
pip install kivy
cd game24
python main.py
```

> Windows / macOS / Linux 均可运行，界面与手机一致。

## 二、打包成安卓 APK

Buildozer 只能在 **Linux 或 WSL** 下打包（Windows 用户建议用 WSL2 的 Ubuntu）：

```bash
# 1. 安装 buildozer 及系统依赖（Ubuntu/WSL）
pip install buildozer cython
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 2. 在项目目录（main.py 与 buildozer.spec 所在目录）执行
cd game24
buildozer android debug        # 首次运行会自动下载 Android SDK/NDK，约 20~40 分钟

# 3. 产物在 bin/ 目录：game24-1.0.0-arm64-v8a-debug.apk
#    传到手机安装即可；连接手机时可用：
buildozer android debug deploy run logcat
```

常用命令：

```bash
buildozer android clean    # 出问题时清理重新构建
buildozer --version
```

## 三、注意事项

- **字体**：`assets/fonts/NotoSansSC-Regular.otf` 已内置，界面中文正常显示。若换字体，保持文件名不变即可（代码按此路径加载）。
- **修改包名**：编辑 `buildozer.spec` 中的 `package.domain` / `package.name`。
- **应用名称**：`buildozer.spec` 中 `title = 24点算法`。
- 中间计算结果若为分数（如 `8÷3`），卡片上显示为 `8/3`，内部按精确分数计算，最终结果仍可准确凑出 24。
- 输入扑克牌符号不区分大小写：`A J Q K`、`a j q k`、`A j Q k` 均可。