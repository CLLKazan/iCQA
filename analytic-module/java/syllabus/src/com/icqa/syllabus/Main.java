package com.icqa.syllabus;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.IntField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;

import java.io.*;
import java.sql.*;


public class Main {

    public static SimpleFSDirectory INDEX_DIR;

    public static void main(String[] args) throws Exception {

        INDEX_DIR = new SimpleFSDirectory(new File("index"));
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));
        String line = in.readLine();

        if(line.equals("index")) {
            indexDb();
        }
        else if(line.equals("search")){
            search(new File("syllabus.txt"));
        }
    }

    public static Connection getConnection() throws ClassNotFoundException, IllegalAccessException, InstantiationException, SQLException {
        Class.forName("com.mysql.jdbc.Driver").newInstance();
        return DriverManager.getConnection("jdbc:mysql://localhost/osqa", "osqa", "osqapass");
    }

    public static void indexDb(){
        try{
            StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_41);
            IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_41, analyzer);
            config.setSimilarity(new BM25Similarity());
            config.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
            IndexWriter writer = new IndexWriter(INDEX_DIR, config);

            System.out.println("Indexing to directory '" + INDEX_DIR.getDirectory().getPath() + "'...");
            String sql = "SELECT id, title, body FROM forum_node WHERE parent_id is NULL";
            Statement stmt = getConnection().createStatement();
            ResultSet rs = stmt.executeQuery(sql);
            while (rs.next()) {
                Document d = new Document();
                d.add(new IntField("id", rs.getInt("id"), Field.Store.YES));
                d.add(new TextField("title", rs.getString("title"), Field.Store.YES));
                d.add(new TextField("body", rs.getString("body"), Field.Store.NO));
                writer.addDocument(d);
            }

            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void search(File queries) throws IOException {
        try{
            IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(INDEX_DIR));

            StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_41);
            QueryParser queryParser = new QueryParser(Version.LUCENE_41, "title", analyzer);

            BufferedReader reader = new BufferedReader(new FileReader(queries));
            String line;
            while((line = reader.readLine()) != null){
                Query query = queryParser.parse(line);
                TopDocs topDocs = searcher.search(query, 10);

                System.out.println("Found " + topDocs.totalHits + " results for '" + line + "'");
                ScoreDoc[] hits = topDocs.scoreDocs;
                for (int i = 0; i < hits.length; i++){
                    Document doc = searcher.doc(hits[i].doc);
                    String title = doc.get("title");
                    System.out.println((i + 1) + ": " + hits[i].score + "\t\t" + doc.get("id") + "\t\t" + title);
                }
            }
        }catch(Exception e){
            e.printStackTrace();
        }
    }
}
