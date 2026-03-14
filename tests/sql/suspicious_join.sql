WITH events AS (

    SELECT
        order_id,
        event_type
    FROM analytics.events

)

SELECT
    o.customer_id,
    COUNT(e.event_type)
FROM analytics.orders o
JOIN events e
    ON o.order_id = e.order_id