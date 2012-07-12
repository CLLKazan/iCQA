SELECT t1.q_id, AVG(t1.count) AS avg_ans_num_for_user FROM
    (
        SELECT t3.id AS q_id, COUNT(*) AS count FROM 
            forum_node AS t1, 
            forum_node AS t2,
            forum_node AS t3
        WHERE 
            t3.node_type='question' AND
            t1.node_type='answer' AND 
            t1.parent_id=t2.id AND
            t2.author_id=t3.author_id AND
            t1.added_at<t3.added_at
        GROUP BY t3.id,t2.id
    ) AS t1
GROUP BY t1.q_id;
