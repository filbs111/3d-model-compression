#save obj.
#with view to reproducing obj export, then exporting obj2 etc formats directly without running additional script.
#then can extend to bake verts, export >3 channel vert colours, bone weights, anim data, etc.

#currently differs from standard blender obj export. suspect that selecting flat shading for object causes
#faceted output, and position/orientation can be different - application of object pose? swizzling?

import bpy
import time


def str_or_empty(input):
  return "" if input is None else str(input+1) #obj indices start from 1!

def limited_float_str(input):
  return "{:.3f}".format(input)
#TODO apply this truncation BEFORE deduplication of coords - especially may debloat normals

def print_and_write_to_file(file_to_write, text):
  #print(text)
  file_to_write.write(text + "\n")

save_file = open("C:\\Users\\SuperUser\\Desktop\\test-blender-save-obj.obj", "w")
save_file2 = open("C:\\Users\\SuperUser\\Desktop\\test-blender-save-obj.obj2", "w")
    

t0 = time.perf_counter()


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
    
    
    deduped_uvs = {}
    unique_uvs_arr = []
    
    #Face list that references verts. Not necessarily triangles!
    mesh = obj.data
    
    deduped_attr_strings = {}
    unique_attr_strings_arr = []
    
    face_output_arr = []
    
    #because uv data might not exist
    if len(mesh.uv_layers)==0:
        print("no uv data!")
        
        for face in mesh.polygons:
            #print(f"Face {face.index}: {face.vertices[:]}")
            #print /obj style with references to positions and normals
            attr_string_refs_for_face = []
            for vert_idx in face.vertices:
                attrib_ids = vertex_attribute_ids[vert_idx]
                verts_data_string = '/'.join( map(str_or_empty, attrib_ids) )
                if verts_data_string in deduped_attr_strings:
                    pass
                else:
                    deduped_attr_strings[verts_data_string]=len(unique_attr_strings_arr)
                    unique_attr_strings_arr.append(verts_data_string)
                attr_string_refs_for_face.append(deduped_attr_strings[verts_data_string])
                
            face_output_arr.append(attr_string_refs_for_face)
    else:
    
        
    
        uv_layer_data = mesh.uv_layers[0].data  #use mesh.uv_layers.active.data ?
    
        for face in mesh.polygons:
            corner_count = len(face.vertices)
            face_uvs = [uv_layer_data[li] for li in face.loop_indices]
        
            attr_string_refs_for_face = []
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
                verts_data_string = '/'.join( map(str_or_empty, new_attrib_ids) )
                if verts_data_string in deduped_attr_strings:
                    pass
                else:
                    deduped_attr_strings[verts_data_string]=len(unique_attr_strings_arr)
                    unique_attr_strings_arr.append(verts_data_string)
                attr_string_refs_for_face.append(deduped_attr_strings[verts_data_string])
                
            face_output_arr.append(attr_string_refs_for_face)
            
            
        print(len(unique_uvs_arr))
    
    
    #write standard obj
    
    print_and_write_to_file(save_file, "# custom obj saver")
    print_and_write_to_file(save_file, f"o {obj.name}")
    
    #print verts obj style
    for posn in unique_positions_arr:
        print_and_write_to_file(save_file, f"v {' '.join(map(limited_float_str,posn))}")
    for norm in unique_normals_arr:
        print_and_write_to_file(save_file, f"vn {' '.join(map(limited_float_str,norm))}")
    for uv in unique_uvs_arr:
        print_and_write_to_file(save_file, f"vt {' '.join(map(limited_float_str,uv))}")
    
    for verts_data_string_refs in face_output_arr:
        verts_data_strings = [ unique_attr_strings_arr[ref] for ref in verts_data_string_refs]
        print_and_write_to_file(save_file, f"f {' '.join(verts_data_strings)}")
    
    #write modified obj which lists vertices referencing all attributes then faces referencing vertices, 
    # rather than faces directly referencing individual attributes. reduces file size for smooth polys,
    # , easier to load into game (because vertices containing all attributes good fit for gl / gpu)
    
    print_and_write_to_file(save_file2, "# custom obj saver")
    print_and_write_to_file(save_file2, f"o {obj.name}")
    
    #print verts obj style (same as standard obj)
    for posn in unique_positions_arr:
        print_and_write_to_file(save_file2, f"v {' '.join(map(limited_float_str,posn))}")
    for norm in unique_normals_arr:
        print_and_write_to_file(save_file2, f"vn {' '.join(map(limited_float_str,norm))}")
    for uv in unique_uvs_arr:
        print_and_write_to_file(save_file2, f"vt {' '.join(map(limited_float_str,uv))}")
    
    for verts_data_string in unique_attr_strings_arr:
        print_and_write_to_file(save_file2, f"a {verts_data_string}")
    
    # faces reference vertex attributes by id
    for verts_data_string_refs in face_output_arr:
        print_and_write_to_file(save_file2, f"f {' '.join(map(str, verts_data_string_refs))}")
    
    
    print(len(unique_uvs_arr))
    
    
save_file.close()
save_file2.close()

t1 = time.perf_counter()
print(f"time taken: {int((t1-t0)*1000)} ms")