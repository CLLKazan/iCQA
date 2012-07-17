SELECT t4.id AS q_id, COUNT(*) AS num_ans_accepted FROM
    forum_node AS t1,
    forum_node AS t2,
    forum_action AS t3,
    forum_node AS t4
WHERE
    t1.author_id=t4.author_id AND
    t2.parent_id=t1.id AND
    t3.node_id=t2.id AND
    t3.action_type='acceptanswer' AND
    t3.action_date<t4.added_at AND
    t4.node_type='question'
GROUP BY t4.id;
