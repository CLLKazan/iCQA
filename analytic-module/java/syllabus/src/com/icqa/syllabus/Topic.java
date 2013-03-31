package com.icqa.syllabus;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import java.util.ArrayList;

/**
 * Created with IntelliJ IDEA.
 * User: ramis
 * Date: 3/24/13
 * Time: 9:44 PM
 * To change this template use File | Settings | File Templates.
 */
public class Topic {
    public String mTitle;
    public ArrayList<Post> mPosts = new ArrayList<Post>();
    public ArrayList<Topic> mChildren = null;
    public Topic mParent = null;

    public static class Post{
        long id;
        String title;
        String body;
        int score;
        boolean marked;
        ArrayList<Post> answers = null;

        public Post(long id, String title, String body, int score, boolean marked, ArrayList<Post> answers){
            this.id = id;
            this.title = title;
            this.body = body;
            this.answers = answers;
            this.score = score;
            this.marked = marked;
        }

        public String toJSON(){
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", id);
            jsonObject.put("title", title);
            jsonObject.put("body", body);
            jsonObject.put("score", score);
            jsonObject.put("marked", marked);
            if(answers != null && answers.size() > 0){
                ArrayList<String> answersString = new ArrayList<String>(answers.size());
                for(Post answer : answers){
                    answersString.add(answer.toJSON());
                }
                jsonObject.put("answers", JSONArray.fromObject(answersString));
            }
            return jsonObject.toString();
        }
    }

    public Topic(String title, ArrayList<Post> posts, ArrayList<Topic> children){
        mTitle = title;
        mPosts = posts;
        mChildren = children;
    }

    public Topic(JSONObject jsonObject, Topic parent){
        mParent = parent;
        mTitle = jsonObject.getString("title");
        JSONArray jsonArray = jsonObject.optJSONArray("children");
        if(jsonArray != null){
            mChildren = new ArrayList<Topic>(jsonArray.size());
            for(int i=0; i<jsonArray.size(); ++i)
                mChildren.add(new Topic(jsonArray.getJSONObject(i), this));
        }
    }

    public String toString(){
        return mTitle;
    }

    public boolean hasChildren(){
        return mChildren != null && mChildren.size() > 0;
    }

    public String toJSON(){
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("title", mTitle);
        if(hasChildren()){
            ArrayList<String> childrenString = new ArrayList<String>(mChildren.size());
            for(Topic answer : mChildren){
                childrenString.add(answer.toJSON());
            }
            jsonObject.put("children", JSONArray.fromObject(childrenString));
        }
        return jsonObject.toString();
    }
}
