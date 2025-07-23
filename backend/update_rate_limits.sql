-- Update rate limits for voice analysis to allow proper testing and deployment
-- This significantly increases the limits to prevent the fast failure issue

-- Update free tier voice analysis limits
UPDATE rate_limit_config 
SET 
    requests_per_minute = 50,
    requests_per_hour = 500, 
    requests_per_day = 2000,
    burst_allowance = 20
WHERE tier = 'free' AND endpoint = 'voice_analysis';

-- Update premium tier voice analysis limits  
UPDATE rate_limit_config 
SET 
    requests_per_minute = 100,
    requests_per_hour = 1000,
    requests_per_day = 10000, 
    burst_allowance = 50
WHERE tier = 'premium' AND endpoint = 'voice_analysis';

-- Verify the updates
SELECT tier, endpoint, requests_per_minute, requests_per_hour, requests_per_day, burst_allowance 
FROM rate_limit_config 
WHERE endpoint = 'voice_analysis'
ORDER BY tier; 