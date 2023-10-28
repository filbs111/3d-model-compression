
var fs = require('fs');
//load in object.

//var filename = "buildings";
//var filename = "chessb";

//convertFile("extruded-thing");
//convertFile("menger");
//convertFile("menger-edgesplit");
//convertFile("mesh-sphere");
//convertFile("monkeyhead");

//convertFile("frigate");
//convertFile("pillar");
//convertFile("sship-pointyc-tidy1-uv3-2020b-cockpit1b-yz-2020-10-04");

convertFile("subdiv-cube-flat");
convertFile("subdiv-cube-smooth");

function convertFile(filename){
	fs.readFile('./objs/' + filename + '.obj', {encoding: 'utf-8'}, function (err, data) {
		//console.log(err);
		//console.log(data);
		//var stringdata = data.toString();
	  loadObjFile(data, filename);
	}); 
}


//adapted from obj loader code from game project.
function loadObjFile(response, filename){
    console.log(response);
    var lines = response.split("\n");
    console.log(lines.length);

	var vertstrings = [];
	var vtstrings = [];
	var vnstrings = [];
    var faces = [];

    for (var ll = 0; ll<lines.length ; ll++){
        var thisLine = lines[ll];
        var splitLine = thisLine.split(" ");
        var firstPart = splitLine[0];
		
        var floatArr = splitLine.slice(1).map((x)=>{return parseFloat(x)});
        //var floatArr = splitLine.slice(1);

        if (firstPart == 'v'){
            vertstrings.push(thisLine);
        }
        if (firstPart == 'vt'){
            vtstrings.push(thisLine);
        }
        if (firstPart == 'vn'){
            vnstrings.push(thisLine);
        }
        if (firstPart == 'f'){
            faces.push(splitLine.slice(1));
        }
    }
    //face data in obj lists indices for position, uv, normals independently.
    //can change file format to describe "whole" vertices by referencing these independent parts, then describe faces referencing the "whole" vertices,
    //but for now just work with regular obj data. this maybe slower, and in some cases file size larger. 
    var vertsCount=0;
    var usedVerts={};
    var newVerts = [];
	var newVertStrings = [];
	
    var newFaces = [];

	//var vertPosAndColorRefs = [];	//for models that have vertex colours

    for (var face of faces){
        var theseVerts = [];
        for (var vertInFace of face){
            var lookedupVertId = usedVerts[vertInFace];
            if (lookedupVertId != undefined){
                theseVerts.push(lookedupVertId);
            }else{
                //newVerts.push(vertInFace.split("/").map(x=>x-1));  //notice subtracting 1 because obj starts counting from 1. FWIW, ends up with -1s in place of emptystrings!
				newVertStrings.push(vertInFace);
				
                theseVerts.push(vertsCount);
                usedVerts[vertInFace] = vertsCount;
                vertsCount++;
            }
        }
        newFaces.push(theseVerts);
    }
	
	
	console.log({vertstrings, vtstrings, vnstrings, faces});
	
	//write out the new file.
	//apart from the faces, initial part is reproduced, though with current method, without anything other than expected flags...
	
	var toWrite = "";
	toWrite+= vertstrings.join("\n");
	toWrite+= "\n";
	toWrite+= vtstrings.join("\n");
	toWrite+= "\n";
	toWrite+= vnstrings.join("\n");
	toWrite+= "\n";
	
	//write out attributes
	var attributeStrings=[];
	for (var vert of newVertStrings){
		attributeStrings.push("a " + vert);
	}
	toWrite+= attributeStrings.join("\n");
	toWrite+= "\n";

	var faceStrings=[];
	//write out faces referencing the vertex indices (note this is zero indexed, different to how other stuff is in obj
	for (var face of newFaces){
		faceStrings.push("f " + face.join(" "));
	}
	toWrite+= faceStrings.join("\n");
	toWrite+= "\n";
	

	
	fs.writeFile('./obj2/' + filename+ '.obj2', toWrite, function(err) {
    if(err) {
        return console.log(err);
    }
    console.log("The file was saved!");
}); 

}




//save files in other formats

//create loader for those files, check outputs same as existing loader


//to create new file, could work back from 