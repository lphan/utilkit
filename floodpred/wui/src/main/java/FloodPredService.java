
import javax.annotation.PostConstruct;
import javax.ejb.EJB;
import javax.enterprise.context.SessionScoped;
import javax.inject.Named;
import javax.json.JsonObject;
import java.io.Serializable;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

@Named("floodpredService")
@SessionScoped
public class FloodPredService implements Serializable{

    private FloodPred fp = new FloodPred();
    private String query = "";

    @EJB
    private  FloodPredDB floodPredDB;
    private List<FloodPred> dat = new ArrayList<>();

    private JsonObject datafp;

    public FloodPredService(){}

    @PostConstruct
    private void init() { query(); }

    public void create() {
        floodPredDB.create(fp);
        query();
    }

    public void query() {
        dat = floodPredDB.retrieve(query);
    }

    public void delete() throws UnknownHostException {
        floodPredDB.delete(fp);
        query();
    }

    public void compute() {
        getObjToDB().create(fp);
    }

    public void displayvisual(){
        fp.getFigure_name();
        // call function to display it
    }

    public FloodPred getFloodPred() {
        return fp;
    }
    public void setFloodPred(FloodPred fp) {
        this.fp = fp;
    }

    /*
    private FloodPredDB getObjFromDatabase() {
        return floodPredDB;
    } */

    public FloodPredDB getObjToDB(){
        return floodPredDB;
    }
    public void setObjToDB(FloodPredDB floodPredDB) {
        this.floodPredDB = floodPredDB;
    }

    public String getQuery() {
        return query;
    }
    public void setQuery(String query){
        this.query = query;
    }

    public List<FloodPred> getObjFloodPred(){
        return dat;
    }
    public void setListFloodPred(List<FloodPred> list) {
        this.dat = list;
    }
}
