-- 1. 总体转化率
SELECT 
    COUNT(*) AS total_users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
FROM converted_features;

-- 2. 按设备类型统计转化率
SELECT 
    device,
    COUNT(*) AS total_users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
FROM converted_features
GROUP BY device
ORDER BY conversion_rate DESC;

-- 3. 按国家统计转化率
SELECT 
    country,
    COUNT(*) AS total_users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
FROM converted_features
GROUP BY country
ORDER BY conversion_rate DESC;

-- 4. 访问次数 vs 转化率分段（访问次数越多，是否更容易转化？）
SELECT 
    CASE 
        WHEN num_visits <= 2 THEN 'Low (1-2)'
        WHEN num_visits <= 4 THEN 'Medium (3-4)'
        ELSE 'High (5+)'
    END AS visit_segment,
    COUNT(*) AS total_users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
FROM converted_features
GROUP BY visit_segment
ORDER BY conversion_rate DESC;

-- 5. 会话时长 vs 转化率分段
SELECT 
    CASE 
        WHEN session_duration < 15 THEN '<15min'
        WHEN session_duration BETWEEN 15 AND 30 THEN '15-30min'
        ELSE '30+min'
    END AS session_segment,
    COUNT(*) AS total_users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
FROM converted_features
GROUP BY session_segment
ORDER BY conversion_rate DESC;