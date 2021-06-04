# Blender-Addons

blender-bake-prep-addon-v01 (alpha)

is mostly based on the method you can find in this youtube tutorial:
https://www.youtube.com/watch?v=9airvjDaVh4

adds a menu in the render (by luck for me directly under baking )
called pre-bake.
there you can select the object you want to bake 
select the uvmaps and select an existing texture 

automaticly connects the uvmap.target to the texture input 

also optionaly connect the material uvmap TO ALL  image textures found in the node tree (this might break stuff).

option to skip metallic materials as these don't bake well (i believe most game engine only support a value of 0 or 1 unlike blender)

automaticaly selects the image texture as active for all materials

can change the texture names and use add nodes to update target texture for baking different maps (diffure ,roughness normall etc) 
pressing the add nodes will only update the texturet target name if nodes already exist
