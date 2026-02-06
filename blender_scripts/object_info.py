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
        
save_file.close()