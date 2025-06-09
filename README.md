# 生理信号分析 (皮电数据)

这个项目提供了一个用于分析皮电(GSR/EDA)信号的Python脚本，使用NeuroKit2包进行数据处理和分析。

## 功能

- 处理和分析皮电(GSR/EDA)信号
- 自动检测数据采样率
- 生成信号可视化
- 提取皮电特征
- 执行分段分析（如果数据长度足够）
- 保存所有结果到CSV文件

## 数据要求

将您的Shimmer设备导出的CSV数据文件放在项目根目录下的`data`文件夹中。数据文件应包含以下列：
- TimestampSync - 时间戳
- GSR_Skin_Conductance - 皮肤电导
- GSR_Skin_Resistance - 皮肤电阻
- Accel_LN_X/Y/Z - 三轴加速度
- Gyro_X/Y/Z - 三轴陀螺仪
- Mag_X/Y_CAL/Z - 三轴磁力计
- Battery - 电池电量
- Range - 范围

## 安装

1. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows上使用: venv\Scripts\activate
```

2. 安装所需包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 将您的数据文件放入`data`目录
2. 运行脚本：
```bash
python analyze_physio.py
```
3. 如果有多个数据文件，根据提示选择要分析的文件

## 输出文件

脚本会生成以下文件：
- `eda_plot.png`: 皮电信号可视化
- `eda_features.csv`: 提取的皮电特征
- `eda_processed_signals.csv`: 处理后的皮电信号数据
- `eda_segmented_features.csv`: 分段分析特征（如果数据长度超过5分钟）

## 注意事项

- 采样率固定为51.20 Hz
- 分段分析默认使用5分钟为一段
- 信号可视化默认显示前60秒的数据