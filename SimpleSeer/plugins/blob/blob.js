SimpleSeer.inspectionhandlers.blob = {
        rendercontrols: function(insp, div_id) {

            onchange = function(e, ui) {
                params = { 
                    threshval: $("#"+insp.id+"_threshval").slider("value"),
                    invert: $("#"+insp.id+"_invert").is(":checked")
                };
                SS.Inspection.preview("blob", params);
            };
            
            
            onapply = function() {
                insp.norender = false;
                params = { 
                    threshval: $("#"+insp.id+"_threshval").slider("value"),
                    invert: $("#"+insp.id+"_invert").is(":checked")
                };
                
                if (insp.id == "preview") {
                    SS.Inspection.add(insp.method, params);
                } else {
                    insp.parameters = params;
                    SS.Inspection.update(insp);
                }
                
                $("#" + div_id).fadeOut(500).remove();
                SS.resetAction(); 
                
            }
            
            oncancel = function() {
                insp.norender = false;
                SS.Inspection.cancelPreview();
                $("#" + div_id).fadeOut(500).remove();
                SS.resetAction();   
            };
            
            $("#" + div_id).append($("<h2/>").append("Blob Controls"));

            
            $("#" + div_id).append(
                SS.InspectionControl.checkbox(insp.id + "_invert", "invert", "Find Dark Blobs", onchange) 
            ).append(
                SS.InspectionControl.slider(insp.id + "_threshval", "threshval", "Threshold", 127, 0, 255, 1, onchange)
            ).append(
                SS.InspectionControl.applyCancelButton(insp, onapply, oncancel)
            );
        },
        
        render: function () {

            
        },
        render_features: function (features, inspection) {
            if (features.length == 0) {
                return;
            }
            
            if (insp.norender) {
                return;
            }
            
            SS.p.stroke(0);
            for (i in features) {
                f = features[i];
                clr = f.meancolor;
                for (index in clr) {
                    clr[index] = Math.round(clr[index]);
                }
                //alert(JSON.stringify(clr));
                SS.p.stroke(0, 255, 255);
                SS.p.fill(0, 128, 128, 60);
            
                SS.p.beginShape();
                for (c in f.featuredata.mContour) {
                    pt = f.featuredata.mContour[c];
                    SS.p.vertex(pt[0], pt[1]);
                }
                SS.p.endShape();
            
                if (!inspection.id || inspection.id == "preview") {
                    continue;
                }
                div_id = "inspection_" + inspection.id + "_feature_"+i.toString();
                
                if ($("#"+div_id).length) {
                    continue;
                }
                
                SS.Display.addDisplayObject(div_id, f.points[0][0], f.points[0][1], f.width, f.height);
                SS.DisplayObject.addNavZoom(div_id);
                SS.DisplayObject.addNavInfo(div_id, "Blob " + i.toString() + " Properties", {
                    x: { label: "top", units: "px" },
                    y: { label: "left", units: "px"},
                    width: { label: "width", units: "px"},
                    height: { label: "height", units: "px"},
                    angle: { label: "angle", units: "&deg;"},
                    area: { label: "area", units: "px"},
                    meancolor: { label: "color", handler: function(clr) { 
                        clrhex = [];  
                        for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                        return "#" + clrhex.join("");
                        }, units: ""}
                }, inspection, i);
                SS.DisplayObject.addNavItem(div_id, "gear", "Edit this Inspection", function (e) {
                        disp_object_id = $(e.target).parent().parent().parent().attr("id");
                        id = disp_object_id.split("_")[1];
                        feature_index = disp_object_id.split("_")[3];
                        console.log(id);
                        index = SS.Inspection.getIndex(id);
                        insp = SS.inspections[index];
                        feat = SS.featuresets[id][feature_index];
                        console.log(feat);
                        SS.Inspection.control(insp, feat.x, feat.y);
                        insp.norender = true;
                });
            }
            
            
            
            
            
        
        },
        manipulate: function() {
            startx = SS.action['startpx'][0];
            starty = SS.action['startpx'][1];
            
            /*
            xdiff = startx - SS.mouseX;
            ydiff = starty - SS.mouseY;
            
            diff = xdiff * SS.xscalefactor;
            
            thresh = SS.clamp(128 + diff, 1, 254);
            
            SS.Inspection.preview("blob", { threshval: thresh, minsize: 1000 });            
            */
            
            insp = { id: "preview", method: "blob", threshval: 127 };
            SS.Inspection.control(insp, startx, starty);
            
            if (isEmpty(SS.preview_data)) {
                SS.Inspection.preview("blob", { threshval: 127 });            
            }
        },

};