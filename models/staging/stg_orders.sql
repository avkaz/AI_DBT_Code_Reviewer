
select
    o.*,
    c.name,
    c.email
from database.schema.orders o
join database.schema.customers c on o.customer_id = c.id
join database.schema.products p on o.product_id = p.id
join database.schema.categories cat on p.category_id = cat.id
where o.created_at between '2024-01-01' and '2024-12-31'