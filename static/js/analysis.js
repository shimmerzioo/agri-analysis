// ... 现有代码 ...

// 修改初始化函数，添加联动过滤功能
function initAnalysisPage() {
    // 加载元数据
    fetch('/api/metadata/')
        .then(response => response.json())
        .then(data => {
            // 保存完整的元数据
            window.fullMetadata = data;
            
            // 初始化国家/地区选择器
            const countrySelect = document.getElementById('country-select');
            data.countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countrySelect.appendChild(option);
            });
            
            // 初始化商品选择器
            const commoditySelect = document.getElementById('commodity-select');
            data.commodities.forEach(commodity => {
                const option = document.createElement('option');
                option.value = commodity;
                option.textContent = commodity;
                commoditySelect.appendChild(option);
            });
            
            // 初始化指标选择器
            const elementSelect = document.getElementById('element-select');
            data.elements.forEach(element => {
                const option = document.createElement('option');
                option.value = element;
                option.textContent = element;
                elementSelect.appendChild(option);
            });
            
            // 初始化年份范围选择器
            const startYearSelect = document.getElementById('start-year-select');
            const endYearSelect = document.getElementById('end-year-select');
            
            data.years.forEach(year => {
                const startOption = document.createElement('option');
                startOption.value = year;
                startOption.textContent = year;
                startYearSelect.appendChild(startOption);
                
                const endOption = document.createElement('option');
                endOption.value = year;
                endOption.textContent = year;
                endYearSelect.appendChild(endOption);
            });
            
            // 设置默认值
            if (data.years.length > 0) {
                startYearSelect.value = data.years[0];
                endYearSelect.value = data.years[data.years.length - 1];
            }
            
            // 添加联动过滤事件监听器
            countrySelect.addEventListener('change', updateAvailableOptions);
            commoditySelect.addEventListener('change', updateAvailableOptions);
            elementSelect.addEventListener('change', updateAvailableOptions);
            
            // 初始化多选插件
            $(countrySelect).select2({
                placeholder: '选择国家/地区',
                allowClear: true,
                multiple: true
            });
            
            // 添加联动过滤事件监听器
            countrySelect.addEventListener('change', updateAvailableOptions);
            commoditySelect.addEventListener('change', updateAvailableOptions);
            elementSelect.addEventListener('change', updateAvailableOptions);
            
            // 初始加载可用选项
            updateAvailableOptions();
        })
        .catch(error => {
            console.error('加载元数据失败:', error);
            showError('加载元数据失败，请刷新页面重试。');
        });
    
    // 绑定分析按钮事件
    document.getElementById('analyze-btn').addEventListener('click', analyzeData);
    
    // 绑定导出按钮事件
    document.getElementById('export-btn').addEventListener('click', exportData);
}

