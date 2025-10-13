const {buildGraph} = require('libs/datalens/v3');

console.log('Начинаем построение графика');

// Стандартное построение графика
const result = buildGraph({
    apiVersion: '2',
    data: Editor.getLoadedData(),
    shared: Editor.getSharedData(),
    params: Editor.getParams(),
    actionParams: Editor.getActionParams(),
    widgetConfig: Editor.getWidgetConfig(),
    Editor,
});

try {
    console.log('Модифицируем данные графиков');
    
    // Модифицируем данные, но сохраняем координаты для отображения графика
    if (result.graphs && Array.isArray(result.graphs)) {
        console.log('Количество графиков:', result.graphs.length);
        
        result.graphs.forEach((graph, graphIndex) => {
            if (!graph.custom) graph.custom = {};
            
            // Устанавливаем пустые заголовки для координат
            graph.custom.xTitle = "";
            graph.custom.yTitle = "";
            
            // Устанавливаем необходимые заголовки для нужных полей
            graph.custom.pointTitle = "Уровень негатива в треде";
            graph.custom.colorTitle = "Название";
            graph.custom.sizeTitle = "Размер";
            graph.custom.threadTitleHeader = "Тема треда";
            
            // Получаем базовый цвет графика для создания градиентов
            const baseColor = graph.color || '#7cb5ec'; // Стандартный цвет Highcharts, если свой не задан
            
            // Для каждой точки данных
            if (graph.data && Array.isArray(graph.data)) {
                console.log(`График #${graphIndex}: количество точек = ${graph.data.length}`);
                
                // Находим минимальный и максимальный размер для нормализации
                let minSize = Infinity;
                let maxSize = -Infinity;
                
                graph.data.forEach(point => {
                    if (point.sizeValue !== undefined) {
                        minSize = Math.min(minSize, point.sizeValue);
                        maxSize = Math.max(maxSize, point.sizeValue);
                    }
                });
                
                console.log(`Диапазон размеров для графика #${graphIndex}: min=${minSize}, max=${maxSize}`);
                
                graph.data.forEach((point, pointIndex) => {
                    if (!point.custom) point.custom = {};
                    
                    // Скрываем метки координат
                    point.xLabel = "";
                    point.yLabel = "";
                    
                    // Нормализуем размеры точек, чтобы они не так сильно отличались
                    // Используем логарифмическую шкалу для лучшего визуального восприятия
                    if (point.sizeValue !== undefined && maxSize > minSize) {
                        // Сохраняем оригинальный размер
                        point.custom.originalSize = point.sizeValue;
                        
                        // Нормализуем размер в диапазоне от 3 до 12
                        // Используем логарифмическую шкалу для более равномерного распределения
                        const normalizedSize = minSize === maxSize
                            ? 7.5 // Средний размер, если все точки одинаковые
                            : 3 + 9 * (Math.log(point.sizeValue - minSize + 1) / Math.log(maxSize - minSize + 1));
                        
                        // Устанавливаем новый размер и стиль для маркера
                        point.marker = point.marker || {};
                        point.marker.radius = normalizedSize;
                        
                        // Убираем обводку
                        point.marker.lineWidth = 0;
                        
                        // Для создания эффекта объемности используем радиальный градиент
                        // Анализируем базовый цвет и создаем градиент со светотенью
                        let pointColor = point.color || baseColor;
                        // Убедимся, что цвет в формате hex или rgb
                        if (!pointColor.startsWith('#') && !pointColor.startsWith('rgb')) {
                            pointColor = baseColor;
                        }
                        
                        point.marker.fillColor = {
                            radialGradient: { 
                                cx: 0.35, // Смещаем центр градиента влево для эффекта света справа
                                cy: 0.35, // Смещаем центр вверх для эффекта света сверху
                                r: 0.65   // Радиус градиента для более мягкого перехода
                            },
                            stops: [
                                // Блик в верхнем левом углу (очень светлый)
                                [0, lightenColor(pointColor, 0.9)],
                                // Основной цвет примерно в центре (немного светлее базового)
                                [0.3, lightenColor(pointColor, 0.3)],
                                // Основной цвет точки
                                [0.6, pointColor],
                                // Затемненный цвет для создания тени (темнее базового)
                                [1, darkenColor(pointColor, 0.3)]
                            ]
                        };
                        
                        // Добавляем мягкую тень для усиления 3D-эффекта
                        point.marker.shadow = true;
                        point.marker.shadowWidth = 3;
                        point.marker.shadowBlur = 10;
                        point.marker.shadowColor = 'rgba(0, 0, 0, 0.25)';
                        point.marker.shadowOffsetX = 1;
                        point.marker.shadowOffsetY = 1;
                    }
                    
                    // Добавляем данные для тултипа
                    point.custom.colorTitle = point.colorValue || 
                                             (point.cLabel && point.cLabel.__wrappedMd__) || 
                                             "Название неизвестно";
                    
                    // Извлекаем тему треда и уровень негатива
                    try {
                        if (point.name && point.name.__wrappedMarkup__ && 
                            point.name.__wrappedMarkup__.children) {
                            
                            // Для темы треда
                            let threadTitle = "Н/Д";
                            if (point.name.__wrappedMarkup__.children[0] && 
                                point.name.__wrappedMarkup__.children[0].children && 
                                point.name.__wrappedMarkup__.children[0].children[0] && 
                                point.name.__wrappedMarkup__.children[0].children[0].children && 
                                point.name.__wrappedMarkup__.children[0].children[0].children[0] && 
                                point.name.__wrappedMarkup__.children[0].children[0].children[0].children && 
                                point.name.__wrappedMarkup__.children[0].children[0].children[0].children[0] && 
                                point.name.__wrappedMarkup__.children[0].children[0].children[0].children[0].content) {
                                
                                threadTitle = point.name.__wrappedMarkup__.children[0].children[0].children[0].children[0].content;
                            }
                            point.custom.threadTitle = threadTitle;
                            
                            // Для уровня негатива
                            let negativeLevel = "Н/Д";
                            if (point.name.__wrappedMarkup__.children[1] && 
                                point.name.__wrappedMarkup__.children[1].content) {
                                negativeLevel = point.name.__wrappedMarkup__.children[1].content;
                            }
                            point.custom.pointTitle = negativeLevel;
                        } else {
                            point.custom.threadTitle = "Н/Д";
                            point.custom.pointTitle = "Н/Д";
                        }
                    } catch (e) {
                        console.error(`Ошибка при извлечении данных для точки ${pointIndex}:`, e.message);
                        point.custom.threadTitle = "Ошибка извлечения темы";
                        point.custom.pointTitle = "Ошибка извлечения уровня негатива";
                    }
                });
            }
            
            // Настраиваем tooltipOptions на уровне графика
            graph.tooltipOptions = {
                followPointer: true,
                headerFormat: '',
                pointFormat: '',
                footerFormat: '',
                hideDelay: 100,
                xDateFormat: null,
                shared: false
            };
        });
        
        console.log('Модификация данных завершена успешно');
    } else {
        console.log('Нет графиков для модификации');
    }
} catch (e) {
    console.error('Ошибка при модификации данных:', e);
}

