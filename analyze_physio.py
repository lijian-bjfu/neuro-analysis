# --- 务必放在第一个单元格并首先运行 ---
import matplotlib
matplotlib.use('Agg')  # 设置为非交互式后端

import neurokit2 as nk
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统可用的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def load_shimmer_data(file_path, fixed_sampling_rate=51.20):
    """加载Shimmer设备的数据文件"""
    print("\n正在读取数据文件...")
    data = pd.read_csv(file_path)
    
    # 打印所有列名
    print("\n数据文件包含以下列：")
    for i, col in enumerate(data.columns):
        print(f"{i+1}. {col}")
    
    # 使用实际的列名
    timestamp_col = 'TimestampSync'
    gsr_col = 'Skin_Conductance'
    accel_cols = ['Accel_LN_X', 'Accel_LN_Y', 'Accel_LN_Z']
    
    # 检查列是否存在
    if timestamp_col not in data.columns:
        raise ValueError(f"找不到时间戳列 '{timestamp_col}'")
    if gsr_col not in data.columns:
        raise ValueError(f"找不到GSR数据列 '{gsr_col}'")
    for col in accel_cols:
        if col not in data.columns:
            raise ValueError(f"找不到加速度数据列 '{col}'")
    
    # 获取时间戳数据
    timestamps = data[timestamp_col]
    
    # 计算数据信息
    start_time = datetime.fromtimestamp(timestamps.iloc[0]/1000)  # 转换为秒
    end_time = datetime.fromtimestamp(timestamps.iloc[-1]/1000)
    duration = end_time - start_time
    
    # 打印数据基本信息
    print("\n=== 数据信息 ===")
    print(f"使用的时间戳列: {timestamp_col}")
    print(f"使用的GSR数据列: {gsr_col}")
    print(f"测量开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测量结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测量时长: {duration}")
    print(f"数据点数: {len(data)}")
    print(f"采样率: {fixed_sampling_rate} Hz")
    
    # 打印数据统计信息
    print("\n信号统计信息:")
    stats = data[gsr_col].describe()
    print(f"\n皮电导 (GSR):")
    print(f"   平均值: {stats['mean']:.3f}")
    print(f"   标准差: {stats['std']:.3f}")
    print(f"   最小值: {stats['min']:.3f}")
    print(f"   最大值: {stats['max']:.3f}")
    
    # 计算合成加速度
    accel_data = np.sqrt(
        data[accel_cols[0]]**2 + 
        data[accel_cols[1]]**2 + 
        data[accel_cols[2]]**2
    )
    
    # 使用移动平均平滑加速度数据
    window_size = int(fixed_sampling_rate)  # 1秒窗口
    accel_smoothed = pd.Series(accel_data).rolling(window=window_size, center=True).mean()
    
    # 标准化加速度数据
    accel_normalized = (accel_smoothed - accel_smoothed.mean()) / accel_smoothed.std()
    
    # 返回皮电数据和加速度数据
    gsr_data = data[gsr_col]
    return gsr_data, accel_normalized, fixed_sampling_rate, duration.total_seconds()

