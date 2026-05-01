# 韩院长预约排班系统（EXE 桌面版）

这是一个可直接打包为 Windows `.exe` 的预约排班系统示例，基于 Python + Tkinter。

## 功能

- 快速录入客户预约信息
- 展示技师排班示例
- 维护“今日预约列表”

## 本地运行

```bash
python app.py
```

## 生成 EXE（Windows）

1. 安装 Python 3.10+
2. 双击运行 `build_exe.bat`
3. 生成文件路径：`dist/SpaBookingApp.exe`

## 目录结构

- `app.py`：主程序
- `requirements.txt`：打包依赖
- `build_exe.bat`：一键打包脚本