// 添加新函数：更新可用选项
function updateAvailableOptions() {
    console.log("更新可用选项...");
    
    // 获取当前选择的值
    const countrySelect = document.getElementById('country-select');
    const commoditySelect = document.getElementById('commodity-select');
    const elementSelect = document.getElementById('element-select');
    
    const selectedCountries = Array.from(countrySelect.selectedOptions || []).map(option => option.value);
    const selectedCommodity = commoditySelect.value;
    const selectedElement = elementSelect.value;
    
    console.log("已选国家:", selectedCountries);
    console.log("已选商品:", selectedCommodity);
    console.log("已选指标:", selectedElement);
    
    // 获取可用数据组合
    fetch('/api/data-quality/')
        .then(response => response.json())
        .then(data => {
            console.log("获取到数据质量信息:", data);
            
            // 更新商品选择器
            if (selectedCountries.length > 0) {
                console.log("根据选择的国家过滤商品...");
                // 如果选择了国家，过滤可用的商品
                const availableCommodities = new Set();
                selectedCountries.forEach(country => {
                    if (data.country_commodities[country]) {
                        data.country_commodities[country].forEach(commodity => {
                            availableCommodities.add(commodity);
                        });
                    }
                });
                
                console.log("可用商品:", Array.from(availableCommodities));
                
                // 更新商品选项
                for (let i = 0; i < commoditySelect.options.length; i++) {
                    const option = commoditySelect.options[i];
                    const isAvailable = availableCommodities.has(option.value);
                    option.disabled = !isAvailable;
                    
                    if (option.disabled) {
                        option.classList.add('disabled-option');
                    } else {
                        option.classList.remove('disabled-option');
                    }
                }
            }
            
            // 更新指标选择器
            if (selectedCommodity) {
                console.log("根据选择的商品过滤指标...");
                // 如果选择了商品，过滤可用的指标
                const availableElements = new Set(data.commodity_elements[selectedCommodity] || []);
                
                console.log("可用指标:", Array.from(availableElements));
                
                // 更新指标选项
                for (let i = 0; i < elementSelect.options.length; i++) {
                    const option = elementSelect.options[i];
                    const isAvailable = availableElements.has(option.value);
                    option.disabled = !isAvailable;
                    
                    if (option.disabled) {
                        option.classList.add('disabled-option');
                    } else {
                        option.classList.remove('disabled-option');
                    }
                }
            }
            
            // 更新国家选择器
            if (selectedCommodity && selectedElement) {
                console.log("根据选择的商品和指标过滤国家...");
                // 如果选择了商品和指标，过滤可用的国家
                const availableCountries = new Set();
                
                // 遍历所有国家，检查是否有该商品的该指标数据
                Object.keys(data.country_commodity_elements).forEach(country => {
                    if (data.country_commodity_elements[country][selectedCommodity] && 
                        data.country_commodity_elements[country][selectedCommodity].includes(selectedElement)) {
                        availableCountries.add(country);
                    }
                });
                
                console.log("可用国家:", Array.from(availableCountries));
                
                // 更新国家选项
                for (let i = 0; i < countrySelect.options.length; i++) {
                    const option = countrySelect.options[i];
                    const isAvailable = availableCountries.has(option.value);
                    option.disabled = !isAvailable;
                }
                
                // 重新初始化Select2
                $(countrySelect).select2('destroy');
                $(countrySelect).select2({
                    placeholder: '选择国家/地区',
                    allowClear: true,
                    multiple: true,
                    templateResult: formatCountryOption
                });
            }
            
            // 如果当前选择的选项被禁用，则清除选择
            if (selectedCommodity && commoditySelect.selectedIndex >= 0 && 
                commoditySelect.options[commoditySelect.selectedIndex].disabled) {
                commoditySelect.value = '';
            }
            
            if (selectedElement && elementSelect.selectedIndex >= 0 && 
                elementSelect.options[elementSelect.selectedIndex].disabled) {
                elementSelect.value = '';
            }
            
            // 对于多选的国家，移除被禁用的选项
            if (selectedCountries.length > 0) {
                const selectedValidCountries = selectedCountries.filter(country => {
                    for (let i = 0; i < countrySelect.options.length; i++) {
                        const option = countrySelect.options[i];
                        if (option.value === country && !option.disabled) {
                            return true;
                        }
                    }
                    return false;
                });
                
                if (selectedValidCountries.length !== selectedCountries.length) {
                    console.log("移除无效的国家选择:", selectedCountries.filter(c => !selectedValidCountries.includes(c)));
                    $(countrySelect).val(selectedValidCountries).trigger('change');
                }
            }
        })
        .catch(error => {
            console.error('加载数据质量信息失败:', error);
        });
}

// 格式化国家选项，为禁用选项添加样式
function formatCountryOption(option) {
    if (!option.id) {
        return option.text;
    }
    
    // 查找对应的DOM选项
    let isDisabled = false;
    const countrySelect = document.getElementById('country-select');
    for (let i = 0; i < countrySelect.options.length; i++) {
        if (countrySelect.options[i].value === option.id && countrySelect.options[i].disabled) {
            isDisabled = true;
            break;
        }
    }
    
    if (isDisabled) {
        return $('<span class="disabled-option">' + option.text + ' (无数据)</span>');
    }
    
    return option.text;
}

// 确保页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log("页面加载完成，初始化分析页面...");
    initAnalysisPage();
    
    // 绑定分析按钮事件
    document.getElementById('analyze-btn').addEventListener('click', analyzeData);
    
    // 绑定导出按钮事件
    document.getElementById('export-btn').addEventListener('click', exportData);
});

// ... 其他函数 ...