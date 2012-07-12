SELECT t1.q_id, AVG(t1.ans_num) AS avg_ans_num_ph_tag FROM
    (
        SELECT COUNT(*) AS ans_num, t2.tag_id, t3.id AS q_id
        FROM 
            forum_node AS t1, 
            forum_node_tags AS t2, 
            forum_node AS t3,
            (SELECT tag_id,node_id FROM forum_node_tags GROUP BY node_id ORDER BY id) AS t4
        WHERE 
            t1.parent_id=t2.node_id AND 
            t3.node_type='question' AND
            t1.node_type='answer' AND
            t1.added_at < t3.added_at AND
            t2.tag_id=t4.tag_id AND t3.id=t4.node_id
        GROUP BY DATE_FORMAT(t1.added_at, '%Y %m %d %H'),t4.tag_id,t4.node_id
    ) AS t1
GROUP BY t1.tag_id,t1.q_id;
