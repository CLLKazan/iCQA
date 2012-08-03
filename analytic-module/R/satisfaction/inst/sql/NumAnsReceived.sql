SELECT t3.id AS q_id, COUNT(*) AS num_ans_received FROM
    forum_node AS t1,
    forum_node AS t2,
    forum_node AS t3
WHERE
    t1.id=t2.parent_id AND
    t2.node_type='answer' AND
    t1.author_id=t3.author_id AND
    t2.added_at<t3.added_at AND
    t3.node_type='question'
GROUP BY t3.id;
