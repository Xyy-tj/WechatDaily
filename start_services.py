#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动微服务架构的所有服务
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import logging
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('service_starter')

# 服务配置
SERVICES = [
    {
        "name": "HTML转图片服务",
        "script": "html_to_image_service_fastapi.py",
        "host": "0.0.0.0",
        "port": 8001,
        "process": None
    },
    {
        "name": "主应用服务",
        "script": "app_soa.py",
        "host": "0.0.0.0",
        "port": 8000,
        "process": None
    }
]

# 进程列表
processes = []

def log_stream(stream, prefix):
    """
    从流中读取并记录输出

    Args:
        stream: 要读取的流
        prefix: 日志前缀
    """
    for line in iter(stream.readline, ''):
        if line:
            print(f"{prefix}: {line.rstrip()}")

    if not stream.closed:
        stream.close()

def start_service(service, debug=False):
    """
    启动单个服务

    Args:
        service: 服务配置字典
        debug: 是否启用调试模式

    Returns:
        启动的进程对象
    """
    cmd = [
        sys.executable,
        service["script"],
        "--host", service["host"],
        "--port", str(service["port"])
    ]

    if debug:
        cmd.append("--debug")

    logger.info(f"启动服务: {service['name']} - {' '.join(cmd)}")

    # 启动进程
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # 创建线程来处理输出
    prefix = f"[{service['name']}]"
    stdout_thread = threading.Thread(target=log_stream, args=(process.stdout, prefix))
    stderr_thread = threading.Thread(target=log_stream, args=(process.stderr, prefix))

    # 设置为守护线程，这样主程序退出时它们也会退出
    stdout_thread.daemon = True
    stderr_thread.daemon = True

    # 启动线程
    stdout_thread.start()
    stderr_thread.start()

    # 等待一段时间确保服务启动
    time.sleep(2)

    if process.poll() is not None:
        # 进程已经结束
        logger.error(f"服务 {service['name']} 启动失败")
        return None

    logger.info(f"服务 {service['name']} 已启动，PID: {process.pid}")
    return process

def stop_services():
    """停止所有服务"""
    for process in processes:
        if process and process.poll() is None:
            logger.info(f"停止进程 PID: {process.pid}")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"进程 PID: {process.pid} 未能正常终止，强制结束")
                process.kill()

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，停止所有服务")
    stop_services()
    sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动微服务架构的所有服务')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动所有服务
    for service in SERVICES:
        process = start_service(service, args.debug)
        if process:
            processes.append(process)

    if not processes:
        logger.error("没有成功启动任何服务")
        return 1

    logger.info(f"所有服务已启动，共 {len(processes)} 个服务")

    try:
        # 保持主进程运行，并监控子进程
        while True:
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    # 进程已结束
                    logger.error(f"服务 {SERVICES[i]['name']} 意外终止")

                    # 尝试重启服务
                    logger.info(f"尝试重启服务 {SERVICES[i]['name']}")
                    new_process = start_service(SERVICES[i], args.debug)
                    if new_process:
                        processes[i] = new_process

            # 每秒检查一次
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("接收到键盘中断，停止所有服务")
        stop_services()

    return 0

if __name__ == "__main__":
    sys.exit(main())
