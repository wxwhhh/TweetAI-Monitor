// 主要JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    
    // 全局变量
    let isMonitoring = false;
    let statusUpdateInterval;
    
    // 初始化
    init();
    
    function init() {
        // 更新监控状态
        updateMonitoringStatus();
        
        // 启动状态轮询
        startStatusPolling();
        
        // 绑定事件
        bindEvents();
        
        // 初始化工具提示
        initTooltips();
    }
    
    // 绑定事件
    function bindEvents() {
        // 推文卡片点击事件
        const tweetCards = document.querySelectorAll('.tweet-card');
        tweetCards.forEach(card => {
            card.addEventListener('click', function() {
                const tweetId = this.dataset.tweetId;
                if (tweetId) {
                    window.location.href = `/tweet/${tweetId}`;
                }
            });
        });
        
        // 筛选表单提交事件
        const filterForm = document.getElementById('filter-form');
        if (filterForm) {
            filterForm.addEventListener('submit', function(e) {
                showLoading('正在筛选...');
            });
        }
        
        // 密码显示/隐藏切换
        initPasswordToggle();
        
        // 表单验证
        initFormValidation();
    }
    
    // 更新监控状态
    function updateMonitoringStatus() {
        fetch('/api/monitoring_status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('monitoring-status');
                if (statusElement) {
                    if (data.running) {
                        statusElement.innerHTML = '<i class="bi bi-circle-fill text-success"></i> 监控中';
                        statusElement.className = 'badge bg-success';
                        isMonitoring = true;
                    } else {
                        statusElement.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> 已停止';
                        statusElement.className = 'badge bg-danger';
                        isMonitoring = false;
                    }
                }
                
                // 更新最后更新时间
                const lastUpdateElement = document.querySelector('.navbar-text small');
                if (lastUpdateElement && data.last_update) {
                    const updateTime = new Date(data.last_update).toLocaleString('zh-CN');
                    lastUpdateElement.textContent = `最后更新: ${updateTime}`;
                }
            })
            .catch(error => {
                console.error('获取监控状态失败:', error);
            });
    }
    
    // 启动状态轮询
    function startStatusPolling() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
        
        statusUpdateInterval = setInterval(updateMonitoringStatus, 10000); // 每10秒更新一次
    }
    
    // 停止状态轮询
    function stopStatusPolling() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
    }
    
    // 显示加载状态
    function showLoading(message = '加载中...') {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div class="d-flex justify-content-center align-items-center position-fixed top-0 start-0 w-100 h-100" 
                 style="background-color: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="text-center text-white">
                    <div class="loading mb-3"></div>
                    <p>${message}</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    }
    
    // 隐藏加载状态
    function hideLoading() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    // 显示消息
    function showMessage(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 3秒后自动隐藏
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
    
    // 初始化密码显示/隐藏功能
    function initPasswordToggle() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            // 检查是否已经有切换按钮
            const existingToggle = input.parentNode.querySelector('.password-toggle');
            if (existingToggle) return;
            
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'btn btn-outline-secondary password-toggle';
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
            toggleBtn.style.cssText = 'position: absolute; right: 5px; top: 50%; transform: translateY(-50%); z-index: 10; border: none; background: transparent;';
            
            // 设置父容器样式
            input.parentNode.style.position = 'relative';
            input.style.paddingRight = '45px';
            
            toggleBtn.addEventListener('click', function() {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.innerHTML = '<i class="bi bi-eye-slash"></i>';
                } else {
                    input.type = 'password';
                    this.innerHTML = '<i class="bi bi-eye"></i>';
                }
            });
            
            input.parentNode.appendChild(toggleBtn);
        });
    }
    
    // 初始化表单验证
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    showMessage('请填写所有必需字段', 'danger');
                }
                form.classList.add('was-validated');
            });
        });
    }
    
    // 初始化工具提示
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // 复制到剪贴板功能
    window.copyToClipboard = function(text, button) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check"></i> 已复制';
                button.classList.replace('btn-outline-secondary', 'btn-success');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.replace('btn-success', 'btn-outline-secondary');
                }, 2000);
                
                showMessage('内容已复制到剪贴板', 'success');
            }).catch(function() {
                showMessage('复制失败，请手动复制', 'danger');
            });
        } else {
            // 备用方案：使用execCommand
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                showMessage('内容已复制到剪贴板', 'success');
            } catch (err) {
                showMessage('复制失败，请手动复制', 'danger');
            }
            document.body.removeChild(textArea);
        }
    };
    
    // 格式化时间
    window.formatTime = function(timeString) {
        const date = new Date(timeString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };
    
    // 截断文本
    window.truncateText = function(text, maxLength = 100) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    };
    
    // 防抖函数
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // 页面离开时清理
    window.addEventListener('beforeunload', function() {
        stopStatusPolling();
    });
    
    // 暴露全局函数
    window.TwitterAI = {
        updateMonitoringStatus: updateMonitoringStatus,
        showLoading: showLoading,
        hideLoading: hideLoading,
        showMessage: showMessage,
        startStatusPolling: startStatusPolling,
        stopStatusPolling: stopStatusPolling
    };
});

