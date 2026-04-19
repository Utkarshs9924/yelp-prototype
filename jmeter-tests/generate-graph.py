#!/usr/bin/env python3
"""
Generate JMeter performance graph from test results
"""
import matplotlib.pyplot as plt
import pandas as pd
import sys

def create_performance_graph(results_file, output_file='performance-graph.png'):
    """Create performance graph from JMeter results"""
    
    # Example data - replace with actual results from JMeter
    concurrency = [100, 200, 300, 400, 500]
    avg_response_time = [45, 92, 185, 380, 650]
    throughput = [180, 320, 410, 450, 480]
    error_rate = [0.0, 0.1, 0.5, 2.0, 5.2]
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('JMeter Performance Test Results - Yelp Prototype', fontsize=16, fontweight='bold')
    
    # 1. Average Response Time
    ax1.plot(concurrency, avg_response_time, marker='o', linewidth=2, markersize=8, color='#2563eb')
    ax1.set_xlabel('Concurrent Users')
    ax1.set_ylabel('Avg Response Time (ms)')
    ax1.set_title('Average Response Time vs Concurrency')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(concurrency)
    
    # 2. Throughput
    ax2.plot(concurrency, throughput, marker='s', linewidth=2, markersize=8, color='#16a34a')
    ax2.set_xlabel('Concurrent Users')
    ax2.set_ylabel('Throughput (req/s)')
    ax2.set_title('Throughput vs Concurrency')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(concurrency)
    
    # 3. Error Rate
    ax3.plot(concurrency, error_rate, marker='^', linewidth=2, markersize=8, color='#dc2626')
    ax3.set_xlabel('Concurrent Users')
    ax3.set_ylabel('Error Rate (%)')
    ax3.set_title('Error Rate vs Concurrency')
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(concurrency)
    
    # 4. Summary Table
    ax4.axis('tight')
    ax4.axis('off')
    table_data = [
        ['Concurrency', 'Avg RT (ms)', 'Throughput', 'Error %'],
        ['100', '45', '180', '0.0'],
        ['200', '92', '320', '0.1'],
        ['300', '185', '410', '0.5'],
        ['400', '380', '450', '2.0'],
        ['500', '650', '480', '5.2'],
    ]
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.25, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#e0e7ff')
        table[(0, i)].set_text_props(weight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Performance graph saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_performance_graph(sys.argv[1])
    else:
        create_performance_graph(None)
