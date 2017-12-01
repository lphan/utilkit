
import com.google.gson.Gson;
// import com.mongodb.BasicDBObject;
import com.mongodb.*;
// import com.mongodb.DBCollection;
// import com.mongodb.DBObject;
// import com.mongodb.client.FindIterable;
// import com.mongodb.client.MongoCollection;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
// import com.mongodb.util.JSON;
// import org.bson.Document;

import javax.ejb.Stateless;
// import javax.json.Json;
// import javax.json.JsonObjectBuilder;
import java.io.FileWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.net.UnknownHostException;
// import java.util.List;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.logging.Logger;

import org.bson.BsonDocument;
import org.bson.BsonRegularExpression;
import org.bson.Document;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

@Stateless
public class FloodPredDB {

    private static final Logger LOGGER = Logger.getLogger(FloodPredDB.class.getName());
    private final static String HOST = "localhost";
    private final static int PORT = 27017;

    private final static String DATABASE = "floodpred";
    private final static String COLLECTION = "floodpred";

    private Mongo mongoClient() {
        return new MongoClient(new ServerAddress(HOST, PORT));
    }

    /*
    CRUD Implementation
     */
    public void create(FloodPred fp) {
        System.out.println("Create New Computing Object");

        if (fp != null){
            int waterlevel_now = fp.getWaterLevel();
            int start_time = fp.getStart_time();
            int predict_hours = fp.getPredictHours();

            JSONObject obj = new JSONObject();
            obj.put("waterlevel_now", waterlevel_now);
            obj.put("start_time", start_time);
            obj.put("predict_hours", predict_hours);

            // Create Json-Object and assign it as file javparams.json to Python-function
            // pyobj = {'start_time': starttime, 'waterlevel_now': waterlevel, 'predict_hours': predictHours};
            try {
                FileWriter fileout = new FileWriter("javparam.json");
                fileout.write(obj.toJSONString());
                fileout.flush();

            } catch (Exception e) {
                e.printStackTrace();
            }
            // System.out.println("Call Python code to compute new result"); -> JYTHON does not support Python3
            // System.out.println("Need to use Flask")
            // System.out.println("and synchronize new result from CSV-file to Database using Python");
        }
    }

    public List< FloodPred> retrieve(String query) {
        final List< FloodPred> list = new ArrayList<>();
        MongoClient mongoClient = new MongoClient(new ServerAddress(HOST, PORT));
        MongoCollection<Document> collection = mongoClient.getDatabase(DATABASE).getCollection(COLLECTION);

        FindIterable<Document> iter;

        if (query == null || query.trim().length() == 0) {
            iter = collection.find();
        } else {
            BsonRegularExpression bsonRegex = new BsonRegularExpression(query);
            BsonDocument bsonDoc = new BsonDocument();
            bsonDoc.put("water_level", bsonRegex);
            iter = collection.find(bsonDoc);
        }

        iter.forEach(new Block<Document>() {
            @Override
            public void apply(Document doc) {
                list.add(new Gson().fromJson(doc.toJson(),  FloodPred.class));
            }
        });
        return list;

        // if (query.equals("all")) {
        //     DBCollection collection = mongoClient().getDB(DATABASE).getCollection(COLLECTION);
        //     DBCursor cursor = collection.find();
        //     // Retrieve all documents
        //     while (cursor.hasNext()) {
        //         System.out.println(cursor.next());
        //     }
        //     DBObject result = cursor.next();
        //     // MongoCollection<Document> colls = collection;
        //     // FindIterable<Document> searchresult = collection.find();
        //     return (JsonObject) result;
        // } else {
        //     return null;
        // }
    }

    public void update( FloodPred fp) {
        MongoClient mongoClient = new MongoClient(new ServerAddress(HOST, PORT));
        MongoCollection<Document> collection = mongoClient.getDatabase(DATABASE).getCollection(COLLECTION);
        // Document d = new Document();
        System.out.println("Continue update database");
    }

    public void delete( FloodPred fp) {
        MongoClient mongoClient = new MongoClient((new ServerAddress(HOST, PORT)));
        MongoCollection<Document> collection = mongoClient.getDatabase((DATABASE)).getCollection(COLLECTION);
        collection.deleteOne(new Document("id", fp.getId()));
    }

    /*
    These following functions are used for testing purpose
     */
    public Set<String> getCollectionNames() throws UnknownHostException {
        DB db = mongoClient().getDB("floodpred");
        Set<String> colls = db.getCollectionNames();

        for (String s: colls) {
            System.out.println(s);
        }

        return colls;
    }
}