// API调用封装
class API {
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || '请求失败');
            }
            
            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
    
    static async saveConfig(config) {
        return this.request('/api/save_config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }
    
    static async startMonitoring() {
        return this.request('/api/start_monitoring', {
            method: 'POST'
        });
    }
    
    static async stopMonitoring() {
        return this.request('/api/stop_monitoring', {
            method: 'POST'
        });
    }
    
    static async getMonitoringStatus() {
        return this.request('/api/monitoring_status');
    }
    
    static async getTweets(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/api/tweets?${params}`);
    }
}

// 暴露API类
window.API = API; 

// 主题切换功能
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        // 设置初始主题
        this.setTheme(this.currentTheme);
        
        // 绑定主题切换按钮事件
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // 更新按钮图标
        this.updateThemeIcon();
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateThemeIcon();
        
        // 添加过渡动画类
        document.body.classList.add('theme-transition');
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 300);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            if (this.currentTheme === 'light') {
                themeIcon.className = 'bi bi-moon-fill';
                themeIcon.style.color = '#6f42c1';
            } else {
                themeIcon.className = 'bi bi-sun-fill';
                themeIcon.style.color = '#ffc107';
            }
        }
    }
}

// 页面加载完成后初始化主题管理器
document.addEventListener('DOMContentLoaded', function() {
    // 初始化主题管理器
    window.themeManager = new ThemeManager();
    
    // 初始化其他功能
    initApp();
});

// 应用初始化
function initApp() {
    // 初始化日期筛选功能
    initDateFilter();
    
    // 初始化推文卡片功能
    initTweetCards();
    
    // 初始化监控状态更新
    initMonitoringStatus();
}

// 日期筛选功能
function initDateFilter() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        // 设置开始日期的最大值为今天
        const today = new Date().toISOString().split('T')[0];
        startDateInput.max = today;
        endDateInput.max = today;
        
        // 当开始日期改变时，设置结束日期的最小值
        startDateInput.addEventListener('change', function() {
            if (endDateInput && this.value) {
                endDateInput.min = this.value;
            }
        });
        
        // 当结束日期改变时，设置开始日期的最大值
        endDateInput.addEventListener('change', function() {
            if (startDateInput && this.value) {
                startDateInput.max = this.value;
            }
        });
    }
}

// 推文卡片功能
function initTweetCards() {
    // 推文卡片点击事件
    document.addEventListener('click', function(e) {
        const tweetCard = e.target.closest('.tweet-card');
        if (tweetCard) {
            const tweetId = tweetCard.getAttribute('data-tweet-id');
            if (tweetId) {
                window.location.href = `/tweet/${tweetId}`;
            }
        }
    });
}

// 监控状态更新
function initMonitoringStatus() {
    let lastTweetCount = 0;
    let isRefreshing = false;

    // 定期更新监控状态
    function updateSystemStatus() {
        if (isRefreshing) return;
        
        fetch('/api/monitoring_status')
            .then(response => response.json())
            .then(data => {
                // 更新导航栏状态
                const statusElement = document.getElementById('monitoring-status');
                if (statusElement) {
                    if (data.running) {
                        statusElement.innerHTML = '<i class="bi bi-cpu"></i> AI ACTIVE';
                        statusElement.className = 'badge bg-success';
                    } else {
                        statusElement.innerHTML = '<i class="bi bi-power"></i> OFFLINE';
                        statusElement.className = 'badge bg-danger';
                    }
                }
                
                // 更新实时状态显示和倒计时
                const liveStatus = document.getElementById('live-status');
                if (liveStatus) {
                    if (data.running) {
                        const status = data.current_status || 'AI运行中';
                        
                        // 如果有下次检查时间，显示倒计时
                        if (data.next_check_time) {
                            const nextCheck = new Date(data.next_check_time);
                            const now = new Date();
                            const diff = nextCheck - now;
                            
                            if (diff > 0) {
                                const minutes = Math.floor(diff / 60000);
                                const seconds = Math.floor((diff % 60000) / 1000);
                                const countdown = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
                                liveStatus.innerHTML = '<i class="bi bi-clock"></i> 下次扫描: ' + countdown;
                                liveStatus.className = 'badge bg-info';
                            } else {
                                liveStatus.innerHTML = '<i class="bi bi-cpu"></i> ' + status;
                                liveStatus.className = 'badge bg-success';
                            }
                        } else {
                            liveStatus.innerHTML = '<i class="bi bi-cpu"></i> ' + status;
                            liveStatus.className = 'badge bg-success';
                        }
                    } else {
                        liveStatus.innerHTML = '<i class="bi bi-power"></i> 离线';
                        liveStatus.className = 'badge bg-secondary';
                    }
                }
            })
            .catch(error => console.error('更新状态失败:', error));
    }

    // 检查新推文
    function checkForNewTweets() {
        if (isRefreshing) return;
        
        fetch('/api/tweets')
            .then(response => response.json())
            .then(tweets => {
                if (tweets.length > lastTweetCount) {
                    // 有新推文，刷新页面
                    isRefreshing = true;
                    const liveStatus = document.getElementById('live-status');
                    if (liveStatus) {
                        liveStatus.innerHTML = '<i class="bi bi-arrow-clockwise"></i> 发现新推文，正在更新...';
                        liveStatus.className = 'badge bg-info';
                    }
                    
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                }
                lastTweetCount = tweets.length;
            })
            .catch(error => console.error('检查新推文失败:', error));
    }

    // 每2秒更新状态（更频繁的倒计时更新），每30秒检查新推文
    setInterval(updateSystemStatus, 2000);
    setInterval(checkForNewTweets, 30000);
    
    // 页面加载时立即更新一次
    updateSystemStatus();
}

// 快速日期设置函数
function setQuickDate(type) {
    const today = new Date();
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (!startDateInput || !endDateInput) return;
    
    const todayStr = today.toISOString().split('T')[0];
    
    switch(type) {
        case 'today':
            startDateInput.value = todayStr;
            endDateInput.value = todayStr;
            break;
        case 'yesterday':
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            const yesterdayStr = yesterday.toISOString().split('T')[0];
            startDateInput.value = yesterdayStr;
            endDateInput.value = yesterdayStr;
            break;
        case 'week':
            const weekAgo = new Date(today);
            weekAgo.setDate(weekAgo.getDate() - 7);
            const weekAgoStr = weekAgo.toISOString().split('T')[0];
            startDateInput.value = weekAgoStr;
            endDateInput.value = todayStr;
            break;
        case 'month':
            const monthAgo = new Date(today);
            monthAgo.setDate(monthAgo.getDate() - 30);
            const monthAgoStr = monthAgo.toISOString().split('T')[0];
            startDateInput.value = monthAgoStr;
            endDateInput.value = todayStr;
            break;
    }
    
    // 自动提交表单
    const form = document.querySelector('form');
    if (form) {
        form.submit();
    }
}

// 复制功能
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bi bi-check"></i> 已复制';
        button.classList.replace('btn-outline-secondary', 'btn-success');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.replace('btn-success', 'btn-outline-secondary');
        }, 2000);
    });
}

// 添加复制按钮到各个文本区域
document.addEventListener('DOMContentLoaded', function() {
    const textAreas = document.querySelectorAll('.content-box');
    textAreas.forEach(function(area, index) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-outline-secondary btn-sm float-end mb-2';
        copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> 复制';
        copyBtn.onclick = function() {
            const textElement = area.querySelector('p');
            if (textElement) {
                copyToClipboard(textElement.textContent, this);
            }
        };
        area.insertBefore(copyBtn, area.firstChild);
    });
}); 