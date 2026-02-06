#print object info.
#with view to reproducing obj export, then exporting obj2 etc formats directly without running additional script.
#then can extend to bake verts, export >3 channel vert colours, bone weights, anim data, etc.

import bpy


def str_or_empty(input):
  return "" if input is None else str(input+1) #obj indices start from 1!

def print_and_write_to_file(text):
  print(text)
  save_file.write(text + "\n")

save_file = open("C:\\Users\\SuperUser\\Desktop\\test-blender-save-obj.obj", "w")

#obj style header
print_and_write_to_file("# custom obj saver")

for obj in bpy.context.selected_objects:
  print("hello world", obj)
  
  deduped_positions = {}
  unique_positions_arr = []
  
  deduped_normals = {}
  unique_normals_arr = []
  
  vertex_attribute_ids = []
  
  if obj and obj.type == 'MESH':
    for vertex in obj.data.vertices:
        
      print(f"Vertex {vertex.index}: {vertex.co}, normal:{vertex.normal}")
      
      vectuple = tuple(vertex.co)
      if vectuple in deduped_positions:
        #print("already in dict")
        pass
      else:
        deduped_positions[vectuple] = len(unique_positions_arr)
        unique_positions_arr.append(vectuple)
      
      normtuple = tuple(vertex.normal)
      if normtuple in deduped_normals:
        #print("normal already in dict")
        pass
      else:
        deduped_normals[normtuple] = len(unique_normals_arr)
        unique_normals_arr.append(normtuple)
        
      vertex_attribute_ids.append((deduped_positions[vectuple],None,deduped_normals[normtuple]))
        # None for tex coord. (TODO populate)
    
    print(f"num vertices: {len(obj.data.vertices)}")
    print(f"num unique positions: {len(unique_positions_arr)}")
    print(f"num unique normals: {len(unique_normals_arr)}")
    
    
    print_and_write_to_file(f"o {obj.name}")
    
    #print verts obj style
    for posn in unique_positions_arr:
        print_and_write_to_file(f"v {' '.join(map(str,posn))}")
    for norm in unique_normals_arr:
        print_and_write_to_file(f"vn {' '.join(map(str,norm))}")

    
    #Face list that references verts. Not necessarily triangles!
    mesh = obj.data
    for face in mesh.polygons:
        #print(f"Face {face.index}: {face.vertices[:]}")
        #print /obj style with references to positions and normals
        verts_data_strings = []
        for vert_idx in face.vertices:
            attrib_ids = vertex_attribute_ids[vert_idx]
            verts_data_strings.append('/'.join( map(str_or_empty, attrib_ids) ))
        print_and_write_to_file(f"f {' '.join(verts_data_strings)}")
    
    #because uv data might not exist
    if len(mesh.uv_layers)>0:
    
        #check whether it is possible for multiple uv coords (for same layer) to exist on a single vertex. 
        #seems that ordinarily only 1 uv coords val per vertex, but can get more by messing about with 
        #uvs - mark seam, lightmap pack... 
        #TODO create new verts that each have a single uv coord.
        
        deduped_vert_uv_tuples = {}
    
        layer_zero_data = mesh.uv_layers[0].data
        print(f"uv data length: {len(layer_zero_data)}")
        print(f"loops length: {len(mesh.loops)}")
        for loop in mesh.loops:
            uv_loop = layer_zero_data[loop.index]
            #print(f"uv: {uv_loop.uv}, vert: {loop.vertex_index}")
            vert_uv_tuple = (uv_loop.uv[0],uv_loop.uv[1],loop.vertex_index)
            if (vert_uv_tuple not in deduped_vert_uv_tuples):
                deduped_vert_uv_tuples[vert_uv_tuple]=True
        
        print(f"num unique vertex, uv tuples: {len(deduped_vert_uv_tuples)}")
    else:
        print("no uv data!")
     
    #TODO include uv data in output.
    
    
    
save_file.close()