def plot_eda_components_separate(time_axis, standardized_eda, components, save_path='eda_components_separate.png'):
    """
    将EDA信号的各个成分绘制为三个子图
    
    参数:
    time_axis: 时间轴数据
    standardized_eda: 标准化后的原始EDA信号
    components: 包含Phasic和Tonic成分的DataFrame
    save_path: 保存图片的路径
    """
    plt.figure(figsize=(20, 12))
    
    # 原始信号
    plt.subplot(3, 1, 1)
    plt.plot(time_axis, standardized_eda, label='标准化EDA信号')
    plt.title('标准化的原始EDA信号')
    plt.xlabel('时间 (分钟)')
    plt.ylabel('振幅 (标准化)')
    plt.grid(True)
    plt.legend()
    
    # Phasic成分
    plt.subplot(3, 1, 2)
    plt.plot(time_axis, components['EDA_Phasic'], label='相位成分')
    plt.title('相位成分 (SCR)')
    plt.xlabel('时间 (分钟)')
    plt.ylabel('振幅')
    plt.grid(True)
    plt.legend()
    
    # Tonic成分
    plt.subplot(3, 1, 3)
    plt.plot(time_axis, components['EDA_Tonic'], label='张力成分')
    plt.title('张力成分 (SCL)')
    plt.xlabel('时间 (分钟)')
    plt.ylabel('振幅')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_eda_components_combined(time_axis, standardized_eda, components, accel_data, save_path='eda_components_combined.png'):
    """
    将EDA信号的所有成分和加速度数据绘制在同一张图上
    
    参数:
    time_axis: 时间轴数据
    standardized_eda: 标准化后的原始EDA信号
    components: 包含Phasic和Tonic成分的DataFrame
    accel_data: 标准化后的合成加速度数据
    save_path: 保存图片的路径
    """
    plt.figure(figsize=(15, 8))
    
    # 绘制加速度数据（放在最下层）
    plt.plot(time_axis, accel_data, label='运动强度', color='gray', alpha=0.3, linewidth=1)
    
    # 绘制所有EDA成分
    plt.plot(time_axis, standardized_eda, label='原始信号', color='blue', alpha=0.6)
    plt.plot(time_axis, components['EDA_Phasic'], label='相位成分', color='red', alpha=0.6)
    plt.plot(time_axis, components['EDA_Tonic'], label='张力成分', color='green', alpha=0.6)
    
    plt.title('皮电信号分解与运动强度', fontsize=14)
    plt.xlabel('时间 (分钟)', fontsize=12)
    plt.ylabel('振幅 (标准化)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片（使用更高DPI以获得更好的质量）
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # 检查数据目录中的文件
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("请在'data'目录中放入您的数据文件")
        return
        
    # 列出数据目录中的CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("在'data'目录中没有找到CSV文件")
        return
        
    # 如果有多个文件，让用户选择
    if len(csv_files) > 1:
        print("\n可用的数据文件：")
        for i, file in enumerate(csv_files):
            print(f"{i+1}. {file}")
        file_idx = int(input("\n请选择要分析的文件编号: ")) - 1
        file_path = os.path.join(data_dir, csv_files[file_idx])
    else:
        file_path = os.path.join(data_dir, csv_files[0])
    
    print(f"\n正在分析文件: {os.path.basename(file_path)}")
    
    # 加载数据
    gsr_data, accel_data, sampling_rate, duration = load_shimmer_data(file_path)
    
    # 处理EDA/GSR信号
    print("\n处理皮电信号...")
    eda_signals, info = nk.eda_process(gsr_data, sampling_rate=sampling_rate)
    
    # 绘制前60秒的EDA信号
    print("生成皮电信号图...")
    plt.figure(figsize=(15, 6))
    signals_60s = eda_signals[:int(60*sampling_rate)].copy()
    nk.eda_plot(signals_60s, info)
    plt.savefig('eda_plot_60s.png')
    plt.close()
    
    # 分解为Phasic和Tonic成分并绘制整个时间段的数据
    print("\n分解皮电信号为Phasic和Tonic成分...")
    # 首先标准化原始信号
    standardized_eda = nk.standardize(gsr_data)
    # 分解为Phasic和Tonic成分
    components = nk.eda_phasic(standardized_eda, sampling_rate=sampling_rate)
    
    # 创建时间轴（以分钟为单位）
    time_axis = np.arange(len(gsr_data)) / (sampling_rate * 60)  # 转换为分钟
    
    # 绘制两种不同的图
    plot_eda_components_separate(time_axis, standardized_eda, components)
    plot_eda_components_combined(time_axis, standardized_eda, components, accel_data)
    
    # 提取EDA特征
    print("提取皮电特征...")
    eda_features = nk.eda_intervalrelated(eda_signals)
    print("\nEDA特征:")
    print(eda_features)
    
    # 将数据分成多个时间段进行分析
    print("\n进行分段分析...")
    # 将数据分成5分钟的段
    segment_duration = 300  # 5分钟 = 300秒
    total_samples = len(gsr_data)
    segment_samples = int(segment_duration * sampling_rate)
    n_segments = total_samples // segment_samples
    
    if n_segments > 1:
        events = [i * segment_samples for i in range(n_segments)]
        epochs = nk.epochs_create(eda_signals, 
                                events=events,
                                sampling_rate=sampling_rate, 
                                epochs_start=0,
                                epochs_end=segment_duration)
        
        segmented_features = nk.eda_intervalrelated(epochs)
        print("\n分段特征:")
        print(segmented_features)
        
        # 保存分段特征
        segmented_features.to_csv('eda_segmented_features.csv')
    
    # 保存特征到CSV文件
    print("\n保存结果...")
    eda_features.to_csv('eda_features.csv')
    
    # 保存处理后的信号数据
    eda_signals.to_csv('eda_processed_signals.csv')
    # 保存分解后的成分数据
    components.to_csv('eda_components.csv')
    
    print("\n分析完成！结果已保存到文件。")
    print("生成的文件：")
    print("- eda_plot_60s.png: 前60秒皮电信号可视化")
    print("- eda_components_combined.png: 完整时间段的Phasic和Tonic成分分解图（包含运动强度）")
    print("- eda_features.csv: 皮电特征")
    print("- eda_processed_signals.csv: 处理后的皮电信号")
    print("- eda_components.csv: Phasic和Tonic成分数据")
    if n_segments > 1:
        print("- eda_segmented_features.csv: 分段分析特征")

if __name__ == "__main__":
    main() 