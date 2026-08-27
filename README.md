```
### 📖 使用说明
**前置条件**：系统需安装 FFmpeg 并加入 PATH：
```bash
# Ubuntu / Debian
sudo apt install ffmpeg
# macOS
brew install ffmpeg
# Windows
winget install ffmpeg
```
**常用命令示例**：
```bash
# 将 ./audio 下所有 wav 转成 mp3，输出到 ./audio/converted_mp3
python audio_convert.py ./audio wav mp3
# 指定输出目录和码率 192kbps
python audio_convert.py ./recordings flac mp3 -o ./out -b 192k
# 递归处理子文件夹 + 重采样为16kHz单声道常用参数 + 覆盖旧文件
python audio_convert.py ./audio wav mp3 -r -sr 16000 -y
```
### ✨ 脚本特点
| 特性 | 说明 |
| :--- | :--- |
| **FFmpeg自检** | 启动前检查FFmpeg是否可用，并给出各平台安装提示 |
| **递归遍历** | `-r` 参数可处理子文件夹，且保持相对目录结构 |
| **断点续转** | 默认跳过已存在的输出文件，配合 `-y` 可强制覆盖 |
| **可选参数** | 支持指定码率、采样率等编码选项 |
| **失败汇总** | 单个文件失败不影响整体任务，最后统一报告 |

**FFmpeg 安装某个文件夹里，需要添加到系统的 `PATH` 环境变量中**。
脚本检查安装的方式是执行 `ffmpeg -version` 命令。当你直接运行 `ffmpeg` 时，Windows 只会在 **PATH 环境变量列出的目录**中寻找 `ffmpeg.exe`，不会自动扫描你的 D 盘。所以即使文件真实存在，系统也“找不到”它。

#### 方法：将 FFmpeg 加入 PATH（一劳永逸）
1.  按 `Win + R`，输入 `sysdm.cpl` 回车 → 切换到【高级】选项卡 → 点击【环境变量】。
2.  在“系统变量”（或“用户变量”）列表中找到 `Path`，双击编辑。
3.  点击【新建】，添加 FFmpeg 所在的 bin 目录：
    ```
    D:\ffmpeg-8.1-full_build\bin
    ```
4.  一路点击【确定】保存。
5.  **重要**：关闭并重新打开命令行窗口（PATH 修改只对新开的终端生效），然后验证：
    ```cmd
    ffmpeg -version
    ```
    如果能输出版本信息，说明配置成功，脚本就可以正常运行了。
> PowerShell 中也可用一条命令快速添加（用户级）：
> ```powershell
> [Environment]::SetEnvironmentVariable("Path", $env:Path + ";D:\ffmpeg-8.1-full_build\bin", "User")
> ```
> 添加后需要重开终端。
### 🔍 小提示
-   如果你是在 **PyCharm/VS Code** 里运行脚本，修改 PATH 后需要**重启 IDE**才能生效。
-   还要确认下载的是 **full build / essentials build** 而不是共享库版本——你已经下载的是 `ffmpeg-8.1-full_build`，没问题 ✅。
-   验证是否生效的判断标准始终是：新开一个 cmd 窗口，输入 `ffmpeg -version` 有输出即可。