// Вспомогательная функция для осветления цвета
function lightenColor(color, factor) {
    // Если цвет в формате RGB/RGBA
    if (color.startsWith('rgb')) {
        // Извлекаем значения RGB
        const rgb = color.match(/\d+/g);
        if (rgb && rgb.length >= 3) {
            const r = parseInt(rgb[0]);
            const g = parseInt(rgb[1]);
            const b = parseInt(rgb[2]);
            // Осветляем, добавляя процент к каждому компоненту
            const newR = Math.min(255, r + (255 - r) * factor);
            const newG = Math.min(255, g + (255 - g) * factor);
            const newB = Math.min(255, b + (255 - b) * factor);
            
            // Сохраняем оригинальный альфа-канал, если он есть
            if (rgb.length > 3) {
                return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, ${rgb[3]})`;
            } else {
                return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, 1)`;
            }
        }
    }
    // Если цвет в формате HEX
    else if (color.startsWith('#')) {
        // Преобразуем HEX в RGB
        let hex = color.slice(1);
        // Расширяем сокращенный формат #RGB до #RRGGBB
        if (hex.length === 3) {
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        
        // Осветляем
        const newR = Math.min(255, r + (255 - r) * factor);
        const newG = Math.min(255, g + (255 - g) * factor);
        const newB = Math.min(255, b + (255 - b) * factor);
        
        return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, 1)`;
    }
    
    // Если формат цвета не распознан, возвращаем исходный цвет
    return color;
}

// Вспомогательная функция для затемнения цвета
function darkenColor(color, factor) {
    // Если цвет в формате RGB/RGBA
    if (color.startsWith('rgb')) {
        // Извлекаем значения RGB
        const rgb = color.match(/\d+/g);
        if (rgb && rgb.length >= 3) {
            const r = parseInt(rgb[0]);
            const g = parseInt(rgb[1]);
            const b = parseInt(rgb[2]);
            // Затемняем, уменьшая каждый компонент
            const newR = r * (1 - factor);
            const newG = g * (1 - factor);
            const newB = b * (1 - factor);
            
            // Сохраняем оригинальный альфа-канал, если он есть
            if (rgb.length > 3) {
                return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, ${rgb[3]})`;
            } else {
                return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, 1)`;
            }
        }
    }
    // Если цвет в формате HEX
    else if (color.startsWith('#')) {
        // Преобразуем HEX в RGB
        let hex = color.slice(1);
        // Расширяем сокращенный формат #RGB до #RRGGBB
        if (hex.length === 3) {
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        
        // Затемняем
        const newR = r * (1 - factor);
        const newG = g * (1 - factor);
        const newB = b * (1 - factor);
        
        return `rgba(${Math.round(newR)}, ${Math.round(newG)}, ${Math.round(newB)}, 1)`;
    }
    
    // Если формат цвета не распознан, возвращаем исходный цвет
    return color;
}

// Создаем функцию для генерации тултипа с CSS для скрытия x и y
function generateTooltipHTML(point) {
    return '<div class="custom-tooltip-container" style="position: relative; padding: 10px; max-width: 250px; font-family: Arial, sans-serif; background-color: white; border: 1px solid #cccccc; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 9999;">' +
           // CSS для скрытия стандартных меток x и y
           '<style>' +
           '.highcharts-tooltip span:contains("x:"), ' +
           '.highcharts-tooltip span:contains("y:"), ' +
           '.highcharts-tooltip-box + g span:contains("x:"), ' +
           '.highcharts-tooltip-box + g span:contains("y:") {' +
           '    display: none !important;' +
           '    visibility: hidden !important;' +
           '    opacity: 0 !important;' +
           '    height: 0 !important;' +
           '    overflow: hidden !important;' +
           '}' +
           '</style>' +
           // Заголовок (название серии)
           '<span style="font-weight: bold; display: block; margin-bottom: 10px; color: ' + point.color + ';">' + 
           point.series.name + '</span>' +
           // Таблица с данными
           '<table style="width: 100%; border-collapse: collapse;">' +
           '<tr><td style="font-weight: bold; padding: 3px 8px 3px 0;">Название:</td><td>' + (point.point.custom?.colorTitle || 'Н/Д') + '</td></tr>' +
           '<tr><td style="font-weight: bold; padding: 3px 8px 3px 0;">Тема треда:</td><td>' + (point.point.custom?.threadTitle || 'Н/Д') + '</td></tr>' +
           '<tr><td style="font-weight: bold; padding: 3px 8px 3px 0;">Размер:</td><td>' + (point.point.custom?.originalSize || point.point.sizeValue || 'Н/Д') + '</td></tr>' +
           '<tr><td style="font-weight: bold; padding: 3px 8px 3px 0;">Уровень негатива:</td><td>' + (point.point.custom?.pointTitle || 'Н/Д') + '</td></tr>' +
           '</table>' +
           '</div>';
}

// Используем updateHighchartsConfig для настройки тултипа и стилизации графика
Editor.updateHighchartsConfig = (config) => {
    console.log('Настраиваем конфигурацию Highcharts');
    
    // Настраиваем глобальные параметры чарта
    config.chart = config.chart || {};
    config.chart.style = config.chart.style || {};
    config.chart.style.fontFamily = 'Arial, sans-serif';
    
    // Настраиваем глобальные параметры для придания объемного эффекта
    config.plotOptions = config.plotOptions || {};
    config.plotOptions.scatter = config.plotOptions.scatter || {};
    
    // Глобальные настройки маркеров для всех серий
    config.plotOptions.scatter.marker = {
        // Убираем обводку
        lineWidth: 0,
        // Эффект объемности через градиент (будет переопределен для каждой серии)
        fillColor: {
            radialGradient: { cx: 0.35, cy: 0.35, r: 0.65 },
            stops: [
                [0, 'rgba(255,255,255,0.9)'],
                [0.3, 'rgba(240,240,240,0.8)'],
                [0.6, 'rgba(210,210,210,0.6)'],
                [1, 'rgba(180,180,180,0.4)']
            ]
        },
        // Добавляем тень для объемного эффекта
        shadow: true,
        shadowWidth: 3,
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.25)',
        shadowOffsetX: 1,
        shadowOffsetY: 1,
        // Тип маркера - круг для лучшего объемного эффекта
        symbol: 'circle',
        // Состояние при наведении - увеличиваем и делаем ярче
        states: {
            hover: {
                enabled: true,
                lineWidth: 0, // Без обводки
                radiusPlus: 2, // Увеличиваем размер при наведении
                brightness: 0.2 // Делаем ярче при наведении
            }
        }
    };
    
    // Добавляем эффект объемности для всех серий
    if (config.series && Array.isArray(config.series)) {
        config.series.forEach((series, index) => {
            console.log(`Настраиваем объемный эффект для серии #${index}`);
            
            // Устанавливаем тип серии scatter для лучшей поддержки настроек маркеров
            series.type = 'scatter';
            
            // Настраиваем маркеры для каждой серии
            series.marker = series.marker || {};
            series.marker.lineWidth = 0; // Без обводки
            
            // Создаем градиент на основе цвета серии для объемного эффекта
            const seriesColor = series.color || '#7cb5ec'; // Стандартный цвет Highcharts, если свой не задан
            
            series.marker.fillColor = {
                radialGradient: { cx: 0.35, cy: 0.35, r: 0.65 },
                stops: [
                    [0, lightenColor(seriesColor, 0.9)], // Очень светлый блик
                    [0.3, lightenColor(seriesColor, 0.3)], // Чуть светлее основного цвета
                    [0.6, seriesColor], // Основной цвет
                    [1, darkenColor(seriesColor, 0.3)] // Затемнённый край для тени
                ]
            };
            
            // Добавляем тень
            series.marker.shadow = true;
            series.marker.shadowWidth = 3;
            series.marker.shadowBlur = 10;
            series.marker.shadowColor = 'rgba(0, 0, 0, 0.25)';
            series.marker.shadowOffsetX = 1;
            series.marker.shadowOffsetY = 1;
            
            // Настраиваем состояние при наведении
            series.marker.states = {
                hover: {
                    enabled: true,
                    lineWidth: 0,
                    radiusPlus: 2,
                    brightness: 0.2
                }
            };
        });
    }
    
    // Отключаем кредиты
    config.credits = { enabled: false };
    
    // Настраиваем тултип с усиленной защитой от появления x и y
    config.tooltip = {
        enabled: true,
        useHTML: true,
        
        // Отключаем стандартные форматы
        headerFormat: '',
        pointFormat: '',
        footerFormat: '',
        
        // Отключаем форматирование значений
        valueDecimals: null,
        valuePrefix: '',
        valueSuffix: '',
        xDateFormat: null,
        
        // Отключаем общий тултип
        shared: false,
        split: false,
        
        // Кастомный форматтер с CSS-защитой
        formatter: function() {
            console.log('Форматирование тултипа для точки');
            return generateTooltipHTML(this);
        },
        
        // Кастомное позиционирование
        positioner: function(labelWidth, labelHeight, point) {
            return {
                x: point.plotX + this.chart.plotLeft,
                y: point.plotY + this.chart.plotTop - labelHeight - 10
            };
        }
    };
    
    // Настраиваем plotOptions для отключения стандартных тултипов на всех уровнях
    config.plotOptions.series = config.plotOptions.series || {};
    config.plotOptions.series.tooltip = {
        headerFormat: '',
        pointFormat: '',
        footerFormat: ''
    };
    
    // Устанавливаем настройки для каждой серии
    if (config.series && Array.isArray(config.series)) {
        config.series.forEach((series) => {
            series.tooltip = {
                headerFormat: '',
                pointFormat: '',
                footerFormat: ''
            };
        });
    }
    
    // Добавляем обработчик события load для дополнительной защиты
    const originalLoad = config.chart.events?.load;
    config.chart.events = config.chart.events || {};
    config.chart.events.load = function() {
        console.log('Событие load графика');
        
        // Вызываем оригинальный обработчик, если он был
        if (typeof originalLoad === 'function') {
            originalLoad.apply(this, arguments);
        }
        
        // Добавляем глобальные CSS стили для скрытия меток x и y
        try {
            if (typeof document !== 'undefined') {
                const styleEl = document.createElement('style');
                styleEl.textContent = `
                    .highcharts-tooltip span:contains("x:"),
                    .highcharts-tooltip span:contains("y:") {
                        display: none !important;
                        visibility: hidden !important;
                    }
                `;
                document.head.appendChild(styleEl);
                console.log('Добавлены глобальные CSS стили');
            }
        } catch (e) {
            console.error('Ошибка при добавлении CSS:', e);
        }
        
        // Перехватываем метод refresh тултипа
        try {
            if (this.tooltip) {
                const originalRefresh = this.tooltip.refresh;
                this.tooltip.refresh = function(point) {
                    originalRefresh.apply(this, arguments);
                    
                    // После обновления тултипа скрываем ненужные элементы
                    setTimeout(() => {
                        const container = document.querySelector('.highcharts-tooltip');
                        if (container) {
                            const spans = container.querySelectorAll('span');
                            spans.forEach(span => {
                                if (span.textContent.includes('x:') || span.textContent.includes('y:')) {
                                    span.style.display = 'none';
                                    span.style.visibility = 'hidden';
                                    span.innerHTML = '';
                                }
                            });
                        }
                    }, 0);
                };
                console.log('Метод refresh тултипа перехвачен');
            }
        } catch (e) {
            console.error('Ошибка при перехвате метода refresh:', e);
        }
    };
    
    console.log('Конфигурация Highcharts успешно настроена');
    return config;
};

console.log('Результат построения графика:', result ? 'успешно' : 'неудача');

module.exports = result;
