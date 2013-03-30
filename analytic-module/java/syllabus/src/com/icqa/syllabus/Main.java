package com.icqa.syllabus;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.util.Version;
import org.jsoup.Jsoup;

import java.io.*;
import java.sql.*;
import java.util.ArrayList;


public class Main {

    public static File INDEX_DIR = new File("index");

    public static final String BM_25_F_PARAMETERS = "BM25FParameters";

    public static String sql = "SELECT node_id, title, body FROM forum_node " +
            "INNER JOIN forum_node_tags ON forum_node.id=forum_node_tags.node_id " +
            "WHERE tag_id=70 AND score>0";

    public static String answer_sql = "SELECT parent_id, GROUP_CONCAT(body) as answer, MAX(marked) as marked " +
            "FROM forum_node WHERE parent_id=? GROUP BY parent_id";

    public static String asql = "SELECT node_id, title, body, answer FROM (\n" +
            "  SELECT * FROM (\n" +
            "    SELECT id, title, body FROM forum_node \n" +
            "    WHERE parent_id IS NULL\n" +
            "  ) as questions \n" +
            "  INNER JOIN forum_node_tags ON questions.id=forum_node_tags.node_id\n" +
            "  WHERE tag_id=70\n" +
            ") as questions_by_tag\n" +
            "INNER JOIN (\n" +
            "  SELECT parent_id, GROUP_CONCAT(body) as answer\n" +
            "  FROM forum_node WHERE marked=1 GROUP BY parent_id\n" +
            ") as answers ON questions_by_tag.id=answers.parent_id";


    public static void main(String[] args) throws Exception {
        indexDb();
        //search();
    }

    public static Connection getConnection() throws ClassNotFoundException, IllegalAccessException, InstantiationException, SQLException {
        Class.forName("com.mysql.jdbc.Driver").newInstance();
        return DriverManager.getConnection("jdbc:mysql://localhost/osqa", "osqa", "osqapass");
    }

    public static void indexDb(){
        try{
            long titlesLength = 0, bodyLength = 0, answersLength = 0, docsCount = 0;

            StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_29);
            IndexWriter writer = new IndexWriter(INDEX_DIR, analyzer);

            System.out.println("Indexing to directory '" + INDEX_DIR.getAbsolutePath() + "'...");
            Connection connection = getConnection();
            Statement questionsStatement = connection.createStatement();
            PreparedStatement answerStatement = connection.prepareStatement(answer_sql);
            ResultSet rs = questionsStatement.executeQuery(sql);

            while (rs.next()) {
                answerStatement.setInt(1, rs.getInt("node_id"));
                answerStatement.execute();
                ResultSet resultSet = answerStatement.getResultSet();

                if(!resultSet.next() || !resultSet.getBoolean("marked")) continue;

                String title = rs.getString("title");
                String body = Jsoup.parse(rs.getString("body")).text();
                String answer =  Jsoup.parse(resultSet.getString("answer")).text();

                Document d = new Document();
                d.add(new Field("id", rs.getString("node_id"), Field.Store.YES, Field.Index.NOT_ANALYZED));

                d.add(new Field("title", title, Field.Store.YES, Field.Index.ANALYZED));
                d.add(new Field("body", body, Field.Store.NO, Field.Index.ANALYZED));
                d.add(new Field("answer", answer, Field.Store.NO, Field.Index.ANALYZED));

                titlesLength += title.length();
                bodyLength += body.length();
                answersLength += answer.length();

                docsCount += 1;

                writer.addDocument(d);
                System.out.println(rs.getString("node_id") + " " + title.length() + " " + answer.length());
            }

            String params = "title\n" + Float.toString(titlesLength/(float)docsCount) + "\n" +
                    "body\n" + Float.toString(bodyLength/(float)docsCount) + "\n" +
                    "answer\n" + Float.toString(answersLength/(float)docsCount) + "\n";
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(BM_25_F_PARAMETERS));
            bufferedWriter.write(params);
            bufferedWriter.close();

            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static ArrayList<String> getSyllabus() throws IOException {
        ArrayList<String> result = new ArrayList<String>();
        BufferedReader reader = new BufferedReader(new FileReader("syllabus.txt"));
        String line;
        while((line = reader.readLine()) != null){
            result.add(line);
        }
        return result;
    }

    public static void search() throws IOException {
        try{
            Connection connection = getConnection();
            PreparedStatement selectStatement = connection.prepareStatement("SELECT * FROM forum_node WHERE id=?");

            BM25FSearch bm25FSearch = new BM25FSearch(BM_25_F_PARAMETERS);

            for(String line : getSyllabus()){
                System.out.println("\t" + line);
                long[] docIds = bm25FSearch.getTopN(line, 5);
                for(long id : docIds){
                    selectStatement.setLong(1, id);
                    selectStatement.execute();
                    ResultSet resultSet = selectStatement.getResultSet();
                    if(resultSet.next())
                        System.out.println(id + "\t" + resultSet.getString("title"));
                }
            }
        }catch(Exception e){
            e.printStackTrace();
        }
    }
}
