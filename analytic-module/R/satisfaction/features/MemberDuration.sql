SELECT t2.id AS q_id, NOW() - t1.date_joined AS member_duration FROM
    auth_user AS t1,
    forum_node AS t2
WHERE
    t2.node_type='question' AND
    t2.author_id=t1.id;
