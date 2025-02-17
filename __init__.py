bl_info = {
    "name": "Animation Presets Pro",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Animation",
    "description": "Animation presets with real-time controls",
    "category": "Animation"
}

import bpy
from operators import *
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import FloatProperty, EnumProperty, PointerProperty, BoolProperty, StringProperty
from bpy.utils import previews
import os

# Global preview collection
preview_collections = {}

def get_addon_name():
    return os.path.basename(os.path.dirname(__file__))

def get_presets_path():
    addon_path = os.path.dirname(os.path.realpath(__file__))
    presets_path = os.path.join(addon_path, "presets")
    if not os.path.exists(presets_path):
        os.makedirs(presets_path)
    return presets_path

def get_preset_items(self, context):
    enum_items = []
    
    if context is None:
        return enum_items
    
    pcoll = preview_collections.get("main")
    if not pcoll:
        pcoll = previews.new()
        preview_collections["main"] = pcoll
    
    # Clear existing previews
    pcoll.clear()
    
    # Load previews from presets directory
    presets_path = get_presets_path()
    index = 1
    
    if os.path.exists(presets_path):
        for filename in sorted(os.listdir(presets_path)):
            if filename.lower().endswith((".gif", ".png", ".jpg")):
                filepath = os.path.join(presets_path, filename)
                
                try:
                    thumb = pcoll.load(filename, filepath, 'IMAGE')
                    enum_items.append((
                        os.path.splitext(filename)[0].upper(),
                        os.path.splitext(filename)[0].replace('_', ' ').title(),
                        f"Apply {filename} animation preset",
                        thumb.icon_id,
                        index
                    ))
                    index += 1
                except Exception as e:
                    print(f"Error loading preview for {filename}: {e}")
    
    return enum_items

# Function to apply popup rotation animation
def apply_popup_rotation(obj):
    # Create new animation data if it doesn't exist
    if not obj.animation_data:
        obj.animation_data_create()
    
    # Create a new action if it doesn't exist
    action = bpy.data.actions.new(name="PopupRotation")
    obj.animation_data.action = action
    
    # Create rotation keyframes
    rot_fcurves = []
    for i in range(3):  # X, Y, Z rotation
        fc = action.fcurves.new(data_path="rotation_euler", index=i)
        rot_fcurves.append(fc)
    
    # Set keyframes for popup rotation
    frame_start = 1
    frame_end = 24
    
    # Initial position
    for i, fc in enumerate(rot_fcurves):
        kf = fc.keyframe_points.insert(frame_start, 0)
        kf.interpolation = 'BOUNCE'
    
    # Rotation
    rot_fcurves[2].keyframe_points.insert(frame_end, 6.28319)  # 360 degrees in radians
    
    # Set nice easing
    for fc in rot_fcurves:
        for kf in fc.keyframe_points:
            kf.easing = 'EASE_OUT'
            kf.handle_left_type = 'AUTO_CLAMPED'
            kf.handle_right_type = 'AUTO_CLAMPED'

class AnimationPresetProperties(PropertyGroup):
    animation_speed: FloatProperty(
        name="Speed",
        description="Animation speed multiplier",
        default=1000.0,
        min=100.0,
        max=2000.0,
        update=lambda self, context: update_animation_timing(self, context)
    )
    
    preset_enum: EnumProperty(
        items=get_preset_items,
        name="Presets",
        description="Animation presets"
    )

def update_animation_timing(self, context):
    if not context.selected_objects:
        return
        
    for obj in context.selected_objects:
        if obj.animation_data and obj.animation_data.action:
            speed = self.animation_speed / 1000.0  # Convert to reasonable range
            action = obj.animation_data.action
            
            # Store original keyframe times if not already stored
            if not hasattr(action, "original_keyframes"):
                action.original_keyframes = {}
                for fc in action.fcurves:
                    action.original_keyframes[fc.data_path] = [
                        (kf.co.x, kf.handle_left.x, kf.handle_right.x)
                        for kf in fc.keyframe_points
                    ]
            
            # Update keyframes based on speed
            for fc in action.fcurves:
                if fc.data_path in action.original_keyframes:
                    for kf, orig in zip(fc.keyframe_points, action.original_keyframes[fc.data_path]):
                        kf.co.x = orig[0] * speed
                        kf.handle_left.x = orig[1] * speed
                        kf.handle_right.x = orig[2] * speed
            
            # Update scene frame range
            if action.frame_range:
                context.scene.frame_start = int(action.frame_range[0] * speed)
                context.scene.frame_end = int(action.frame_range[1] * speed)

class ANIM_OT_play_animation(Operator):
    bl_idname = "anim.play_animation"
    bl_label = "Play Animation"
    bl_description = "Play the animation in the viewport"
    
    def execute(self, context):
        if not context.screen.is_animation_playing:
            context.scene.frame_current = context.scene.frame_start
            bpy.ops.screen.animation_play()
        return {'FINISHED'}

