package com.icqa.syllabus;


import com.amazonaws.mturk.addon.HITDataCSVReader;
import com.amazonaws.mturk.addon.HITDataCSVWriter;
import com.amazonaws.mturk.addon.HITDataInput;
import com.amazonaws.mturk.addon.HITDataOutput;
import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.addon.HITQuestion;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.apache.commons.lang.StringUtils;
import org.apache.lucene.queryParser.ParseException;

import java.awt.image.AreaAveragingScaleFilter;
import java.io.*;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.Random;


public class Mturk {

    public static final int POSTS_COUNT = 2;
    public static final int HITS_COUNT = 10;
    // Defining the locations of the input files
    private RequesterService service;
    private static String inputFile = "mturk.input";
    private static String propertiesFile = "mturkHIT.properties";
    private static String questionFile = "mturk.question";

    public Mturk() {
        service = new RequesterService(new PropertiesClientConfig("mturk.properties"));
    }

    /**
     * Check to see if there are sufficient funds.
     * @return true if there are sufficient funds.  False otherwise.
     */
    public boolean hasEnoughFund() {
        double balance = service.getAccountBalance();
        System.out.println("Got account balance: " + RequesterService.formatCurrency(balance));
        return balance > 0;
    }

    /**
     * Create the website category HITs.
     *
     */
    public void createSiteCategoryHITs() {
        try {

            //Loading the input file.  The input file is a tab delimited file where the first row
            //defines the fields/variables and the remaining rows contain the values for each HIT.
            //Each row represents a unique HIT.  The SDK uses the Apache Velocity engine to merge
            //the input values into a templatized QAP file.
            //Please refer to http://velocity.apache.org for more details on this engine and
            //how to specify variable names.  Apache Velocity is fully supported so there may be
            //additional functionality you can take advantage of if you know the Velocity syntax.
            HITDataInput input = new HITDataCSVReader(inputFile);

            //Loading the question (QAP) file.  This QAP file contains Apache Velocity variable names where the values
            //from the input file are to be inserted.  Essentially the QAP becomes a template for the input file.
            HITQuestion question = new HITQuestion(questionFile);

            //Loading the HIT properties file.  The properties file defines two system qualifications that will
            //be used for the HIT.  The properties file can also be a Velocity template.  Currently, only
            //the "annotation" field is allowed to be a Velocity template variable.  This allows the developer
            //to "tie in" the input value to the results.
            HITProperties props = new HITProperties(propertiesFile);

            HIT[] hits = null;

            // Create multiple HITs using the input, properties, and question files

            System.out.println("--[Loading HITs]----------");
            Date startTime = new Date();
            System.out.println("  Start time: " + startTime);

            //The simpliest way to bulk load a large number of HITs where all details are defined in files.
            //When using this method, it will automatically create output files of the following type:
            //  - <your input file name>.success - A file containing the HIT IDs and HIT Type IDs of
            //                                     all HITs that were successfully loaded.  This file will
            //                                     not exist if there are no HITs successfully loaded.
            //  - <your input file name>.failure - A file containing the input rows that failed to load.
            //                                     This file will not exist if there are no failures.
            //The .success file can be used in subsequent operations to retrieve the results that workers submitted.
            HITDataOutput success = new HITDataCSVWriter(inputFile + ".success");
            HITDataOutput failure = new HITDataCSVWriter(inputFile + ".failure");
            hits = service.createHITs(input, props, question, success, failure);

            System.out.println("--[End Loading HITs]----------");
            Date endTime = new Date();
            System.out.println("  End time: " + endTime);
            System.out.println("--[Done Loading HITs]----------");
            System.out.println("  Total load time: " + (endTime.getTime() - startTime.getTime())/1000 + " seconds.");

            if (hits == null) {
                throw new Exception("Could not create HITs");
            }

        } catch (Exception e) {
            System.err.println(e.getLocalizedMessage());
        }
    }


    Random random = new Random();

    public String pickPosts(ArrayList<SyllabusItem> syllabusItems){

        ArrayList<String> posts = new ArrayList<String>();

        for(SyllabusItem item : syllabusItems){
            for(int i=0; i < POSTS_COUNT; ++i){
                int idx = random.nextInt(item.mPosts.size());
                posts.add(item.mPosts.get(idx).toJSON());
            }
        }

        Collections.shuffle(posts);
        return StringUtils.join(posts, ",");
    }

    public void createInputFile(){
        try{
            StringBuilder templateBuilder = new StringBuilder();
            BufferedReader reader = new BufferedReader(new FileReader("/home/ramis/amt.html"));
            String line1;
            while((line1 = reader.readLine()) != null){
                templateBuilder.append(line1);
                templateBuilder.append("\n");
            }
            String template = templateBuilder.toString();

            ArrayList<String> syllabus = Main.getSyllabus();
            Connection connection = Main.getConnection();
            PreparedStatement selectStatement = connection.prepareStatement("SELECT * FROM forum_node WHERE id=?");


            BM25FSearch bm25FSearch = new BM25FSearch(Main.BM_25_F_PARAMETERS);

            ArrayList<SyllabusItem> syllabusItems = new ArrayList<SyllabusItem>(syllabus.size());
            for(String line : syllabus){
                long[] docIds = bm25FSearch.getTopN(line, 5);

                ArrayList<SyllabusItem.Post> posts = new ArrayList<SyllabusItem.Post>(docIds.length);
                for(long id : docIds){
                    selectStatement.setLong(1, id);
                    selectStatement.execute();
                    ResultSet resultSet = selectStatement.getResultSet();
                    if(resultSet.next()){
                        posts.add(new SyllabusItem.Post(id, resultSet.getString("title"),
                                resultSet.getString("body"), "Answer Not Available"/*resultSet.getString("answer")*/));
                    }
                }

                syllabusItems.add(new SyllabusItem(line, posts));
            }

            String syllabusLine = JSONArray.fromObject(syllabus.toArray()).toString();
            for(int i=0; i < HITS_COUNT; ++i){
                String postsString = pickPosts(syllabusItems);
                String html = template.replace("$syllabus$", syllabusLine).replace("$posts$", postsString);
                BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter("hit" + i + ".html"));
                bufferedWriter.write(html);
                bufferedWriter.close();
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {

        Mturk app = new Mturk();

        if (app.hasEnoughFund()) {
            //app.createInputFile();
            app.createSiteCategoryHITs();
        }
    }
}
