SELECT id AS q_id, HOUR(added_at) AS post_time FROM
    forum_node
WHERE
    node_type='question'
