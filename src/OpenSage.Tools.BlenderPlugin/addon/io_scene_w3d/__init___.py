bl_info = {
    "name": "Westwood W3D Format (.w3d)",
    "author": "OpenSage Developer Team",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Westwood W3D (.w3d)",
    "description": "Import or Export the Westwood W3D-Format (.w3d)",
    "warning": "Still in Progress",
    "wiki_url": "https://github.com/OpenSAGE/OpenSAGE",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_w3d" in locals():
        importlib.reload(import_w3d)
    if "export_w3d" in locals():
        importlib.reload(export_w3d)
else:
    import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import (CollectionProperty,
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       IntProperty)


class ImportW3D(bpy.types.Operator):
    bl_idname = "import_mesh.westwood_w3d"
    bl_label = "Import W3D"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.w3d", options={'HIDDEN'})

    def execute(self, context):
        from . import import_w3d
        import_w3d.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ExportW3D(bpy.types.Operator):
    bl_idname = 'export_mesh.westwood_w3d'
    bl_label = 'Export W3D'
    bl_options = {'UNDO', 'PRESET'}

    filepath = StringProperty(subtype='FILE_PATH')
    filename_ext = ".w3d"
    filter_glob = StringProperty(default='*.w3d', options={'HIDDEN'})

    ui_tab = EnumProperty(
            items=(('GENERAL', "General", "General settings"),
                #('MESHES', "Meshes", "Mesh settings"),
                #('OBJECTS', "Objects", "Object settings"),
                #('MATERIALS', "Materials", "Material settings"),
                ('ANIMATION', "Animation", "Animation settings")),
            name="ui_tab",
            description="Export setting categories",
    )    

    export_mode = EnumProperty(
            name="Export Mode",
             items=(('M', "Model", "This will export all the meshes of the scene, without skeletons or animation"), 
                ('S', "Skeleton", "This will export the hierarchy tree without any geometry or animation data"), 
                ('A', "Animation", "This will export the animation without any geometry data or skeletons"), 
                ('HAM', "HierarchicalAnimatedModel", "This will export the meshes with the hierarchy and animation into one file")
                ),          
            default='M',)   

    export_compress = EnumProperty(
            name="Compression",
             items=(('U', "Uncompressed", "This will not compress the animations"), 
                ('TC', "TimeCoded", "This will export the animation with keyframes"), 
                ('AD', "AdaptiveDelta", "This will use adaptive delta compression to reduce size"), 
                ),          
            default='TC',)

    will_save_settings = BoolProperty(default=False)

    # Custom scene property for saving settings
    scene_key = "w3dExportSettings"


    def execute(self, context):
        from . import export_w3d

        if self.will_save_settings:
            self.save_settings(context)

        # All custom export settings are stored in this container.
        export_settings = {}

        export_settings['w3d_mode'] = export_mode
        export_settings['w3d_compression'] = animation_compression

        export_w3d.save(self.filepath, context, export_settings)
        return {'FINISHED'}

    def save_settings(self, context):
        # find all export_ props
        all_props = self.properties
        export_props = {x: getattr(self, x) for x in dir(all_props)
                        if x.startswith("export_") and all_props.get(x) is not None}

        context.scene[self.scene_key] = export_props

    def invoke(self, context, event):
        settings = context.scene.get(self.scene_key)
        self.will_save_settings = False
        if settings:
            try:
                for (k, v) in settings.items():
                    setattr(self, k, v)
                self.will_save_settings = True

            except (AttributeError, TypeError):
                self.report({"ERROR"}, "Loading export settings failed. Removed corrupted settings")
                del context.scene[self.scene_key]

        ExportHelper.invoke(self, context, event)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.prop(self, 'ui_tab', expand=True)
        if self.ui_tab == 'GENERAL':
            self.draw_general_settings()
        elif self.ui_tab == 'ANIMATION':
            self.draw_animation_settings()

    def draw_general_settings(self):
        col = self.layout.box().column()
        col.prop(self, 'export_mode')

    def draw_animation_settings(self):
        col = self.layout.box().column()
        col.prop(self, 'export_compress')



def menu_import(self, context):
    self.layout.operator(ImportW3D.bl_idname, text="Westwood W3D (.w3d)")

def menu_export(self, context):
    self.layout.operator(ExportW3D.bl_idname, text='Westwood W3D (.w3d)')


def register():
    bpy.utils.register_class(ImportW3D)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    bpy.utils.register_class(ExportW3D)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)

def unregister():
    bpy.utils.unregister_class(ImportW3D)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(ExportW3D)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
