// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const dailyReportForm = document.getElementById('daily-report-form');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    const htmlPreview = document.getElementById('html-preview');
    const imagePreview = document.getElementById('image-preview');
    const downloadHtmlBtn = document.getElementById('download-html');
    const downloadImageBtn = document.getElementById('download-image');
    const alertContainer = document.getElementById('alert-container');
    const fileInput = document.getElementById('chat-file');
    const fileNameDisplay = document.getElementById('file-name');
    const templateSelect = document.getElementById('template-select');

    // 加载模板列表
    loadTemplates();

    // 文件选择处理
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = '未选择文件';
            }
        });
    }

    // 表单提交处理
    if (dailyReportForm) {
        dailyReportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generateDailyReport();
        });
    }

    // 加载模板列表
    function loadTemplates() {
        if (!templateSelect) return;

        fetch('/api/templates')
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取模板列表失败');
                }
                return response.json();
            })
            .then(templates => {
                // 清空现有选项
                templateSelect.innerHTML = '';

                // 添加模板选项
                templates.forEach(template => {
                    const option = document.createElement('option');
                    option.value = template;
                    option.textContent = template;
                    templateSelect.appendChild(option);
                });
            })
            .catch(error => {
                showAlert('danger', '加载模板列表失败: ' + error.message);
            });
    }

    // 生成日报
    function generateDailyReport() {
        // 显示加载动画
        loadingContainer.style.display = 'flex';
        resultContainer.style.display = 'none';

        // 获取表单数据
        const formData = new FormData(dailyReportForm);
        const chatFile = fileInput.files[0];

        // 检查是否选择了文件
        if (!chatFile) {
            loadingContainer.style.display = 'none';
            showAlert('danger', '请选择聊天记录文件');
            return;
        }

        // 读取文件内容
        const reader = new FileReader();
        reader.onload = function(e) {
            const chatContent = e.target.result;
            const templateName = formData.get('template');
            const convertToImage = formData.get('convert_to_image') === 'on';
            const model = formData.get('model') || null;

            // 获取文件名
            const chatFileName = chatFile.name;
            console.log("聊天文件名:", chatFileName);

            // 准备请求数据
            const requestData = {
                chat_content: chatContent,
                chat_file_name: chatFileName,  // 添加文件名
                template_name: templateName,
                convert_to_image: convertToImage,
                model: model
            };

            // 发送请求
            fetch('/api/daily-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('生成日报失败');
                }
                return response.json();
            })
            .then(data => {
                // 隐藏加载动画
                loadingContainer.style.display = 'none';

                if (data.success) {
                    // 显示结果
                    resultContainer.style.display = 'block';

                    // 显示HTML预览
                    htmlPreview.srcdoc = data.html_content;

                    // 显示图片预览（如果有）
                    if (data.png_file_path) {
                        // 提取文件名（处理Windows和Unix路径）
                        let filename = data.png_file_path.split('/').pop();
                        if (filename.includes('\\')) {
                            filename = filename.split('\\').pop();
                        }
                        console.log("PNG文件路径:", data.png_file_path);
                        console.log("提取的文件名:", filename);

                        // 构建图片URL
                        const imgUrl = '/api/image/' + filename;
                        console.log("图片URL:", imgUrl);

                        // 设置图片预览
                        imagePreview.src = imgUrl;
                        imagePreview.style.display = 'block';

                        // 设置下载链接
                        downloadImageBtn.href = imgUrl;
                        downloadImageBtn.setAttribute('download', filename);
                        downloadImageBtn.style.display = 'inline-block';
                    } else {
                        imagePreview.style.display = 'none';
                        downloadImageBtn.style.display = 'none';
                    }

                    // 设置HTML下载链接
                    const blob = new Blob([data.html_content], { type: 'text/html' });
                    const htmlUrl = URL.createObjectURL(blob);
                    downloadHtmlBtn.href = htmlUrl;
                    downloadHtmlBtn.download = 'daily_report.html';

                    // 显示成功消息
                    showAlert('success', '日报生成成功！');
                } else {
                    // 显示错误消息
                    showAlert('danger', '日报生成失败: ' + data.message);
                }
            })
            .catch(error => {
                // 隐藏加载动画
                loadingContainer.style.display = 'none';

                // 显示错误消息
                showAlert('danger', '生成日报时出错: ' + error.message);
            });
        };

        reader.onerror = function() {
            loadingContainer.style.display = 'none';
            showAlert('danger', '读取文件失败');
        };

        reader.readAsText(chatFile);
    }

    // 显示提示消息
    function showAlert(type, message) {
        // 创建提示元素
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        // 清空现有提示
        alertContainer.innerHTML = '';

        // 添加新提示
        alertContainer.appendChild(alert);

        // 5秒后自动隐藏
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alertContainer.removeChild(alert);
            }, 500);
        }, 5000);
    }
});
