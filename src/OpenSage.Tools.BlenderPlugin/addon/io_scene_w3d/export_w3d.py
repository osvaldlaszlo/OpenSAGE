import bpy

def write(filepath):
    objName = bpy.path.display_name_from_filepath(filepath)
    return {'FINISHED'}

def save(givenfilepath, context, export_settings):
    """Start the w3d export and save to a .w3d file."""
    print('Saving file', givenfilepath)
    return {'FINISHED'}
