import bpy


def find_vertex_color_attribute(attributes):
    for attr in attributes:
        #NOTE want float color not byte colour because blender stores byte colours as sRGB.
        #will convert float to byte before saving, because want linear!
        
        #also NOTE that blender supports vert colours on verts and in "loops". Latter
        # is older and apparently what standard obj exporter looks for, but more of a pig to 
        # get (similar to uvs), and baking results don't seem as good, so use the newer
        # and seemingly more sane vertex colours on vertices.
        
        if attr.domain == 'POINT' and attr.name == 'Color':
            return attr
    return None

for obj in bpy.context.selected_objects:
  print("hello world", obj)
  
  if obj and obj.type == 'MESH':
    
    mesh = obj.data
    
    print(len(mesh.attributes))
    
    vert_colors_attr = find_vertex_color_attribute(mesh.attributes)
    
    print(vert_colors_attr.name)
    
    #for vertex in obj.data.vertices: