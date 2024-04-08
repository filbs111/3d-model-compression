
var fs = require('fs');
//load in object.

convertFile("buildings");
convertFile("chessb");
/*
convertFile("extruded-thing");
convertFile("menger");
convertFile("menger-edgesplit");
convertFile("mesh-sphere");
convertFile("monkeyhead");
*/
//convertFile("frigate");
//convertFile("pillar");
//convertFile("sship-pointyc-tidy1-uv3-2020b-cockpit1b-yz-2020-10-04");

//convertFile("subdiv-cube-flat");
//convertFile("subdiv-cube-smooth");

var loaderOptionSets = {
	obj1:{
		extension: "obj1",
		hasVertColors: true,
		useVertexAttributes: false,
	},
	obj2:{
		extension: "obj2",
		hasVertColors: false,
		useVertexAttributes: true,
		differenceIndices: false
	},
	obj3:{
		extension: "obj3",
		hasVertColors: true,
		useVertexAttributes: true,
		differenceIndices: false
	},
	obj5:{
		extension: "obj5",
		hasVertColors: true,
		useVertexAttributes: true,
		differenceIndices: true
	}
}

function convertFile(filename){
	fs.readFile('./objs/' + filename + '.obj', {encoding: 'utf-8'}, function (err, data) {
		//console.log(err);
		//console.log(data);
		//var stringdata = data.toString();
	  loadObjFile(data, filename, loaderOptionSets.obj1);
	  loadObjFile(data, filename, loaderOptionSets.obj2);	//2,3 are pointless/undesirable if object lacks vertex colours
	  loadObjFile(data, filename, loaderOptionSets.obj3);
	  loadObjFile(data, filename, loaderOptionSets.obj5);	//obj3 but with indices stored as differences
	}); 
}


//adapted from obj loader code from game project.
function loadObjFile(response, filename, loaderOptions){
	var {extension, hasVertColors, useVertexAttributes, differenceIndices} = loaderOptions;
	
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


	var vRefsTranslate = x=>x;

	//write out the new file.
	//apart from the faces, initial part is reproduced, though with current method, without anything other than expected flags...
	var toWrite = "";
		
	var vIdxTranslate = (x => x);
	
	if (hasVertColors){
		var usedPositions={};
		var usedColours={};
		var positionsArr = [];
		var coloursArr = [];
		var posCount=0;
		var coloursCount=0;
		var vertPosRefs = [];	//for models that have vertex colours
		var vertColorRefs = [];
		
		for (var vstring of vertstrings){
			var components = vstring.split(" ");
			var positionpart = components.slice(1,4).join(" ");
			var colourpart = components.slice(4).join(" ");
			var posIdx = usedPositions[positionpart];
			var colourIdx = usedColours[colourpart];
			if (posIdx == undefined){
				usedPositions[positionpart]=posCount;
				posIdx=posCount;
				posCount++;	//this same as positionsArr.length
				positionsArr.push(positionpart);
			}
			if (colourIdx == undefined){
				usedColours[colourpart]=coloursCount;
				colourIdx=coloursCount;
				coloursCount++;
				coloursArr.push(colourpart);
			}
			vertPosRefs.push(posIdx);
			vertColorRefs.push(colourIdx);
		}
		toWrite+= positionsArr.map(x=>"vp " + x + "\n").join("");
		toWrite+= coloursArr.map(x=>"vc " + x + "\n").join("");
		//TODO include references for both in face or attribute data.
		
		vRefsTranslate = ( indices=> {
			var parts = indices.split("/");
			var vidx = parts[0] - 1;	//-1 because obj numbers start at 1!
			
			parts[0] = vertPosRefs[vidx] + 1;	//+1 because obj numbers start at 1!
			if (hasVertColors){
				parts.push(vertColorRefs[vidx] + 1);
			}
			return parts.join("/");
		});
				
	} else {
		toWrite+= vertstrings.join("\n");	//regular vertices
		toWrite+= "\n";
	}
	
	toWrite+= vtstrings.map(x=>x+"\n").join("");
	toWrite+= vnstrings.map(x=>x+"\n").join("");
	

	console.log({vertstrings, vtstrings, vnstrings, faces});


	if (useVertexAttributes){

		for (var face of faces){
			var theseVerts = [];
			for (var vertInFace of face){
				
				vertInFace = vRefsTranslate(vertInFace);	//does nothing when no vertex colours.
				
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
	
		//write out attributes
		toWrite+= newVertStrings.map(v=> "a " + v + "\n").join("");
	}else{
		for (var face of faces){
			var theseVerts = [];
			for (var vertInFace of face){
				vertInFace = vRefsTranslate(vertInFace);	//does nothing when no vertex colours.
				theseVerts.push(vertInFace);
			}
			newFaces.push(theseVerts);
		}
	}
	

	if (differenceIndices){
		//in order to store smaller numbers than indices (which can be ~5 digit numbers for 16 bit indices),
		// store differences.

		//NOTE sorting attributes may make for smaller differences, but seems like standard process
		// results in reasonable ordering anyway.

		//sort faces so can store with +ve derivatives.
		//each face is stored with 1st index relative to 1st index of previous face,
		// and 2nd, 3rd indices stored as difference from 1st index of current face.
		//might improve perf by wrapping, but avoid for now. (will help if 2 large indices, one small,
		//, and with small and very large > 2^15 index)
		//first cycle each face's verts (retaining winding order)

		//then sort by 1st face index.

		var sortedFaces = newFaces
		.map( f => {
			if (f[0]<=f[1]){
				if (f[0]<=f[2]){
					return f;
				}
			}else{
				if (f[1]<=f[2]){
					return [f[1],f[2],f[0]];
				}
			}
			return [f[2],f[0],f[1]];
		})
		.sort((a, b) => {
			var a_minus_b = a[0]-b[0];
			if (a_minus_b < 0){
				return -1;
			}else if (a_minus_b>0){
				return 1;
			}
			return 0;
		});
		
		//store differences.
		var currentFirstIndex = 0 ;
		var differenceFaces=sortedFaces.map(f=>{
			var firstIdx = f[0];
			var lastFirstIdx = currentFirstIndex;
			currentFirstIndex = firstIdx;
			return [currentFirstIndex - lastFirstIdx, f[1]-currentFirstIndex, f[2]-currentFirstIndex];
		});

		toWrite+= differenceFaces.map(f=> "f " + f.join(" ") + "\n").join("");

	} else {

		toWrite+= newFaces.map(f=> "f " + f.join(" ") + "\n").join("");
	}

	
	fs.writeFile('./'+extension+'/' + filename+ '.'+extension, toWrite, function(err) {
    if(err) {
        return console.log(err);
    }
    console.log("The file was saved!");
}); 

}




//save files in other formats

//create loader for those files, check outputs same as existing loader


//to create new file, could work back from 