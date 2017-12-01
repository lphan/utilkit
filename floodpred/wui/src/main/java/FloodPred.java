
public class FloodPred {
    private int id;
    private String datetime;
    private int waterlevel_now;
    private int start_time;
    private int predict_hours;
    private String figure_name;
    private float predict_result;
    private float artificial_result;

    public FloodPred(){}

    public FloodPred(int id, String datetime, int waterlevel_now, int start_time, int predict_hours,
                     String figure_name, float predict_result, float artificial_result) {
        this.id = id;
        this.datetime = datetime;
        this.waterlevel_now = waterlevel_now;
        this.start_time = start_time;
        this.predict_hours = predict_hours;
        this.figure_name = figure_name;
        this.predict_result = predict_result;
        this.artificial_result = artificial_result;
    }

    public int getId() { return id;}
    public void setId(int id) { this.id = id;}

    public String getDateTime(){return datetime;}
    public void setDatetime(String datetime) { this.datetime = datetime;}

    public int getWaterLevel() {return waterlevel_now;}
    public void setWaterLevel(int waterlevel_now) { this.waterlevel_now = waterlevel_now;}

    public int getStart_time() { return start_time;}
    public void setStart_time(int start_time) {this.start_time = start_time;}

    public int getPredictHours() { return predict_hours;}
    public void setPredictHours(int predict_hours){this.predict_hours= predict_hours;}

    public String getFigure_name(){return figure_name;}
    public void setFigure_name(String image_path) { this.figure_name = image_path;}

    public float getPredict_result(){return predict_result;}
    public void setPredict_result(float predict_result){this.predict_result = predict_result;}

    public float getArtificial_result(){return artificial_result;}
    public void setArtificial_result(float artificial_result){this.artificial_result = artificial_result;}

}
