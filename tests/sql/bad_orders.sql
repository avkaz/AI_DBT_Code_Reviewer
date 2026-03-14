SELECT *
FROM prod.sales.orders o
LEFT JOIN prod.sales.payments p
    ON o.order_id = p.order_id
LEFT JOIN prod.sales.shipments s
    ON o.order_id = s.order_id
LEFT JOIN prod.sales.customers c
    ON o.customer_id = c.customer_id