class ANIM_OT_reset_animation(Operator):
    bl_idname = "anim.reset_animation"
    bl_label = "Reset Animation"
    bl_description = "Reset animation to start frame"
    
    def execute(self, context):
        bpy.ops.screen.animation_cancel()
        context.scene.frame_current = context.scene.frame_start
        return {'FINISHED'}

class ANIM_OT_previous_preset(Operator):
    bl_idname = "anim.previous_preset"
    bl_label = "Previous Preset"
    bl_description = "Go to previous animation preset"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        items = props.preset_enum
        current_idx = 0
        
        # Find current index
        for i, (identifier, name, _, _, _) in enumerate(items):
            if identifier == props.preset_enum:
                current_idx = i
                break
        
        # Set to previous item
        if current_idx > 0:
            props.preset_enum = items[current_idx - 1][0]
        
        return {'FINISHED'}

class ANIM_OT_next_preset(Operator):
    bl_idname = "anim.next_preset"
    bl_label = "Next Preset"
    bl_description = "Go to next animation preset"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        items = props.preset_enum
        current_idx = 0
        
        # Find current index
        for i, (identifier, name, _, _, _) in enumerate(items):
            if identifier == props.preset_enum:
                current_idx = i
                break
        
        # Set to next item
        if current_idx < len(items) - 1:
            props.preset_enum = items[current_idx + 1][0]
        
        return {'FINISHED'}

class ANIM_OT_add_preset(Operator):
    bl_idname = "anim.add_preset"
    bl_label = "Add Animation"
    bl_description = "Apply the selected animation preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.scene.animation_preset_props.preset_enum != 'NONE'
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        preset = props.preset_enum
        
        if not context.selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
            
        for obj in context.selected_objects:
            if preset == "POPUP_ROTATION":
                apply_popup_rotation(obj)
                self.report({'INFO'}, f"Applied popup rotation animation to {obj.name}")
            else:
                # Handle other presets here
                preset_path = os.path.join(get_presets_path(), f"{preset.lower()}.py")
                if os.path.exists(preset_path):
                    try:
                        exec(compile(open(preset_path).read(), preset_path, 'exec'))
                        self.report({'INFO'}, f"Applied {preset} animation")
                    except Exception as e:
                        self.report({'ERROR'}, f"Error applying preset: {str(e)}")
                        return {'CANCELLED'}
                else:
                    self.report({'WARNING'}, f"Preset file not found: {preset.lower()}.py")
                    return {'CANCELLED'}
        
        return {'FINISHED'}

class ANIM_PT_main_panel(Panel):
    bl_label = "Animation Presets Pro"
    bl_idname = "ANIM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animation'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.animation_preset_props
        
        # Info Section
        box = layout.box()
        box.label(text="MelU Info")
        
        row = box.row(align=True)
        row.operator("wm.url_open", text="Discord", icon='URL').url = "https://discord.com/kllc666"
        row.operator("wm.url_open", text="Github", icon='URL').url = "https://github.com/Kllc7"
        
        box.operator("wm.url_open", text="Documentation", icon='HELP').url = "https://github.com/Kllc7/blender_animation_addon/blob/main/README.md"
        
        # VFX Preview Section
        box = layout.box()
        box.label(text="")
        
        # Preview with full-height navigation
        row = box.row(align=True)
        
        # Left navigation
        col = row.column(align=True)
        col.scale_y = 8.0  # Match preview height
        col.operator("anim.previous_preset", text="", icon='TRIA_LEFT')
        
        # Preview area
        col = row.column()
        col.template_icon_view(props, "preset_enum", show_labels=True, scale=8.0)
        
        # Right navigation
        col = row.column(align=True)
        col.scale_y = 8.0  # Match preview height
        col.operator("anim.next_preset", text="", icon='TRIA_RIGHT')
        
        # Add animation button
        row = box.row()
        row.scale_y = 1.5
        row.operator("anim.add_preset", text="Add Animation")
        
        # Tools Section
        box = layout.box()
        box.label(text="")
        
        # Timeline controls
        row = box.row(align=True)
        row.scale_y = 1.2
        
        # Left timeline controls
        subrow = row.row(align=True)
        subrow.operator("screen.frame_jump", text="", icon='REW').end = False
        subrow.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
        
        # Play controls
        subrow = row.row(align=True)
        subrow.operator("anim.play_animation", text="", icon='PLAY')
        subrow.operator("anim.reset_animation", text="", icon='LOOP_BACK')
        
        # Right timeline controls
        subrow = row.row(align=True)
        subrow.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
        subrow.operator("screen.frame_jump", text="", icon='FF').end = True
        
        # Speed Control
        row = box.row(align=True)
        row.prop(props, "animation_speed", text="Speed")

classes = (
    ANIM_OT_previous_preset,
    ANIM_OT_next_preset,
    AnimationPresetProperties,
    ANIM_OT_play_animation,
    ANIM_OT_reset_animation,
    ANIM_OT_add_preset,
    ANIM_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.animation_preset_props = PointerProperty(type=AnimationPresetProperties)

def unregister():
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.animation_preset_props

if __name__ == "__main__":
    register()