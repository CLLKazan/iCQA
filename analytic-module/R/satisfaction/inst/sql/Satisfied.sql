SELECT t1.id AS q_id, IF(t2.q_id,TRUE,FALSE) AS satisfied FROM
    forum_node AS t1 LEFT JOIN
    (
        SELECT t1.id AS q_id FROM 
            forum_node AS t1,
            forum_node AS t2
        WHERE
            t2.node_type='answer' AND
            t2.state_string='(accepted)' AND
            t2.parent_id=t1.id
    ) AS t2 ON t1.id=t2.q_id
WHERE
    t1.node_type='question';
