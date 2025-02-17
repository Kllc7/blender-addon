import bpy
from bpy.types import Operator
import os
import bpy.utils.previews

preview_collections = {}

def get_preset_path():
    return os.path.join(os.path.dirname(__file__), "presets")

def generate_previews():
    enum_items = []
    pcoll = preview_collections["main"]
    
    preview_dir = get_preset_path()
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)
        return enum_items
    
    image_paths = []
    for fn in os.listdir(preview_dir):
        if fn.lower().endswith(".gif"):
            image_paths.append(fn)
    
    for i, name in enumerate(image_paths):
        filepath = os.path.join(preview_dir, name)
        if filepath not in pcoll:
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
        else:
            thumb = pcoll[filepath]
        
        enum_items.append((
            name,
            name.split('.')[0].replace('_', ' ').title(),
            "",
            thumb.icon_id,
            i
        ))
    
    return enum_items

class ANIM_OT_play_animation(Operator):
    bl_idname = "anim.play_animation"
    bl_label = "Play/Pause Animation"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        props.is_playing = not props.is_playing
        return {'FINISHED'}

class ANIM_OT_next_frame(Operator):
    bl_idname = "anim.next_frame"
    bl_label = "Next Frame"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        if props.current_frame < props.total_frames:
            props.current_frame += 1
        return {'FINISHED'}

class ANIM_OT_previous_frame(Operator):
    bl_idname = "anim.previous_frame"
    bl_label = "Previous Frame"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        if props.current_frame > 0:
            props.current_frame -= 1
        return {'FINISHED'}

class ANIM_OT_skip_to_start(Operator):
    bl_idname = "anim.skip_to_start"
    bl_label = "Skip to Start"
    
    def execute(self, context):
        context.scene.animation_preset_props.current_frame = 0
        return {'FINISHED'}

class ANIM_OT_skip_to_end(Operator):
    bl_idname = "anim.skip_to_end"
    bl_label = "Skip to End"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        props.current_frame = props.total_frames
        return {'FINISHED'}

class ANIM_OT_previous_keyframe(Operator):
    bl_idname = "anim.previous_keyframe"
    bl_label = "Previous Keyframe"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        # For now, jump 10 frames back
        props.current_frame = max(0, props.current_frame - 10)
        return {'FINISHED'}

class ANIM_OT_next_keyframe(Operator):
    bl_idname = "anim.next_keyframe"
    bl_label = "Next Keyframe"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        # For now, jump 10 frames forward
        props.current_frame = min(props.total_frames, props.current_frame + 10)
        return {'FINISHED'}

class ANIM_OT_decrease_frame(Operator):
    bl_idname = "anim.decrease_frame"
    bl_label = "Decrease Frame"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        if props.current_frame > 0:
            props.current_frame -= 1
        return {'FINISHED'}

class ANIM_OT_increase_frame(Operator):
    bl_idname = "anim.increase_frame"
    bl_label = "Increase Frame"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        if props.current_frame < props.total_frames:
            props.current_frame += 1
        return {'FINISHED'}

class ANIM_OT_reset_animation(Operator):
    bl_idname = "anim.reset_animation"
    bl_label = "Reset Animation"
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        props.current_frame = 0
        props.is_playing = False
        return {'FINISHED'}

# Register all operators
classes = (
    ANIM_OT_play_animation,
    ANIM_OT_next_frame,
    ANIM_OT_previous_frame,
    ANIM_OT_skip_to_start,
    ANIM_OT_skip_to_end,
    ANIM_OT_previous_keyframe,
    ANIM_OT_next_keyframe,
    ANIM_OT_decrease_frame,
    ANIM_OT_increase_frame,
    ANIM_OT_reset_animation,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)