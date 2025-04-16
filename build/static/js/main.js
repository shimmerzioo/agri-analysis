// 全局函数和工具

// 格式化数字，添加千位分隔符
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

// 生成随机颜色
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// 设置活动导航项
$(document).ready(function() {
    // 获取当前URL路径
    const path = window.location.pathname;
    
    // 设置对应的导航项为活动状态
    $('.navbar-nav .nav-link').each(function() {
        const href = $(this).attr('href');
        if (path === href) {
            $(this).addClass('active');
        }
    });
});