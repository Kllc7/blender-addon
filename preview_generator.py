import bpy
import os
import tempfile
from PIL import Image
import io

class AnimationPresetGIFPreview:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def create_preview(self, start_frame, end_frame, width=200, height=200):
        """
        Create a GIF preview of the animation between start_frame and end_frame
        Returns the binary data of the optimized GIF
        """
        original_frame = bpy.context.scene.frame_current
        frames = []
        
        # Store render settings
        original_resolution_x = bpy.context.scene.render.resolution_x
        original_resolution_y = bpy.context.scene.render.resolution_y
        original_percentage = bpy.context.scene.render.resolution_percentage
        
        try:
            # Set temporary render settings for preview
            bpy.context.scene.render.resolution_x = width
            bpy.context.scene.render.resolution_y = height
            bpy.context.scene.render.resolution_percentage = 100
            
            # Render frames
            for frame in range(start_frame, end_frame + 1):
                bpy.context.scene.frame_set(frame)
                
                # Render frame to temporary file
                temp_path = os.path.join(self.temp_dir, f"preview_frame_{frame}.png")
                bpy.context.scene.render.filepath = temp_path
                bpy.ops.render.render(write_still=True)
                
                # Open rendered frame with PIL
                img = Image.open(temp_path)
                frames.append(img.copy())
                
                # Clean up temporary file
                os.remove(temp_path)
                
            # Create optimized GIF
            output_buffer = io.BytesIO()
            
            # Save with optimization
            frames[0].save(
                output_buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=1000/24,  # 24 fps
                loop=0,
                optimize=True,
                quality=70,  # Lower quality for smaller file size
                disposal=2,  # Clear frame before rendering next
            )
            
            return output_buffer.getvalue()
            
        finally:
            # Restore original render settings
            bpy.context.scene.render.resolution_x = original_resolution_x
            bpy.context.scene.render.resolution_y = original_resolution_y
            bpy.context.scene.render.resolution_percentage = original_percentage
            bpy.context.scene.frame_set(original_frame)

    def save_preview(self, filepath, start_frame, end_frame, width=200, height=200):
        """
        Create and save a GIF preview to the specified filepath
        """
        gif_data = self.create_preview(start_frame, end_frame, width, height)
        with open(filepath, 'wb') as f:
            f.write(gif_data)

# Example usage in your addon:
class ANIMATION_OT_create_preset_preview(bpy.types.Operator):
    bl_idname = "animation.create_preset_preview"
    bl_label = "Create Preset Preview"
    
    def execute(self, context):
        preview_generator = AnimationPresetGIFPreview()
        
        # Get animation range
        scene = context.scene
        start = scene.frame_start
        end = scene.frame_end
        
        # Create preview
        preview_path = os.path.join(bpy.app.tempdir, "preset_preview.gif")
        preview_generator.save_preview(preview_path, start, end)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ANIMATION_OT_create_preset_preview)

def unregister():
    bpy.utils.unregister_class(ANIMATION_OT_create_preset_preview)

if __name__ == "__main__":
    register()