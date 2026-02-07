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
        
      #print(f"Vertex {vertex.index}: {vertex.co}, normal:{vertex.normal}")
      
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
    
    face_output_arr = [] #collect face list and print after know uvs etc. however, could interleave
                        #and just print faces as go along in obj file, but nice to have f lines all at end.
    
    #because uv data might not exist
    if len(mesh.uv_layers)==0:
        print("no uv data!")
        
        for face in mesh.polygons:
            #print(f"Face {face.index}: {face.vertices[:]}")
            #print /obj style with references to positions and normals
            verts_data_strings = []
            for vert_idx in face.vertices:
                attrib_ids = vertex_attribute_ids[vert_idx]
                verts_data_strings.append('/'.join( map(str_or_empty, attrib_ids) ))
            face_output_arr.append(verts_data_strings)
            
    else:
    
        #TODO use this when want to specify verts with all attributes and reference these 
        # verts for faces. however, don't need this for standard obj export.
        #deduped_vert_with_uv = {}
        #unique_vert_with_uv_arr = []
        
        deduped_uvs = {}
        unique_uvs_arr = []
    
        uv_layer_data = mesh.uv_layers[0].data  #use mesh.uv_layers.active.data ?
    
        for face in mesh.polygons:
            corner_count = len(face.vertices)
            face_uvs = [uv_layer_data[li] for li in face.loop_indices]
        
            verts_data_strings = []
            for ii in range(corner_count):
                vert_idx = face.vertices[ii]
                attrib_ids = vertex_attribute_ids[vert_idx]
                print(ii)
                print(face_uvs)
                uv = face_uvs[ii]
                print(uv)
                uvtuple = tuple(uv.uv)
                if uvtuple in deduped_uvs:
                  #print("already in dict")
                  pass
                else:
                  deduped_uvs[uvtuple] = len(unique_uvs_arr)
                  unique_uvs_arr.append(uvtuple)
                
                new_attrib_ids = [attrib_ids[0], deduped_uvs[uvtuple], attrib_ids[2]]
                verts_data_strings.append('/'.join( map(str_or_empty, new_attrib_ids) ))
            
            face_output_arr.append(verts_data_strings)
            
        print(len(unique_uvs_arr))
    
    for verts_data_strings in face_output_arr:
        print_and_write_to_file(f"f {' '.join(verts_data_strings)}")
    
save_file.close()