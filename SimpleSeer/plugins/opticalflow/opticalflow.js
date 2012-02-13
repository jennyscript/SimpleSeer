SimpleSeer.inspectionhandlers.opticalflow = {
    
    render: function(insp) {

    },
    
    remove: function(insp) {
        $("#inspection_" + insp.id).remove();
        SS.waitForClick();
    },
    render_features: function(feats, insp) {
      console.log("motion occured");
    },
    
    
    manipulate: function() {
      SS.Inspection.add("opticalflow", {});
      SS.resetAction();
      //SS.waitForClick();
    },
    
    generate_name: function(parameters) {
      return "Motion Detection";    
    },
};

    
console.log("optical flow plugin loaded");
